"""Parser de CVs em PDF.

Usa pdfplumber para extrair texto de todas as páginas.
Lança ParseError customizado para que o pipeline possa tratar sem parar a execução.
"""

from __future__ import annotations

from pathlib import Path

import pdfplumber


class PDFParseError(Exception):
    """Falha ao extrair texto de um PDF."""


def extrair_texto_pdf(caminho: str | Path) -> str:
    """Extrai o texto de um arquivo PDF.

    Args:
        caminho: Caminho para o arquivo .pdf.

    Returns:
        Texto concatenado de todas as páginas, separado por quebras de linha.

    Raises:
        PDFParseError: Se o arquivo não existir, estiver protegido, corrompido
                       ou não contiver camada de texto (PDF escaneado sem OCR).
    """
    caminho = Path(caminho)

    if not caminho.exists():
        raise PDFParseError(f"Arquivo não encontrado: {caminho}")

    try:
        with pdfplumber.open(caminho) as pdf:
            if not pdf.pages:
                raise PDFParseError(f"PDF sem páginas: {caminho.name}")

            partes: list[str] = []
            for i, pagina in enumerate(pdf.pages, start=1):
                texto = pagina.extract_text()
                if texto:
                    partes.append(texto)
                # Páginas sem texto são silenciosamente ignoradas — comuns em PDFs
                # com imagens. O texto total pode ainda ser utilizável.

    except PDFParseError:
        raise
    except Exception as exc:
        # pdfplumber lança várias exceções dependendo do tipo de problema
        raise PDFParseError(
            f"Não foi possível ler '{caminho.name}': {exc}"
        ) from exc

    texto_final = "\n\n".join(partes).strip()

    if not texto_final:
        raise PDFParseError(
            f"Nenhum texto extraído de '{caminho.name}'. "
            "O PDF pode estar escaneado (imagem sem OCR) ou vazio."
        )

    return texto_final
