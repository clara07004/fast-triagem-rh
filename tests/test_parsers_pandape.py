"""Testes do parser de exportação PandaPé."""

from __future__ import annotations

import pytest

from fast_triagem_rh.parsers.pandape import PandapeParseError, extrair_pandape


def test_extrai_metadados_e_candidatos(criar_pandape):
    caminho = criar_pandape(
        cargo="Gerente de Obras",
        candidatos=[
            {"Nome": "Ana", "Sobrenome": "Souza", "E-mail": "ana@x.com",
             "Cidade": "RJ", "Título": "Gerente"},
            {"Nome": "Bruno", "Sobrenome": "Lima", "E-mail": "bruno@x.com"},
        ],
    )
    meta, candidatos = extrair_pandape(caminho)

    assert meta.cargo == "Gerente de Obras"
    assert len(candidatos) == 2
    assert candidatos[0].nome == "Ana"
    assert candidatos[0].email == "ana@x.com"
    assert candidatos[1].sobrenome == "Lima"


def test_arquivo_inexistente():
    with pytest.raises(PandapeParseError, match="não encontrado"):
        extrair_pandape("nao_existe.xlsx")


def test_cargo_vazio_falha(criar_pandape):
    caminho = criar_pandape(cargo="")
    with pytest.raises(PandapeParseError, match="Nome da vaga"):
        extrair_pandape(caminho)


def test_headers_obrigatorios_ausentes(criar_pandape):
    # Sem as colunas Nome/Sobrenome/E-mail não é uma exportação válida
    caminho = criar_pandape(headers=["Coluna A", "Coluna B"])
    with pytest.raises(PandapeParseError, match="Headers obrigatórios"):
        extrair_pandape(caminho)


def test_sem_candidatos_falha(criar_pandape):
    caminho = criar_pandape(candidatos=[])
    with pytest.raises(PandapeParseError, match="Nenhum candidato"):
        extrair_pandape(caminho)


def test_ignora_linhas_vazias_no_fim(criar_pandape):
    # Linhas sem nome ao final devem ser puladas, não viram candidatos fantasma
    caminho = criar_pandape(
        candidatos=[
            {"Nome": "Ana", "Sobrenome": "Souza", "E-mail": "ana@x.com"},
            {"Sobrenome": "SemNome", "E-mail": "x@x.com"},  # sem Nome → pulada
        ]
    )
    _meta, candidatos = extrair_pandape(caminho)
    assert len(candidatos) == 1
    assert candidatos[0].nome == "Ana"
