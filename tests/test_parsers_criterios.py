"""Testes do parser de critérios (Excel → VagaCriterios)."""

from __future__ import annotations

import pytest

from fast_triagem_rh.parsers.criterios import CriteriosParseError, parse_criterios


def test_le_criterios_validos(criar_criterios):
    caminho = criar_criterios(
        cargo="Analista Fiscal",
        requisitos=["SAP", "Ensino superior"],
        diferenciais=["Inglês"],
    )
    vaga = parse_criterios(caminho)

    assert vaga.cargo == "Analista Fiscal"
    assert vaga.requisitos_obrigatorios == ["SAP", "Ensino superior"]
    assert vaga.diferenciais == ["Inglês"]


def test_arquivo_inexistente():
    with pytest.raises(CriteriosParseError, match="não encontrado"):
        parse_criterios("nao_existe.xlsx")


def test_aba_criterios_ausente(criar_criterios):
    caminho = criar_criterios(aba="Plan1")
    with pytest.raises(CriteriosParseError, match="aba 'Critérios'|Critérios"):
        parse_criterios(caminho)


def test_sem_requisitos_obrigatorios_falha(criar_criterios):
    # requisitos_obrigatorios é campo obrigatório no modelo — lista vazia deve falhar
    caminho = criar_criterios(requisitos=[])
    with pytest.raises(CriteriosParseError):
        parse_criterios(caminho)


def test_ignora_placeholders_de_exemplo(criar_criterios):
    # Linhas que começam com "Ex:" são placeholders do template e devem ser ignoradas
    caminho = criar_criterios(requisitos=["Ex: digite aqui", "Requisito real"])
    vaga = parse_criterios(caminho)
    assert vaga.requisitos_obrigatorios == ["Requisito real"]
