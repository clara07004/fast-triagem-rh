"""Análise de candidatos com Claude API.

Recebe critérios da vaga + texto do CV e retorna ResultadoCandidato
com classificação, pontuação e justificativa geradas pela IA.
"""

from __future__ import annotations

import json
from datetime import datetime

from anthropic import (
    Anthropic,
    APIConnectionError,
    InternalServerError,
    RateLimitError,
)
from pydantic import ValidationError
from tenacity import (
    after_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# Logger configurado em logger.py
from .logger import get_logger
from .models import ResultadoCandidato, VagaCriterios

log = get_logger(__name__)


class AnalyzerError(Exception):
    """Erro ao analisar candidato com IA."""


# Cliente único do processo — lazy para não exigir ANTHROPIC_API_KEY no import.
# Reusado entre candidatos (mantém conexões HTTP vivas em vez de recriar tudo).
_client: Anthropic | None = None


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic()
    return _client


# Schema da resposta da IA — o structured output da API garante JSON válido
# nesse formato, sem wrapper de markdown nem campos fora do contrato.
# (Limites numéricos de pontuacao ficam por conta do Pydantic em ResultadoCandidato.)
_SCHEMA_ANALISE = {
    "type": "object",
    "properties": {
        "classificacao": {"type": "string", "enum": ["aprovado", "reprovado", "verificar"]},
        "pontuacao": {"type": "integer"},
        "pontos_positivos": {"type": "array", "items": {"type": "string"}},
        "pontos_negativos": {"type": "array", "items": {"type": "string"}},
        "justificativa": {"type": "string"},
        "nome_extraido": {"type": ["string", "null"]},
        "email_extraido": {"type": ["string", "null"]},
        "telefone_extraido": {"type": ["string", "null"]},
    },
    "required": [
        "classificacao",
        "pontuacao",
        "pontos_positivos",
        "pontos_negativos",
        "justificativa",
        "nome_extraido",
        "email_extraido",
        "telefone_extraido",
    ],
    "additionalProperties": False,
}


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

Analise o currículo contra os critérios acima e preencha a resposta estruturada:
pontos_positivos e pontos_negativos com 2-3 itens cada; nome, email e telefone
extraídos do CV (ou null se não encontrados).

REGRAS DE CLASSIFICAÇÃO:
- "aprovado": atende TODOS os requisitos obrigatórios e tem boa aderência geral à vaga.
- "reprovado": não atende claramente pelo menos 1 requisito obrigatório.
- "verificar": atende os requisitos mas há dúvidas relevantes, informações insuficientes ou pontos que precisam ser confirmados em entrevista.

CALIBRAÇÃO DE PONTUAÇÃO (0-100):
- 85-100: candidato excelente — atende todos os requisitos e tem diferenciais relevantes
- 70-84: candidato bom — atende todos os requisitos com boa aderência geral
- 50-69: candidato razoável — atende a maioria dos requisitos mas com lacunas ou dúvidas em algum ponto
- 30-49: candidato fraco — não atende pelo menos 1 requisito obrigatório com clareza
- 0-29: candidato muito inadequado — não atende a maioria dos requisitos

A classificação e a pontuação devem ser consistentes:
  "aprovado" → pontuação ≥ 70
  "verificar" → pontuação entre 40 e 84
  "reprovado" → pontuação ≤ 49

- Se não encontrar nome/email/telefone no CV, coloque null.
- Justificativa deve ser concisa e objetiva, focada nos critérios da vaga.
"""


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    # Só erros transitórios da API. Erro de chave (AuthenticationError), request
    # inválido ou bug de código falham direto, sem 3 tentativas inúteis.
    retry=retry_if_exception_type((APIConnectionError, RateLimitError, InternalServerError)),
    after=after_log(log, 20),
)
def _chamar_claude(client: Anthropic, prompt: str) -> str:
    """Chama Claude API com retry automático.

    O structured output (output_config.format) garante que o texto retornado
    é JSON válido no formato de _SCHEMA_ANALISE.
    """
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        output_config={"format": {"type": "json_schema", "schema": _SCHEMA_ANALISE}},
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
        resposta_texto = _chamar_claude(_get_client(), prompt)

        # Structured output garante JSON puro; o except abaixo fica como rede
        # de segurança caso a API devolva algo fora do contrato.
        dados_ia = json.loads(resposta_texto)

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

        # Criar resultado — o construtor do Pydantic já valida tipos e limites.
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

        log.info(
            f"Candidato analisado: {nome or 'sem nome'} | "
            f"Classificacao: {resultado.classificacao} "
            f"({resultado.pontuacao}/100)"
        )

        return resultado

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
