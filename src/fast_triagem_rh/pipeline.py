"""Orquestrador da triagem.

Amarra o fluxo completo de uma vaga:
    critérios (Excel) → varre pasta de CVs → identifica tipo → parseia
    → analisa com IA → planilha Excel ranqueada.

Regra central: um CV problemático nunca derruba a execução. Ele entra na
planilha com status de erro (`erro_parsing` / `erro_api`) e o processamento
segue para o próximo. O único erro fatal é o dos critérios da vaga — sem eles
não há o que triar.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .analyzer import AnalyzerError, analisar_candidato
from .envelope import run_envelope
from .logger import get_logger
from .models import ResultadoCandidato, VagaCriterios
from .output.excel import escrever_planilha
from .parsers.criterios import parse_criterios
from .parsers.docx import DOCXParseError, extrair_texto_docx
from .parsers.pandape import CandidatoPandape, PandapeParseError, extrair_pandape
from .parsers.pdf import PDFParseError, extrair_texto_pdf

log = get_logger(__name__)

# Extensões reconhecidas como CV individual (1 arquivo = 1 candidato).
_EXT_PDF = {".pdf"}
_EXT_WORD = {".docx", ".doc"}
# Exportação PandaPé (1 arquivo = N candidatos).
_EXT_PANDAPE = {".xlsx", ".xlsm"}


class PipelineError(Exception):
    """Erro fatal que impede a triagem (ex.: critérios inválidos)."""


def _erro(
    classificacao: str,
    arquivo_fonte: str,
    motivo: str,
    *,
    nome: str | None = None,
    contato: str | None = None,
) -> ResultadoCandidato:
    """Cria um ResultadoCandidato de erro para entrar na planilha."""
    return ResultadoCandidato(
        nome=nome,
        contato=contato,
        classificacao=classificacao,  # type: ignore[arg-type]
        pontuacao=0,
        pontos_positivos=[],
        pontos_negativos=[motivo],
        justificativa=motivo,
        arquivo_fonte=arquivo_fonte,
        data_triagem=datetime.now(),
    )


def _candidato_pandape_para_texto(c: CandidatoPandape) -> str:
    """Monta um 'currículo' textual a partir dos campos estruturados da PandaPé."""
    return "\n".join(
        [
            f"Nome: {c.nome} {c.sobrenome}".strip(),
            f"Título profissional: {c.titulo_profissional or '-'}",
            f"Localização: {c.cidade or '-'} / {c.estado or '-'}",
            f"Idiomas: {c.idiomas or '-'}",
            f"Tags do CV: {c.tags_cv or '-'}",
            "",
            "Experiência profissional:",
            c.experiencia_profissional or "(não informada)",
        ]
    )


def _contato_pandape(c: CandidatoPandape) -> str | None:
    """Junta email e telefone/celular vindos da PandaPé (dado confiável)."""
    partes = [p for p in (c.email, c.telefone or c.celular) if p]
    return " / ".join(partes) if partes else None


def _analisar(vaga: VagaCriterios, texto: str, fonte: str) -> ResultadoCandidato:
    """Chama o analyzer protegendo contra falha inesperada da API."""
    try:
        return analisar_candidato(vaga, texto, nome_arquivo=fonte)
    except AnalyzerError as exc:
        log.error(f"Falha na análise de {fonte}: {exc}")
        return _erro("erro_api", fonte, f"Falha na análise com IA: {exc}")


def _processar_pandape(
    vaga: VagaCriterios, arquivo: Path, env
) -> list[ResultadoCandidato]:
    """Processa uma exportação PandaPé: N candidatos em um arquivo."""
    try:
        _meta, candidatos = extrair_pandape(arquivo)
    except PandapeParseError as exc:
        log.warning(f"[{env.run_id}] PandaPé ilegível ({arquivo.name}): {exc}")
        env.add_failed()
        return [_erro("erro_parsing", arquivo.name, f"Exportação PandaPé inválida: {exc}")]

    resultados: list[ResultadoCandidato] = []
    for c in candidatos:
        nome_completo = f"{c.nome} {c.sobrenome}".strip()
        fonte = f"{arquivo.name} — {nome_completo}"
        resultado = _analisar(vaga, _candidato_pandape_para_texto(c), fonte)
        # Nome e contato da PandaPé são mais confiáveis que a extração da IA.
        resultado.nome = nome_completo or resultado.nome
        resultado.contato = _contato_pandape(c) or resultado.contato
        resultados.append(resultado)
        env.add_processed()
        log.info(
            f"[{env.run_id}] {nome_completo}: {resultado.classificacao} "
            f"({resultado.pontuacao}/100)"
        )
    return resultados


def _processar_arquivo_unico(
    vaga: VagaCriterios, arquivo: Path, env
) -> ResultadoCandidato:
    """Processa um CV de arquivo único (PDF ou Word): 1 arquivo = 1 candidato."""
    ext = arquivo.suffix.lower()
    try:
        texto = (
            extrair_texto_pdf(arquivo)
            if ext in _EXT_PDF
            else extrair_texto_docx(arquivo)  # Word
        )
    except (PDFParseError, DOCXParseError) as exc:
        log.warning(f"[{env.run_id}] CV ilegível ({arquivo.name}): {exc}")
        env.add_failed()
        return _erro("erro_parsing", arquivo.name, f"Não foi possível ler o CV: {exc}")

    resultado = _analisar(vaga, texto, arquivo.name)
    env.add_processed()
    log.info(
        f"[{env.run_id}] {arquivo.name}: {resultado.classificacao} "
        f"({resultado.pontuacao}/100)"
    )
    return resultado


def processar_vaga(
    caminho_criterios: str | Path,
    pasta_cvs: str | Path,
    pasta_saida: str | Path = ".",
) -> tuple[Path, list[ResultadoCandidato]]:
    """Executa a triagem completa de uma vaga.

    Args:
        caminho_criterios: Template Excel com os critérios da vaga.
        pasta_cvs: Pasta com os CVs (PDF/Word) e/ou exportações PandaPé.
        pasta_saida: Onde gravar a planilha de triagem.

    Returns:
        Tupla (caminho da planilha gerada, lista de resultados).

    Raises:
        PipelineError: Se os critérios ou a pasta de CVs forem inválidos.
    """
    pasta_cvs = Path(pasta_cvs)

    # Critérios são pré-requisito — erro aqui é fatal.
    try:
        vaga = parse_criterios(caminho_criterios)
    except Exception as exc:
        raise PipelineError(f"Critérios da vaga inválidos: {exc}") from exc

    if not pasta_cvs.is_dir():
        raise PipelineError(f"Pasta de CVs não encontrada: {pasta_cvs}")

    arquivos = sorted(p for p in pasta_cvs.iterdir() if p.is_file())
    if not arquivos:
        raise PipelineError(f"Nenhum arquivo na pasta de CVs: {pasta_cvs}")

    resultados: list[ResultadoCandidato] = []

    with run_envelope("triagem-vaga") as env:
        env.set("cargo", vaga.cargo)
        env.set("arquivos", len(arquivos))
        log.info(f"[{env.run_id}] Triagem '{vaga.cargo}' — {len(arquivos)} arquivo(s)")

        for arquivo in arquivos:
            ext = arquivo.suffix.lower()
            if ext in _EXT_PANDAPE:
                resultados.extend(_processar_pandape(vaga, arquivo, env))
            elif ext in _EXT_PDF or ext in _EXT_WORD:
                resultados.append(_processar_arquivo_unico(vaga, arquivo, env))
            else:
                log.warning(f"[{env.run_id}] Ignorado (tipo não suportado): {arquivo.name}")

        env.set("candidatos", len(resultados))

    caminho = escrever_planilha(resultados, cargo=vaga.cargo, pasta_saida=pasta_saida)
    return caminho, resultados
