"""Geração da planilha de triagem em Excel.

Recebe a lista de ResultadoCandidato produzida pela análise e escreve um
arquivo .xlsx ranqueado, pronto para a Karina revisar. Sem dependência de
Google Sheets — a saída é um arquivo local que abre direto no Excel.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from ..logger import get_logger
from ..models import Classificacao, ResultadoCandidato

log = get_logger(__name__)


# Ordem de exibição: melhores candidatos primeiro, erros por último.
# Dentro de cada grupo, ordena por pontuação decrescente.
_PRIORIDADE: dict[Classificacao, int] = {
    "aprovado": 0,
    "verificar": 1,
    "reprovado": 2,
    "erro_parsing": 3,
    "erro_api": 4,
}

# Rótulos legíveis e cor de fundo por classificação (RGB hex, sem #).
_ROTULO: dict[Classificacao, str] = {
    "aprovado": "Aprovado",
    "verificar": "Verificar",
    "reprovado": "Reprovado",
    "erro_parsing": "Erro de leitura",
    "erro_api": "Erro de análise",
}
_COR: dict[Classificacao, str] = {
    "aprovado": "C6EFCE",      # verde
    "verificar": "FFEB9C",     # amarelo
    "reprovado": "FFC7CE",     # vermelho
    "erro_parsing": "D9D9D9",  # cinza
    "erro_api": "D9D9D9",      # cinza
}

_COLUNAS = [
    ("Nome", 28),
    ("Contato", 32),
    ("Classificação", 16),
    ("Pontuação", 11),
    ("Pontos Positivos", 45),
    ("Pontos Negativos", 45),
    ("Justificativa", 55),
    ("Arquivo Fonte", 30),
    ("Data Triagem", 18),
]


def _ordenar(resultados: list[ResultadoCandidato]) -> list[ResultadoCandidato]:
    """Ordena por classificação (aprovado→erro) e pontuação decrescente."""
    return sorted(
        resultados,
        key=lambda r: (_PRIORIDADE.get(r.classificacao, 99), -r.pontuacao),
    )


def _slug(texto: str) -> str:
    """Normaliza o cargo para uso seguro em nome de arquivo."""
    sem_acento = (
        unicodedata.normalize("NFKD", texto)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    slug = re.sub(r"[^\w]+", "_", sem_acento).strip("_").lower()
    return slug or "vaga"


def _linha(resultado: ResultadoCandidato) -> list[str | int]:
    """Converte um ResultadoCandidato em uma linha da planilha."""
    return [
        resultado.nome or "—",
        resultado.contato or "—",
        _ROTULO.get(resultado.classificacao, resultado.classificacao),
        resultado.pontuacao,
        "\n".join(f"• {p}" for p in resultado.pontos_positivos),
        "\n".join(f"• {p}" for p in resultado.pontos_negativos),
        resultado.justificativa,
        resultado.arquivo_fonte,
        resultado.data_triagem.strftime("%d/%m/%Y %H:%M"),
    ]


def _estilizar_cabecalho(ws: Worksheet) -> None:
    """Aplica cabeçalho em negrito, fundo escuro e larguras de coluna."""
    fonte = Font(bold=True, color="FFFFFF")
    fundo = PatternFill("solid", fgColor="305496")
    for idx, (titulo, largura) in enumerate(_COLUNAS, start=1):
        celula = ws.cell(row=1, column=idx, value=titulo)
        celula.font = fonte
        celula.fill = fundo
        celula.alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions[get_column_letter(idx)].width = largura


def escrever_planilha(
    resultados: list[ResultadoCandidato],
    cargo: str,
    pasta_saida: Path | str = ".",
    timestamp: datetime | None = None,
) -> Path:
    """Escreve a planilha de triagem ranqueada e retorna o caminho do arquivo.

    Args:
        resultados: Candidatos analisados (em qualquer ordem).
        cargo: Título da vaga — usado no nome do arquivo.
        pasta_saida: Diretório onde gravar o .xlsx. Criado se não existir.
        timestamp: Momento da triagem (default: agora) — vai no nome do arquivo.

    Returns:
        Caminho do arquivo .xlsx gerado.
    """
    pasta = Path(pasta_saida)
    pasta.mkdir(parents=True, exist_ok=True)

    quando = timestamp or datetime.now()
    nome_arquivo = f"triagem_{_slug(cargo)}_{quando.strftime('%Y%m%d_%H%M%S')}.xlsx"
    caminho = pasta / nome_arquivo

    wb = Workbook()
    ws = wb.active
    ws.title = "Triagem"

    _estilizar_cabecalho(ws)

    alinhamento_topo = Alignment(vertical="top", wrap_text=True)
    for resultado in _ordenar(resultados):
        ws.append(_linha(resultado))
        linha_atual = ws.max_row
        cor = _COR.get(resultado.classificacao)
        for col in range(1, len(_COLUNAS) + 1):
            celula = ws.cell(row=linha_atual, column=col)
            celula.alignment = alinhamento_topo
            if cor:
                celula.fill = PatternFill("solid", fgColor=cor)

    # Congela o cabeçalho e liga o autofiltro para a Karina ordenar/filtrar.
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(_COLUNAS))}{ws.max_row}"

    wb.save(caminho)
    log.info(f"Planilha de triagem gerada: {caminho} ({len(resultados)} candidatos)")
    return caminho
