"""Gera criterios_vaga_template.xlsx na raiz do projeto.

Template que a Karina preenche com os critérios de cada vaga, na identidade
visual da Fast (Manual de Marca 2025): vermelho #D21217, preto #191A1A,
tipografia Montserrat e logo embutido.

IMPORTANTE: as posições das células de dados são lidas pelo parser
(src/fast_triagem_rh/parsers/criterios.py) e NÃO podem mudar:
  B3=cargo  B4=localizacao  B5=tipo_contrato  B6=observacoes
  B8:B11=requisitos_obrigatorios   B13:B16=diferenciais
O design ocupa as linhas que o parser ignora (1, 2, 7, 12) e o logo flutua
sobre o cabeçalho, sem deslocar nenhuma célula.

Rodar uma vez:
    python scripts/gerar_template_criterios.py
"""

from pathlib import Path

from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

RAIZ = Path(__file__).parent.parent
OUTPUT = RAIZ / "criterios_vaga_template.xlsx"
LOGO = RAIZ / "assets" / "logo_fast.png"

# === Identidade Fast =======================================================
FONTE = "Montserrat"
RED = "D21217"        # vermelho principal
PRETO = "191A1A"      # preto da marca
AMARELO_INPUT = "FFF3C4"  # destaque "preencha aqui" (amarelo suave da marca)
CINZA_LABEL = "ECECEC"
CINZA_BORDA = "D9D9D9"
CINZA_TXT = "717578"
TEXTO = "191A1A"


def _fill(cor: str) -> PatternFill:
    return PatternFill("solid", fgColor=cor)


def _font(*, size=11, bold=False, color=TEXTO, italic=False) -> Font:
    return Font(name=FONTE, size=size, bold=bold, color=color, italic=italic)


def _borda(cor=CINZA_BORDA) -> Border:
    lado = Side(style="thin", color=cor)
    return Border(left=lado, right=lado, top=lado, bottom=lado)


def _left(indent=1) -> Alignment:
    return Alignment(horizontal="left", vertical="center", wrap_text=True, indent=indent)


def _inserir_logo(ws, ancora: str, altura_px: int = 50) -> bool:
    if not LOGO.is_file():
        return False
    try:
        img = XLImage(str(LOGO))
        if img.height:
            escala = altura_px / float(img.height)
            img.height = altura_px
            img.width = int(img.width * escala)
        ws.add_image(img, ancora)
        return True
    except Exception:
        return False


def _build_criterios(ws) -> None:
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 64

    # --- Linha 1: letterhead branco com logo + título à direita ---
    ws.row_dimensions[1].height = 58
    ws.merge_cells("A1:B1")
    _fill_intervalo(ws, 1, 1, 1, 2, "FFFFFF")
    titulo = ws.cell(1, 1, "CRITÉRIOS DA VAGA")
    titulo.font = Font(name=FONTE, size=18, bold=True, color=PRETO)
    titulo.alignment = Alignment(horizontal="right", vertical="center", indent=1)
    if not _inserir_logo(ws, "A1", altura_px=48):
        # fallback textual
        titulo.value = "FAST  ·  CRITÉRIOS DA VAGA"

    # --- Linha 2: faixa vermelha com instrução ---
    ws.merge_cells("A2:B2")
    instr = ws.cell(
        2, 1,
        "Preencha os campos destacados em amarelo. Em listas, um item por linha.",
    )
    instr.font = _font(size=10, bold=True, color="FFFFFF")
    instr.alignment = _left()
    _fill_intervalo(ws, 2, 1, 2, 2, RED)
    ws.row_dimensions[2].height = 24

    # --- Campos simples (linhas 3–6) — col A rótulo, col B input ---
    campos = [
        (3, "Cargo", "Ex: Assistente de Vendas"),
        (4, "Localização", "Ex: Rio de Janeiro - RJ  /  Remoto  /  Qualquer"),
        (5, "Tipo de contrato", "Ex: CLT  /  PJ  /  Estágio"),
        (6, "Observações (opcional)", "Contexto extra que ajude a IA a entender a vaga"),
    ]
    for linha, rotulo, exemplo in campos:
        _rotulo(ws, linha, rotulo)
        _input(ws, linha, exemplo)
        ws.row_dimensions[linha].height = 26

    # --- Seção: Requisitos obrigatórios (linha 7) + itens (8–11) ---
    _secao(ws, 7, "REQUISITOS OBRIGATÓRIOS", "candidato reprovado se não atender algum", RED)
    exemplos_req = [
        "Ex: Experiência mínima de 1 ano em vendas",
        "Ex: Ensino médio completo",
        "Ex: Disponibilidade para viagens",
        "(adicione mais requisitos se precisar)",
    ]
    for i, ex in enumerate(exemplos_req):
        linha = 8 + i
        _bullet(ws, linha)
        _input(ws, linha, ex)
        ws.row_dimensions[linha].height = 24

    # --- Seção: Diferenciais (linha 12) + itens (13–16) ---
    _secao(ws, 12, "DIFERENCIAIS", "pesam positivamente, não são eliminatórios", PRETO)
    exemplos_dif = [
        "Ex: Experiência com CRM",
        "Ex: Inglês intermediário",
        "Ex: Conhecimento em drywall / construção a seco",
        "(adicione mais diferenciais se precisar)",
    ]
    for i, ex in enumerate(exemplos_dif):
        linha = 13 + i
        _bullet(ws, linha)
        _input(ws, linha, ex)
        ws.row_dimensions[linha].height = 24

    # --- Rodapé (linha 17) ---
    ws.merge_cells("A17:B17")
    pe = ws.cell(17, 1, "Dúvidas? Fale com a Clara Barbosa.")
    pe.font = _font(size=9, italic=True, color=CINZA_TXT)
    pe.alignment = _left()
    _fill_intervalo(ws, 17, 1, 17, 2, "FFFFFF")
    ws.cell(17, 1).border = Border(top=Side(style="thin", color=CINZA_BORDA))
    ws.cell(17, 2).border = Border(top=Side(style="thin", color=CINZA_BORDA))
    ws.row_dimensions[17].height = 18

    ws.freeze_panes = "A3"


def _fill_intervalo(ws, r1, c1, r2, c2, cor):
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            ws.cell(r, c).fill = _fill(cor)


def _rotulo(ws, linha, texto):
    c = ws.cell(linha, 1, texto)
    c.font = _font(bold=True, color=PRETO)
    c.fill = _fill(CINZA_LABEL)
    c.alignment = _left()
    c.border = _borda()


def _input(ws, linha, exemplo):
    c = ws.cell(linha, 2, exemplo)
    c.font = _font(size=10, italic=True, color="9A8A55")
    c.fill = _fill(AMARELO_INPUT)
    c.alignment = _left()
    c.border = _borda()


def _bullet(ws, linha):
    c = ws.cell(linha, 1, "▸")
    c.font = _font(bold=True, color=RED)
    c.fill = _fill(CINZA_LABEL)
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.border = _borda()


def _secao(ws, linha, titulo, subtitulo, cor):
    ws.merge_cells(start_row=linha, start_column=1, end_row=linha, end_column=2)
    c = ws.cell(linha, 1)
    c.value = f"{titulo}   —   {subtitulo}"
    c.font = _font(size=11, bold=True, color="FFFFFF")
    c.alignment = _left()
    _fill_intervalo(ws, linha, 1, linha, 2, cor)
    ws.row_dimensions[linha].height = 24


def _build_instrucoes(ws) -> None:
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 4
    ws.column_dimensions["B"].width = 100

    # Letterhead + título
    ws.row_dimensions[1].height = 54
    _fill_intervalo(ws, 1, 1, 1, 2, "FFFFFF")
    if not _inserir_logo(ws, "A1", altura_px=48):
        cel = ws.cell(1, 1, "FAST")
        cel.font = _font(size=18, bold=True, color=RED)
        cel.alignment = _left()

    ws.merge_cells("A2:B2")
    t = ws.cell(2, 1, "Como usar este template")
    t.font = _font(size=16, bold=True, color="FFFFFF")
    t.alignment = _left()
    _fill_intervalo(ws, 2, 1, 2, 2, RED)
    ws.row_dimensions[2].height = 32

    blocos = [
        ("", "spacer"),
        ("PASSO 1 — Duplique este arquivo", "secao"),
        ("Renomeie para: criterios_<nome_da_vaga>.xlsx   (ex: criterios_assistente_vendas.xlsx)", "item"),
        ("", "spacer"),
        ("PASSO 2 — Preencha a aba 'Critérios'", "secao"),
        ("Cargo, localização e tipo de contrato: preencha na coluna amarela.", "item"),
        ("Requisitos obrigatórios: um item por linha. Quem não atender é reprovado.", "item"),
        ("Diferenciais: idem — um por linha. Não são eliminatórios.", "item"),
        ("Observações: contexto extra que ajude a IA a entender a vaga.", "item"),
        ("", "spacer"),
        ("PASSO 3 — Organize os CVs", "secao"),
        ("Crie uma pasta com o nome da vaga e coloque os CVs (PDF/Word) e a exportação do PandaPé dentro.", "item"),
        ("", "spacer"),
        ("PASSO 4 — Rode o script", "secao"),
        ("python -m fast_triagem_rh --vaga criterios_<vaga>.xlsx --cvs pasta_dos_cvs/", "codigo"),
        ("", "spacer"),
        ("PASSO 5 — Revise a planilha gerada", "secao"),
        ("O script gera triagem_<vaga>_<data>.xlsx com os candidatos ranqueados. Revise e encaminhe.", "item"),
        ("", "spacer"),
        ("A IA faz a triagem, mas a decisão final é sempre sua.", "callout"),
    ]

    r = 3
    for texto, tipo in blocos:
        if tipo == "spacer":
            ws.row_dimensions[r].height = 8
            r += 1
            continue
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        c = ws.cell(r, 1, texto)
        c.alignment = _left()
        if tipo == "secao":
            c.font = _font(size=12, bold=True, color=RED)
            ws.cell(r, 1).border = Border(bottom=Side(style="thin", color=CINZA_BORDA))
            ws.cell(r, 2).border = Border(bottom=Side(style="thin", color=CINZA_BORDA))
            ws.row_dimensions[r].height = 26
        elif tipo == "codigo":
            c.font = Font(name="Consolas", size=10, color="FFFFFF")
            _fill_intervalo(ws, r, 1, r, 2, PRETO)
            ws.row_dimensions[r].height = 22
        elif tipo == "callout":
            c.font = _font(size=11, bold=True, color="FFFFFF")
            _fill_intervalo(ws, r, 1, r, 2, PRETO)
            ws.row_dimensions[r].height = 30
        else:
            c.font = _font(size=11, color=TEXTO)
            ws.row_dimensions[r].height = 20
        r += 1


def main() -> None:
    wb = Workbook()
    ws_criterios = wb.active
    ws_criterios.title = "Critérios"
    _build_criterios(ws_criterios)

    ws_instrucoes = wb.create_sheet("Instruções")
    _build_instrucoes(ws_instrucoes)

    wb.save(OUTPUT)
    print(f"Template criado: {OUTPUT}")


if __name__ == "__main__":
    main()
