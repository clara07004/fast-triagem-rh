"""Parser de CVs em Word (.docx).

Usa python-docx para extrair parágrafos e texto de tabelas.
Arquivos .doc antigos (Word 97-2003) não são suportados — sinaliza com erro claro.
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.opc.exceptions import PackageNotFoundError


class DOCXParseError(Exception):
    """Falha ao extrair texto de um arquivo Word."""


def extrair_texto_docx(caminho: str | Path) -> str:
    """Extrai o texto de um arquivo .docx.

    Coleta parágrafos do corpo principal e texto de tabelas (células).

    Args:
        caminho: Caminho para o arquivo .docx.

    Returns:
        Texto concatenado do documento.

    Raises:
        DOCXParseError: Se o arquivo não existir, for .doc antigo, estiver
                        corrompido ou não contiver texto.
    """
    caminho = Path(caminho)

    if not caminho.exists():
        raise DOCXParseError(f"Arquivo não encontrado: {caminho}")

    # .doc antigo não é suportado por python-docx
    if caminho.suffix.lower() == ".doc":
        raise DOCXParseError(
            f"'{caminho.name}' é um arquivo .doc (Word 97-2003), que não é suportado. "
            "Peça ao candidato para salvar em .docx e reprocesse manualmente."
        )

    try:
        doc = Document(str(caminho))
    except PackageNotFoundError as exc:
        raise DOCXParseError(
            f"Não foi possível abrir '{caminho.name}': arquivo corrompido ou formato inválido."
        ) from exc
    except Exception as exc:
        raise DOCXParseError(
            f"Erro ao ler '{caminho.name}': {exc}"
        ) from exc

    partes: list[str] = []

    # Parágrafos do corpo principal
    for paragrafo in doc.paragraphs:
        texto = paragrafo.text.strip()
        if texto:
            partes.append(texto)

    # Texto em tabelas (comum em CVs com layout em grade)
    for tabela in doc.tables:
        for linha in tabela.rows:
            for celula in linha.cells:
                texto = celula.text.strip()
                if texto and texto not in partes:
                    partes.append(texto)

    texto_final = "\n".join(partes).strip()

    if not texto_final:
        raise DOCXParseError(
            f"Nenhum texto extraído de '{caminho.name}'. O arquivo pode estar vazio."
        )

    return texto_final
