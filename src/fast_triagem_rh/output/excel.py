"""Geração da planilha de triagem em Excel.

Recebe a lista de ResultadoCandidato produzida pela análise e escreve um
arquivo .xlsx com três abas, na identidade visual da Fast (Manual de Marca
2025): vermelho #D21217, preto #191A1A, tipografia Montserrat.

  1. Resumo    — painel da vaga: KPIs em cartões e os melhores candidatos.
  2. Triagem   — tabela detalhada, ranqueada, com filtro e cabeçalho fixo.
  3. Como usar — guia de leitura das colunas, classificações e do papel dela.

Logo: se houver um PNG em assets/ (logo_fast.png, logo_fast_horizontal.png
ou logo.png), ele é embutido no cabeçalho. Sem o arquivo, cai num wordmark
"FAST" em texto. Sem dependência de Google Sheets — saída local .xlsx.
"""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from ..logger import get_logger
from ..models import Classificacao, ResultadoCandidato

log = get_logger(__name__)


# === Identidade Fast (Manual de Marca 2025) ================================
_FONTE = "Montserrat"          # tipografia de corpo da marca
_FONTE_TITULO = "Montserrat"   # (Big Noodle Titling não existe no Excel)

_RED = "D21217"        # vermelho principal
_RED_DARK = "A91918"   # vermelho escuro
_RED_DEEP = "7D1715"   # bordô
_PRETO = "191A1A"      # preto da marca
_AMARELO = "FFCE00"    # amarelo
_CINZA_TXT = "717578"  # texto secundário
_CINZA_BORDA = "EAEAEA"
_CINZA_ZEBRA = "F7F7F7"
_TEXTO = "191A1A"

# Cada classificação: cor "forte" (selo/destaque) e "suave" (fundo).
# Aprovado usa verde (semântica de "ok"); verificar puxa o amarelo da marca;
# reprovado usa o vermelho Fast; erros, neutro.
_COR_FORTE: dict[Classificacao, str] = {
    "aprovado": "15803D",
    "verificar": "946C00",
    "reprovado": _RED_DARK,
    "erro_parsing": _CINZA_TXT,
    "erro_api": _CINZA_TXT,
}
_COR_SUAVE: dict[Classificacao, str] = {
    "aprovado": "DCFCE7",
    "verificar": "FFF3C4",
    "reprovado": "FCE3E2",
    "erro_parsing": _CINZA_BORDA,
    "erro_api": _CINZA_BORDA,
}

_PRIORIDADE: dict[Classificacao, int] = {
    "aprovado": 0,
    "verificar": 1,
    "reprovado": 2,
    "erro_parsing": 3,
    "erro_api": 4,
}

_ROTULO: dict[Classificacao, str] = {
    "aprovado": "Aprovado",
    "verificar": "Verificar",
    "reprovado": "Reprovado",
    "erro_parsing": "Erro de leitura",
    "erro_api": "Erro de análise",
}

_COLUNAS = [
    ("Nome", 26),
    ("Contato", 30),
    ("Classificação", 16),
    ("Pontuação", 12),
    ("Pontos Positivos", 44),
    ("Pontos Negativos", 44),
    ("Justificativa", 52),
    ("Arquivo Fonte", 28),
    ("Data Triagem", 17),
]

# Nomes de arquivo de logo procurados em assets/ (na ordem).
_LOGOS_CANDIDATOS = [
    "logo_fast.png",
    "logo_fast_horizontal.png",
    "logo.png",
]


# === Helpers de dados ======================================================
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


def _linhas_de_texto(texto: str, chars_por_linha: int) -> int:
    """Estima quantas linhas visuais um texto ocupa numa coluna (com quebra)."""
    cpl = max(8, chars_por_linha)
    total = 0
    for segmento in str(texto).split("\n"):
        total += max(1, math.ceil(len(segmento) / cpl))
    return total


def _estimar_altura(resultado: ResultadoCandidato) -> float:
    """Altura da linha (em pontos) que comporta o conteúdo sem cortar.

    O Excel não auto-ajusta a altura em arquivos gerados, então calculamos:
    para cada coluna de texto, quantas linhas ela ocupa dada a largura, e
    usamos a coluna mais alta como referência.
    """
    pos = "\n".join(f"•  {p}" for p in resultado.pontos_positivos)
    neg = "\n".join(f"•  {p}" for p in resultado.pontos_negativos)
    # (texto, largura da coluna em caracteres) — descontamos margem/indent.
    colunas = [
        (resultado.nome or "—", 26),
        (resultado.contato or "—", 30),
        (pos, 44),
        (neg, 44),
        (resultado.justificativa or "", 52),
        (resultado.arquivo_fonte or "", 28),
    ]
    max_linhas = max(_linhas_de_texto(t, w - 3) for t, w in colunas)
    altura = max_linhas * 14.5 + 8  # ~14.5 pt por linha + respiro
    return min(max(altura, 22), 380)  # piso e teto sensatos


def _linha(resultado: ResultadoCandidato) -> list[str | int]:
    """Converte um ResultadoCandidato em uma linha da planilha."""
    return [
        resultado.nome or "—",
        resultado.contato or "—",
        _ROTULO.get(resultado.classificacao, resultado.classificacao),
        resultado.pontuacao,
        "\n".join(f"•  {p}" for p in resultado.pontos_positivos),
        "\n".join(f"•  {p}" for p in resultado.pontos_negativos),
        resultado.justificativa,
        resultado.arquivo_fonte,
        resultado.data_triagem.strftime("%d/%m/%Y %H:%M"),
    ]


# === Helpers de estilo =====================================================
def _fill(hex_cor: str) -> PatternFill:
    return PatternFill("solid", fgColor=hex_cor)


def _font(
    *, size: int = 11, bold: bool = False, color: str = _TEXTO, italic: bool = False
) -> Font:
    return Font(name=_FONTE, size=size, bold=bold, color=color, italic=italic)


def _borda_inferior(cor: str = _CINZA_BORDA) -> Border:
    return Border(bottom=Side(style="thin", color=cor))


def _borda_caixa(cor: str = _CINZA_BORDA) -> Border:
    lado = Side(style="thin", color=cor)
    return Border(left=lado, right=lado, top=lado, bottom=lado)


def _estilizar_intervalo(
    ws: Worksheet,
    r1: int,
    c1: int,
    r2: int,
    c2: int,
    *,
    fill: PatternFill | None = None,
    border: Border | None = None,
) -> None:
    """Aplica fill/borda a todas as células de um retângulo (inclui mesclados)."""
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            cel = ws.cell(r, c)
            if fill is not None:
                cel.fill = fill
            if border is not None:
                cel.border = border


def _localizar_logo() -> Path | None:
    """Procura um PNG de logo em assets/ (relativo ao diretório de trabalho)."""
    base = Path.cwd() / "assets"
    for nome in _LOGOS_CANDIDATOS:
        candidato = base / nome
        if candidato.is_file():
            return candidato
    return None


def _inserir_logo(ws: Worksheet, ancora: str, altura_px: int = 40) -> bool:
    """Embute o logo da Fast ancorado numa célula. Retorna True se inseriu."""
    caminho = _localizar_logo()
    if caminho is None:
        return False
    try:
        img = XLImage(str(caminho))
        if img.height:
            escala = altura_px / float(img.height)
            img.height = altura_px
            img.width = int(img.width * escala)
        ws.add_image(img, ancora)
        return True
    except Exception as exc:  # Pillow ausente, arquivo corrompido, etc.
        log.warning(f"Não foi possível embutir o logo ({caminho.name}): {exc}")
        return False


def _wordmark(ws: Worksheet, linha: int) -> None:
    """Fallback textual quando não há arquivo de logo: 'FAST Sistemas...'."""
    cel = ws.cell(linha, 1, "FAST")
    cel.font = Font(name=_FONTE_TITULO, size=20, bold=True, color=_RED)
    cel.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    sub = ws.cell(linha, 2, "Sistemas Construtivos")
    sub.font = Font(name=_FONTE, size=11, bold=True, color=_PRETO)
    sub.alignment = Alignment(horizontal="left", vertical="center")


# === Aba 1 — Resumo ========================================================
def _aba_resumo(
    ws: Worksheet,
    resultados: list[ResultadoCandidato],
    cargo: str,
    quando: datetime,
) -> None:
    """Painel executivo: logo, identificação da vaga, KPIs e top 5."""
    ws.sheet_view.showGridLines = False
    larguras = {"A": 26, "B": 22, "C": 16, "D": 22, "E": 16, "F": 16}
    for col, w in larguras.items():
        ws.column_dimensions[col].width = w

    contagem = Counter(r.classificacao for r in resultados)
    total = len(resultados)

    centro = Alignment(horizontal="center", vertical="center")
    esq = Alignment(horizontal="left", vertical="center")

    # --- Faixa de marca (linha 1): logo em fundo branco ---
    ws.row_dimensions[1].height = 54
    _estilizar_intervalo(ws, 1, 1, 1, 6, fill=_fill("FFFFFF"))
    if not _inserir_logo(ws, "A1", altura_px=60):
        _wordmark(ws, 1)

    # --- Banda de título (linha 2): vermelho Fast ---
    ws.merge_cells("A2:F2")
    t = ws.cell(2, 1, "Resumo da Triagem")
    t.font = Font(name=_FONTE_TITULO, size=20, bold=True, color="FFFFFF")
    t.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[2].height = 36
    _estilizar_intervalo(ws, 2, 1, 2, 6, fill=_fill(_RED))

    # --- Subtítulo (linha 3): preto da marca ---
    ws.merge_cells("A3:F3")
    sub = ws.cell(
        3, 1,
        f"{cargo}    ·    {total} candidato(s)    ·    {quando.strftime('%d/%m/%Y %H:%M')}",
    )
    sub.font = _font(size=11, color="D9D9D9")
    sub.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[3].height = 22
    _estilizar_intervalo(ws, 3, 1, 3, 6, fill=_fill(_PRETO))

    ws.row_dimensions[4].height = 12  # respiro

    # --- KPIs em cartões (linhas 5-6) ---
    cards = [
        ("APROVADOS", contagem.get("aprovado", 0), "aprovado"),
        ("VERIFICAR", contagem.get("verificar", 0), "verificar"),
        ("REPROVADOS", contagem.get("reprovado", 0), "reprovado"),
    ]
    col_ini = [1, 3, 5]  # A:B, C:D, E:F
    ws.row_dimensions[5].height = 46
    ws.row_dimensions[6].height = 20
    for (rotulo, valor, classe), c1 in zip(cards, col_ini, strict=True):
        c2 = c1 + 1
        suave = _fill(_COR_SUAVE[classe])
        ws.merge_cells(start_row=5, start_column=c1, end_row=5, end_column=c2)
        num = ws.cell(5, c1, valor)
        num.font = Font(name=_FONTE_TITULO, size=32, bold=True, color=_COR_FORTE[classe])
        num.alignment = centro
        ws.merge_cells(start_row=6, start_column=c1, end_row=6, end_column=c2)
        lab = ws.cell(6, c1, rotulo)
        lab.font = _font(size=10, bold=True, color=_COR_FORTE[classe])
        lab.alignment = centro
        _estilizar_intervalo(ws, 5, c1, 6, c2, fill=suave, border=_borda_caixa("FFFFFF"))

    linha = 7
    n_erros = contagem.get("erro_parsing", 0) + contagem.get("erro_api", 0)
    if n_erros:
        ws.merge_cells(start_row=linha, start_column=1, end_row=linha, end_column=6)
        e = ws.cell(
            linha, 1,
            f"⚠  {n_erros} candidato(s) não puderam ser processados — revise na aba Triagem.",
        )
        e.font = _font(size=10, italic=True, color=_CINZA_TXT)
        e.alignment = esq
        ws.row_dimensions[linha].height = 20
        linha += 1

    linha += 1  # respiro

    # --- Seção: Melhores candidatos ---
    ws.merge_cells(start_row=linha, start_column=1, end_row=linha, end_column=6)
    sec = ws.cell(linha, 1, "MELHORES CANDIDATOS")
    sec.font = _font(size=11, bold=True, color=_RED)
    sec.alignment = esq
    _estilizar_intervalo(
        ws, linha, 1, linha, 6,
        border=Border(bottom=Side(style="medium", color=_RED)),
    )
    ws.row_dimensions[linha].height = 22
    linha += 1

    cab = linha
    ws.merge_cells(start_row=cab, start_column=1, end_row=cab, end_column=3)
    ws.cell(cab, 1, "Candidato").font = _font(bold=True, color="FFFFFF")
    ws.cell(cab, 1).alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.cell(cab, 4, "Pontuação").font = _font(bold=True, color="FFFFFF")
    ws.cell(cab, 4).alignment = centro
    ws.merge_cells(start_row=cab, start_column=5, end_row=cab, end_column=6)
    ws.cell(cab, 5, "Contato").font = _font(bold=True, color="FFFFFF")
    ws.cell(cab, 5).alignment = Alignment(horizontal="left", vertical="center", indent=1)
    _estilizar_intervalo(ws, cab, 1, cab, 6, fill=_fill(_PRETO))
    ws.row_dimensions[cab].height = 24
    linha += 1

    elegiveis = [
        r for r in _ordenar(resultados)
        if r.classificacao in ("aprovado", "verificar")
    ][:5]

    if not elegiveis:
        ws.merge_cells(start_row=linha, start_column=1, end_row=linha, end_column=6)
        cel = ws.cell(linha, 1, "Nenhum candidato aprovado ou para verificar.")
        cel.font = _font(italic=True, color=_CINZA_TXT)
        cel.alignment = esq
        ws.row_dimensions[linha].height = 22
    else:
        for i, r in enumerate(elegiveis):
            zebra = _fill("FFFFFF") if i % 2 == 0 else _fill(_CINZA_ZEBRA)
            ws.merge_cells(start_row=linha, start_column=1, end_row=linha, end_column=3)
            nome = ws.cell(linha, 1, f"{i + 1}.  {r.nome or '—'}")
            nome.font = _font(color=_TEXTO)
            nome.alignment = Alignment(horizontal="left", vertical="center", indent=1)
            pont = ws.cell(linha, 4, r.pontuacao)
            pont.font = _font(bold=True, color=_COR_FORTE[r.classificacao])
            pont.alignment = centro
            ws.merge_cells(start_row=linha, start_column=5, end_row=linha, end_column=6)
            cont = ws.cell(linha, 5, r.contato or "—")
            cont.font = _font(size=10, color=_CINZA_TXT)
            cont.alignment = Alignment(horizontal="left", vertical="center", indent=1)
            _estilizar_intervalo(ws, linha, 1, linha, 6, fill=zebra, border=_borda_inferior())
            ws.row_dimensions[linha].height = 22
            linha += 1

    ws.sheet_view.zoomScale = 110


# === Aba 2 — Triagem =======================================================
def _aba_triagem(ws: Worksheet, resultados: list[ResultadoCandidato]) -> None:
    """Tabela ranqueada, uma linha por candidato, com filtro e cabeçalho fixo."""
    ws.sheet_view.showGridLines = False

    for idx, (titulo, largura) in enumerate(_COLUNAS, start=1):
        cel = ws.cell(1, idx, titulo)
        cel.font = _font(bold=True, color="FFFFFF")
        cel.fill = _fill(_PRETO)
        cel.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cel.border = Border(bottom=Side(style="medium", color=_RED))
        ws.column_dimensions[get_column_letter(idx)].width = largura
    ws.row_dimensions[1].height = 30

    n_col = len(_COLUNAS)
    topo = Alignment(vertical="top", wrap_text=True, indent=1)
    centro_topo = Alignment(horizontal="center", vertical="top")

    # Divisória do registro: linha inferior cinza separa um candidato do outro;
    # separadores verticais brancos delimitam cada coluna sobre o fundo colorido.
    borda_registro = Border(
        left=Side(style="thin", color="FFFFFF"),
        right=Side(style="thin", color="FFFFFF"),
        bottom=Side(style="thin", color="9CA3AF"),
    )

    for resultado in _ordenar(resultados):
        ws.append(_linha(resultado))
        r = ws.max_row
        suave = _fill(_COR_SUAVE.get(resultado.classificacao, "FFFFFF"))
        forte = _COR_FORTE.get(resultado.classificacao, _CINZA_TXT)

        for col in range(1, n_col + 1):
            cel = ws.cell(r, col)
            cel.alignment = topo
            cel.fill = suave
            cel.border = borda_registro
            cel.font = _font(size=10, color=_TEXTO)

        selo = ws.cell(r, 3)
        selo.fill = _fill(forte)
        selo.font = _font(size=10, bold=True, color="FFFFFF")
        selo.alignment = Alignment(horizontal="center", vertical="center")

        pont = ws.cell(r, 4)
        pont.font = Font(name=_FONTE_TITULO, size=14, bold=True, color=forte)
        pont.alignment = centro_topo
        pont.number_format = "0"

        ws.cell(r, 1).font = _font(size=10, bold=True, color=_TEXTO)
        ws.row_dimensions[r].height = _estimar_altura(resultado)

    ws.freeze_panes = "B2"
    ws.auto_filter.ref = f"A1:{get_column_letter(n_col)}{ws.max_row}"
    ws.sheet_view.zoomScale = 100


# === Aba 3 — Como usar =====================================================
def _aba_instrucoes(ws: Worksheet) -> None:
    """Guia de leitura: colunas, classificações e o papel da Karina."""
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 4
    ws.column_dimensions["B"].width = 104

    esq = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)

    # Faixa de marca + título
    ws.row_dimensions[1].height = 54
    _estilizar_intervalo(ws, 1, 1, 1, 2, fill=_fill("FFFFFF"))
    if not _inserir_logo(ws, "A1", altura_px=60):
        _wordmark(ws, 1)

    ws.merge_cells("A2:B2")
    t = ws.cell(2, 1, "Como ler esta planilha")
    t.font = Font(name=_FONTE_TITULO, size=18, bold=True, color="FFFFFF")
    t.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    _estilizar_intervalo(ws, 2, 1, 2, 2, fill=_fill(_RED))
    ws.row_dimensions[2].height = 34

    blocos: list[tuple[str, str]] = [
        ("", "spacer"),
        ("As três abas", "secao"),
        ("Resumo — visão geral da vaga: quantos candidatos em cada classificação e os melhores nomes.", "item"),
        ("Triagem — a lista completa, ranqueada do melhor para o pior. É onde você revisa.", "item"),
        ("Como usar — esta aba.", "item"),
        ("", "spacer"),
        ("O que significa cada classificação", "secao"),
        ("Aprovado — atende aos requisitos obrigatórios e tem boa aderência à vaga.", "item"),
        ("Verificar — atende ao essencial, mas há dúvidas que valem uma olhada sua.", "item"),
        ("Reprovado — não atende a algum requisito obrigatório.", "item"),
        ("Erro de leitura / análise — não foi possível processar o candidato; revise manualmente.", "item"),
        ("", "spacer"),
        ("O que cada coluna traz (aba Triagem)", "secao"),
        ("Nome / Contato — extraídos da exportação do PandaPé (dado confiável).", "item"),
        ("Pontuação — aderência geral à vaga, de 0 a 100.", "item"),
        ("Pontos Positivos / Negativos — destaques e ressalvas que a IA encontrou.", "item"),
        ("Justificativa — em 2-3 frases, por que o candidato recebeu essa classificação.", "item"),
        ("Arquivo Fonte — de onde veio o candidato (rastreabilidade).", "item"),
        ("", "spacer"),
        ("Como usar no dia a dia", "secao"),
        ("1.  Abra a aba Triagem (já vem ordenada: melhores no topo).", "item"),
        ("2.  Use o filtro do cabeçalho para ver só Aprovados, ou uma faixa de pontuação.", "item"),
        ("3.  Leia a Justificativa e os Pontos Negativos antes de decidir.", "item"),
        ("4.  Os Pontos Negativos costumam apontar o que confirmar na entrevista.", "item"),
        ("", "spacer"),
        ("A IA faz a triagem, mas a decisão final é sempre sua. Confirme os finalistas antes de encaminhar aos gestores.", "callout"),
    ]

    r = 3
    for texto, tipo in blocos:
        if tipo == "spacer":
            ws.row_dimensions[r].height = 8
            r += 1
            continue

        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        cel = ws.cell(r, 1, texto)
        cel.alignment = esq

        if tipo == "secao":
            cel.font = _font(size=12, bold=True, color=_RED)
            _estilizar_intervalo(
                ws, r, 1, r, 2,
                border=Border(bottom=Side(style="thin", color=_CINZA_BORDA)),
            )
            ws.row_dimensions[r].height = 26
        elif tipo == "callout":
            cel.font = _font(size=11, bold=True, color="FFFFFF")
            _estilizar_intervalo(ws, r, 1, r, 2, fill=_fill(_PRETO))
            ws.row_dimensions[r].height = 34
        else:
            cel.font = _font(size=11, color=_TEXTO)
            ws.row_dimensions[r].height = 20
        r += 1

    ws.sheet_view.zoomScale = 110


def escrever_planilha(
    resultados: list[ResultadoCandidato],
    cargo: str,
    pasta_saida: Path | str = ".",
    timestamp: datetime | None = None,
) -> Path:
    """Escreve a planilha de triagem (3 abas) e retorna o caminho do arquivo.

    Args:
        resultados: Candidatos analisados (em qualquer ordem).
        cargo: Título da vaga — usado no nome do arquivo e no resumo.
        pasta_saida: Diretório onde gravar o .xlsx. Criado se não existir.
        timestamp: Momento da triagem (default: agora) — vai no nome do arquivo
                   e no painel de resumo.

    Returns:
        Caminho do arquivo .xlsx gerado.
    """
    pasta = Path(pasta_saida)
    pasta.mkdir(parents=True, exist_ok=True)

    quando = timestamp or datetime.now()
    nome_arquivo = f"triagem_{_slug(cargo)}_{quando.strftime('%Y%m%d_%H%M%S')}.xlsx"
    caminho = pasta / nome_arquivo

    wb = Workbook()
    ws_resumo = wb.active
    ws_resumo.title = "Resumo"
    ws_triagem = wb.create_sheet("Triagem")
    ws_instrucoes = wb.create_sheet("Como usar")

    _aba_resumo(ws_resumo, resultados, cargo, quando)
    _aba_triagem(ws_triagem, resultados)
    _aba_instrucoes(ws_instrucoes)

    wb.active = 0  # abre no Resumo

    wb.save(caminho)
    log.info(f"Planilha de triagem gerada: {caminho} ({len(resultados)} candidatos)")
    return caminho
