"""Testes do parser de PDF.

Cobrem os caminhos de erro (o que importa para a resiliência do T13). O
happy-path de extração e os casos de PDF escaneado (sem camada de texto) e
PDF protegido por senha exigem arquivos reais — ficam para o T12 com CVs
de verdade, pois não há writer de PDF nas dependências para fabricá-los aqui.
"""

from __future__ import annotations

import pytest

from fast_triagem_rh.parsers.pdf import PDFParseError, extrair_texto_pdf


def test_arquivo_inexistente():
    with pytest.raises(PDFParseError, match="não encontrado"):
        extrair_texto_pdf("nao_existe.pdf")


def test_pdf_corrompido(tmp_path):
    # Edge case T13: extensão .pdf mas bytes inválidos → erro tratado, sem traceback cru
    caminho = tmp_path / "corrompido.pdf"
    caminho.write_bytes(b"isto nao e um PDF de verdade")
    with pytest.raises(PDFParseError, match="Não foi possível ler"):
        extrair_texto_pdf(caminho)


def test_pdf_vazio(tmp_path):
    # Edge case T13: arquivo .pdf de 0 bytes
    caminho = tmp_path / "vazio.pdf"
    caminho.write_bytes(b"")
    with pytest.raises(PDFParseError):
        extrair_texto_pdf(caminho)
