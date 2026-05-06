"""Parser do template Excel de critérios de vaga.

Lê criterios_vaga.xlsx e retorna um VagaCriterios validado.

Estrutura esperada na aba 'Critérios':
  Linha 1: cabeçalho (ignorado)
  Linha 2: instrução geral (ignorada)
  Linhas 3–6: campos simples — coluna A = nome do campo, coluna B = valor
  Linha 7: cabeçalho de seção REQUISITOS (ignorado)
  Linhas 8–11: itens de requisitos_obrigatorios — coluna B = texto do item
  Linha 12: cabeçalho de seção DIFERENCIAIS (ignorado)
  Linhas 13–16: itens de diferenciais — coluna B = texto do item
"""

from __future__ import annotations

from pathlib import Path

import openpyxl
from pydantic import ValidationError

from ..models import VagaCriterios

# Mapeamento linha → campo simples (índices 1-based conforme openpyxl)
_LINHAS_CAMPOS_SIMPLES = {
    3: "cargo",
    4: "localizacao",
    5: "tipo_contrato",
    6: "observacoes",
}

_LINHAS_REQUISITOS   = range(8, 12)   # 8, 9, 10, 11
_LINHAS_DIFERENCIAIS = range(13, 17)  # 13, 14, 15, 16


class CriteriosParseError(Exception):
    """Erro de leitura ou validação do arquivo de critérios."""


def parse_criterios(caminho: str | Path) -> VagaCriterios:
    """Lê o template Excel e retorna VagaCriterios validado.

    Args:
        caminho: Caminho para o arquivo .xlsx preenchido por Karina.

    Returns:
        VagaCriterios com os dados da vaga.

    Raises:
        CriteriosParseError: Se o arquivo não puder ser lido ou os dados forem inválidos.
    """
    caminho = Path(caminho)

    if not caminho.exists():
        raise CriteriosParseError(f"Arquivo não encontrado: {caminho}")

    try:
        wb = openpyxl.load_workbook(caminho, data_only=True)
    except Exception as exc:
        raise CriteriosParseError(f"Não foi possível abrir o arquivo: {exc}") from exc

    if "Critérios" not in wb.sheetnames:
        raise CriteriosParseError(
            "Aba 'Critérios' não encontrada. "
            "Verifique se está usando o template correto (criterios_vaga_template.xlsx)."
        )

    ws = wb["Critérios"]

    dados: dict[str, str | list[str]] = {}

    # Campos simples
    for linha, campo in _LINHAS_CAMPOS_SIMPLES.items():
        valor = ws.cell(linha, 2).value
        dados[campo] = str(valor).strip() if valor else ""

    # Listas
    def _extrair_lista(linhas: range) -> list[str]:
        itens = []
        for linha in linhas:
            val = ws.cell(linha, 2).value
            if val and str(val).strip() and not str(val).strip().startswith("Ex:"):
                itens.append(str(val).strip())
        return itens

    dados["requisitos_obrigatorios"] = _extrair_lista(_LINHAS_REQUISITOS)
    dados["diferenciais"] = _extrair_lista(_LINHAS_DIFERENCIAIS)

    # Valida com Pydantic — falha rápida com mensagem legível
    try:
        return VagaCriterios(**dados)
    except ValidationError as exc:
        erros = "; ".join(
            f"{e['loc'][0]}: {e['msg']}" for e in exc.errors()
        )
        raise CriteriosParseError(
            f"Critérios inválidos no arquivo — corrija e tente novamente. Detalhes: {erros}"
        ) from exc
