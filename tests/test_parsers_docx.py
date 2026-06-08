"""Testes do parser de Word (.docx) — happy path e edge cases do T13."""

from __future__ import annotations

import pytest

from fast_triagem_rh.parsers.docx import DOCXParseError, extrair_texto_docx


def test_extrai_paragrafos_e_tabela(criar_docx):
    caminho = criar_docx(
        paragrafos=["João Silva", "Engenheiro Civil"],
        tabela=[("Email", "joao@x.com")],
    )
    texto = extrair_texto_docx(caminho)

    assert "João Silva" in texto
    assert "Engenheiro Civil" in texto
    assert "joao@x.com" in texto


def test_arquivo_inexistente():
    with pytest.raises(DOCXParseError, match="não encontrado"):
        extrair_texto_docx("nao_existe.docx")


def test_doc_antigo_nao_suportado(tmp_path):
    # Edge case T13: .doc (Word 97-2003) deve falhar com mensagem clara, não travar
    caminho = tmp_path / "cv_antigo.doc"
    caminho.write_bytes(b"conteudo qualquer")
    with pytest.raises(DOCXParseError, match="Word 97-2003|não é suportado"):
        extrair_texto_docx(caminho)


def test_docx_corrompido(tmp_path):
    # Edge case T13: arquivo com extensão .docx mas conteúdo inválido
    caminho = tmp_path / "corrompido.docx"
    caminho.write_bytes(b"isto nao e um docx")
    with pytest.raises(DOCXParseError, match="corrompido|inválido"):
        extrair_texto_docx(caminho)


def test_docx_vazio_sem_texto(criar_docx):
    # Edge case T13: documento sem nenhum texto
    caminho = criar_docx(paragrafos=[])
    with pytest.raises(DOCXParseError, match="Nenhum texto|vazio"):
        extrair_texto_docx(caminho)


def test_nome_com_caractere_especial(criar_docx):
    # Edge case T13: nome de arquivo com acentos, espaços e símbolos
    caminho = criar_docx(
        paragrafos=["Currículo de teste"],
        nome="currículo (versão final) #1.docx",
    )
    texto = extrair_texto_docx(caminho)
    assert "Currículo de teste" in texto
