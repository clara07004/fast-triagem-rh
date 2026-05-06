"""Gera criterios_vaga_template.xlsx na raiz do projeto.

Rodar uma vez:
    python scripts/gerar_template_criterios.py
"""

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

OUTPUT = Path(__file__).parent.parent / "criterios_vaga_template.xlsx"

AZUL_HEADER   = "1F3864"
AZUL_SECAO    = "2E75B6"
CINZA_LABEL   = "D6E4F0"
AMARELO_INPUT = "FFF2CC"
VERDE_LISTA   = "E2EFDA"


def _bold_white(size: int = 11) -> Font:
    return Font(name="Arial", bold=True, color="FFFFFF", size=size)

def _bold_dark(size: int = 11) -> Font:
    return Font(name="Arial", bold=True, color="1F3864", size=size)

def _fill(hex_color: str) -> PatternFill:
    return PatternFill("solid", start_color=hex_color, fgColor=hex_color)

def _border() -> Border:
    s = Side(style="thin", color="BFBFBF")
    return Border(left=s, right=s, top=s, bottom=s)

def _center() -> Alignment:
    return Alignment(horizontal="center", vertical="center", wrap_text=True)

def _left() -> Alignment:
    return Alignment(horizontal="left", vertical="center", wrap_text=True)


def _build_criterios(ws) -> None:
    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 62

    # Título
    ws.merge_cells("A1:B1")
    ws["A1"] = "TRIAGEM DE CANDIDATOS — CRITÉRIOS DA VAGA"
    ws["A1"].font = _bold_white(13)
    ws["A1"].fill = _fill(AZUL_HEADER)
    ws["A1"].alignment = _center()
    ws.row_dimensions[1].height = 32

    # Instrução geral
    ws.merge_cells("A2:B2")
    ws["A2"] = (
        "Preencha os campos em amarelo. "
        "Para listas (Requisitos e Diferenciais), adicione um item por linha."
    )
    ws["A2"].font = Font(name="Arial", size=9, italic=True, color="595959")
    ws["A2"].alignment = _left()
    ws.row_dimensions[2].height = 18

    def campo(row: int, label: str, exemplo: str, bg: str = AMARELO_INPUT) -> None:
        c1 = ws.cell(row, 1, label)
        c1.font = _bold_dark()
        c1.fill = _fill(CINZA_LABEL)
        c1.alignment = _left()
        c1.border = _border()

        c2 = ws.cell(row, 2, exemplo)
        c2.font = Font(name="Arial", size=10, color="808080", italic=True)
        c2.fill = _fill(bg)
        c2.alignment = _left()
        c2.border = _border()
        ws.row_dimensions[row].height = 22

    def secao(row: int, label: str) -> None:
        ws.merge_cells(f"A{row}:B{row}")
        ws.cell(row, 1, label).font = _bold_white()
        ws.cell(row, 1).fill = _fill(AZUL_SECAO)
        ws.cell(row, 1).alignment = _left()
        ws.row_dimensions[row].height = 24

    def item_lista(row: int, exemplo: str) -> None:
        c1 = ws.cell(row, 1, "  ↳ item")
        c1.font = Font(name="Arial", size=9, color="595959", italic=True)
        c1.fill = _fill(CINZA_LABEL)
        c1.alignment = Alignment(horizontal="right", vertical="center")
        c1.border = _border()

        c2 = ws.cell(row, 2, exemplo)
        c2.font = Font(name="Arial", size=10, color="808080", italic=True)
        c2.fill = _fill(VERDE_LISTA)
        c2.alignment = _left()
        c2.border = _border()
        ws.row_dimensions[row].height = 22

    # Campos simples (linhas 3–6)
    campo(3, "cargo",         "Ex: Assistente de Vendas")
    campo(4, "localizacao",   "Ex: São Paulo - SP  /  Remoto  /  Qualquer")
    campo(5, "tipo_contrato", "Ex: CLT  /  PJ  /  Estágio")
    campo(6, "observacoes",   "Informações adicionais para a triagem (opcional)")

    # Requisitos obrigatórios (linhas 7–11)
    secao(7, "📋  REQUISITOS OBRIGATÓRIOS  — candidato reprovado se não atender algum")
    item_lista(8,  "Ex: Experiência mínima de 1 ano em vendas")
    item_lista(9,  "Ex: Ensino médio completo")
    item_lista(10, "Ex: Disponibilidade para viagens")
    item_lista(11, "(adicione mais linhas se precisar de mais requisitos)")

    # Diferenciais (linhas 12–16)
    secao(12, "⭐  DIFERENCIAIS  — pesam positivamente, não são obrigatórios")
    item_lista(13, "Ex: Experiência com CRM")
    item_lista(14, "Ex: Inglês intermediário")
    item_lista(15, "Ex: Conhecimento em drywall / construção a seco")
    item_lista(16, "(adicione mais linhas se precisar de mais diferenciais)")

    # Rodapé
    ws.merge_cells("A17:B17")
    ws["A17"] = "ℹ️  Dúvidas? Fale com Clara Barbosa."
    ws["A17"].font = Font(name="Arial", size=9, italic=True, color="595959")
    ws["A17"].alignment = _left()
    ws.row_dimensions[17].height = 16

    ws.freeze_panes = "A3"


def _build_instrucoes(wi) -> None:
    wi.column_dimensions["A"].width = 82

    linhas = [
        ("COMO USAR ESTE TEMPLATE", True, AZUL_HEADER, "FFFFFF", 30),
        ("", False, None, "000000", 8),
        ("PASSO 1 — Duplique este arquivo", True, AZUL_SECAO, "FFFFFF", 24),
        ("  Renomeie para: criterios_<nome_da_vaga>.xlsx", False, None, "000000", 20),
        ("  Exemplo: criterios_assistente_vendas.xlsx", False, None, "595959", 20),
        ("", False, None, "000000", 8),
        ("PASSO 2 — Preencha a aba 'Critérios'", True, AZUL_SECAO, "FFFFFF", 24),
        ("  • Cargo, localização e tipo de contrato: preencha na coluna B.", False, None, "000000", 20),
        ("  • Requisitos obrigatórios: um item por linha (linhas verdes).", False, None, "000000", 20),
        ("  • Diferenciais: idem — um por linha. Não são eliminatórios.", False, None, "000000", 20),
        ("  • Observações: contexto extra que ajude a IA a entender a vaga.", False, None, "000000", 20),
        ("", False, None, "000000", 8),
        ("PASSO 3 — Organize os CVs", True, AZUL_SECAO, "FFFFFF", 24),
        ("  Crie uma pasta com o nome da vaga e coloque todos os CVs (PDF ou Word) dentro.", False, None, "000000", 20),
        ("  O arquivo de exportação do PandaPé também vai nessa pasta.", False, None, "000000", 20),
        ("", False, None, "000000", 8),
        ("PASSO 4 — Rode o script", True, AZUL_SECAO, "FFFFFF", 24),
        ("  Abra o terminal e execute:", False, None, "000000", 20),
        ("  python -m fast_triagem_rh --vaga criterios_<vaga>.xlsx --cvs pasta_dos_cvs/", False, None, "595959", 20),
        ("", False, None, "000000", 8),
        ("PASSO 5 — Revise a planilha gerada", True, AZUL_SECAO, "FFFFFF", 24),
        ("  O script gera triagem_<vaga>_<data>.xlsx com os candidatos ranqueados.", False, None, "000000", 20),
        ("  Revise, ajuste se necessário, e encaminhe aos gestores.", False, None, "000000", 20),
        ("", False, None, "000000", 8),
        ("⚠️  A IA faz a triagem, mas a decisão final é sempre sua.", True, AMARELO_INPUT, "1F3864", 22),
    ]

    for r, (texto, bold, bg, fg, height) in enumerate(linhas, start=1):
        cell = wi.cell(r, 1, texto)
        cell.font = Font(name="Arial", bold=bold, color=fg, size=10 if not bold else 11)
        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        if bg:
            cell.fill = PatternFill("solid", start_color=bg, fgColor=bg)
        wi.row_dimensions[r].height = height


def main() -> None:
    wb = Workbook()
    ws_criterios = wb.active
    ws_criterios.title = "Critérios"
    _build_criterios(ws_criterios)

    ws_instrucoes = wb.create_sheet("Instruções")
    _build_instrucoes(ws_instrucoes)

    wb.save(OUTPUT)
    print(f"✅  Template criado: {OUTPUT}")


if __name__ == "__main__":
    main()
