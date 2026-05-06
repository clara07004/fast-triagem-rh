"""Análise de candidatos com Claude API.

Recebe critérios da vaga + texto do CV e retorna ResultadoCandidato
com classificação, pontuação e justificativa geradas pela IA.
"""

from __future__ import annotations

import json
from datetime import datetime

from anthropic import Anthropic
from pydantic import ValidationError
from tenacity import (
    after_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .models import Classificacao, ResultadoCandidato, VagaCriterios

# Logger configurado em logger.py
from .logger import get_logger

log = get_logger(__name__)


class AnalyzerError(Exception):
    """Erro ao analisar candidato com IA."""


def _montar_prompt(vaga: VagaCriterios, texto_cv: str) -> str:
    """Monta prompt para Claude analisar o CV contra critérios."""

    requisitos_str = "\n".join(f"- {r}" for r in vaga.requisitos_obrigatorios)
    diferenciais_str = (
        "\n".join(f"- {d}" for d in vaga.diferenciais) if vaga.diferenciais else "(nenhum)"
    )

    return f"""Você é um assistente especializado em triagem de candidatos.

VAGA: {vaga.cargo}
LOCALIZAÇÃO: {vaga.localizacao}
TIPO DE CONTRATO: {vaga.tipo_contrato}

REQUISITOS OBRIGATÓRIOS (candidato reprovado se não atender):
{requisitos_str}

DIFERENCIAIS (pesam positivamente):
{diferenciais_str}

{f"OBSERVAÇÕES: {vaga.observacoes}" if vaga.observacoes else ""}

---

CURRÍCULO DO CANDIDATO:

{texto_cv}

---

Analise o currículo contra os critérios acima. Retorne APENAS um JSON (sem markdown, sem explicação adicional) com esta estrutura:

{{
  "classificacao": "aprovado" | "reprovado" | "verificar",
  "pontuacao": <número 0-100>,
  "pontos_positivos": [<lista de 2-3 pontos fortes do candidato>],
  "pontos_negativos": [<lista de 2-3 pontos fracos ou dúvidas>],
  "justificativa": "<2-3 frases explicando a classificação>",
  "nome_extraido": "<nome do candidato se encontrado, ou null>",
  "email_extraido": "<email se encontrado, ou null>",
  "telefone_extraido": "<telefone se encontrado, ou null>"
}}

REGRAS:
- classificacao: "aprovado" se atende TODOS os requisitos + boa aderência geral.
                "reprovado" se não atende a algum requisito obrigatório.
                "verificar" se está na margem (atende requisitos mas com dúvidas, ou precisa clareza).
- pontuacao: 0-100. 100 = candidato perfeito. 0 = não atende nada.
- Se não encontrar nome/email/telefone no CV, coloque null.
- Justificativa deve ser concisa e objetiva.
"""


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((Exception,)),
    after=after_log(log, 20),
)
def _chamar_claude(client: Anthropic, prompt: str) -> str:
    """Chama Claude API com retry automático."""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def analisar_candidato(
    vaga: VagaCriterios,
    texto_cv: str,
    nome_arquivo: str = "cv_desconhecido",
) -> ResultadoCandidato:
    """Analisa um candidato contra critérios usando Claude API.

    Args:
        vaga: Critérios da vaga (VagaCriterios).
        texto_cv: Texto extraído do currículo.
        nome_arquivo: Nome do arquivo de origem (para rastreabilidade).

    Returns:
        ResultadoCandidato com análise e classificação.

    Raises:
        AnalyzerError: Se a API falhar após retries ou resposta inválida.
    """
    try:
        # Validar inputs
        if not texto_cv or not texto_cv.strip():
            return ResultadoCandidato(
                nome=None,
                contato=None,
                classificacao="erro_parsing",
                pontuacao=0,
                pontos_positivos=[],
                pontos_negativos=["CV vazio ou sem texto extraível"],
                justificativa="Não foi possível extrair texto do currículo.",
                arquivo_fonte=nome_arquivo,
                data_triagem=datetime.now(),
            )

        # Montar e enviar prompt
        prompt = _montar_prompt(vaga, texto_cv)

        client = Anthropic()
        resposta_texto = _chamar_claude(client, prompt)

        # Parsear JSON da resposta
        # A resposta pode vir com markdown (```json ... ```), remover
        resposta_json = resposta_texto.strip()
        if resposta_json.startswith("```"):
            resposta_json = resposta_json.split("```")[1]
            if resposta_json.startswith("json"):
                resposta_json = resposta_json[4:]
            resposta_json = resposta_json.strip()

        dados_ia = json.loads(resposta_json)

        # Mapear nome e contato
        nome = dados_ia.get("nome_extraido")
        email = dados_ia.get("email_extraido")
        telefone = dados_ia.get("telefone_extraido")

        contato = None
        if email or telefone:
            partes = []
            if email:
                partes.append(email)
            if telefone:
                partes.append(telefone)
            contato = " / ".join(partes)

        # Criar resultado
        resultado = ResultadoCandidato(
            nome=nome,
            contato=contato,
            classificacao=dados_ia.get("classificacao", "verificar"),
            pontuacao=int(dados_ia.get("pontuacao", 0)),
            pontos_positivos=dados_ia.get("pontos_positivos", []),
            pontos_negativos=dados_ia.get("pontos_negativos", []),
            justificativa=dados_ia.get("justificativa", ""),
            arquivo_fonte=nome_arquivo,
            data_triagem=datetime.now(),
        )

        # Validar com Pydantic (garante tipos corretos)
        resultado_validado = ResultadoCandidato(**resultado.model_dump())

        log.info(
            f"Candidato analisado: {nome or 'sem nome'} | "
            f"Classificacao: {resultado_validado.classificacao} "
            f"({resultado_validado.pontuacao}/100)"
        )

        return resultado_validado

    except json.JSONDecodeError as exc:
        log.error(f"Resposta da IA não é JSON válido: {exc}")
        return ResultadoCandidato(
            nome=None,
            contato=None,
            classificacao="erro_api",
            pontuacao=0,
            pontos_positivos=[],
            pontos_negativos=["IA retornou resposta inválida (JSON malformado)"],
            justificativa="Erro ao processar resposta da IA.",
            arquivo_fonte=nome_arquivo,
            data_triagem=datetime.now(),
        )

    except ValidationError as exc:
        log.error(f"Erro ao validar resposta da IA: {exc}")
        return ResultadoCandidato(
            nome=None,
            contato=None,
            classificacao="erro_api",
            pontuacao=0,
            pontos_positivos=[],
            pontos_negativos=[f"Resposta da IA não atende schema esperado: {exc}"],
            justificativa="Erro ao processar resposta da IA.",
            arquivo_fonte=nome_arquivo,
            data_triagem=datetime.now(),
        )

    except Exception as exc:
        log.exception(f"Erro inesperado ao analisar candidato: {exc}")
        raise AnalyzerError(f"Falha na análise: {exc}") from exc
