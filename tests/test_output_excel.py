"""Testes da geração da planilha de triagem (output/excel.py)."""

from __future__ import annotations

from datetime import datetime

import pytest
from openpyxl import load_workbook

from fast_triagem_rh.models import ResultadoCandidato
from fast_triagem_rh.output.excel import escrever_planilha


def _resultado(nome, classificacao, pontuacao):
    return ResultadoCandidato(
        nome=nome,
        contato=f"{nome}@x.com",
        classificacao=classificacao,
        pontuacao=pontuacao,
        pontos_positivos=["ok"],
        pontos_negativos=[],
        justificativa="teste",
        arquivo_fonte=f"{nome}.pdf",
        data_triagem=datetime(2026, 6, 8, 10, 0, 0),
    )


@pytest.fixture
def planilha(tmp_path):
    resultados = [
        _resultado("reprov", "reprovado", 40),
        _resultado("aprov_baixo", "aprovado", 70),
        _resultado("erro", "erro_parsing", 0),
        _resultado("aprov_alto", "aprovado", 95),
        _resultado("verif", "verificar", 60),
    ]
    caminho = escrever_planilha(
        resultados, cargo="Vendedor Técnico", pasta_saida=tmp_path,
        timestamp=datetime(2026, 6, 8, 14, 30, 0),
    )
    return caminho


def test_arquivo_criado_com_nome_esperado(planilha):
    assert planilha.exists()
    assert planilha.name == "triagem_vendedor_tecnico_20260608_143000.xlsx"


def test_ordenacao_por_classificacao_e_pontuacao(planilha):
    ws = load_workbook(planilha).active
    nomes = [row[0].value for row in ws.iter_rows(min_row=2)]
    # aprovado(95) > aprovado(70) > verificar(60) > reprovado(40) > erro(0)
    assert nomes == ["aprov_alto", "aprov_baixo", "verif", "reprov", "erro"]


def test_cabecalho_e_estrutura(planilha):
    ws = load_workbook(planilha).active
    cabecalho = [c.value for c in ws[1]]
    assert cabecalho[0] == "Nome"
    assert "Pontuação" in cabecalho
    assert "Justificativa" in cabecalho
    assert ws.freeze_panes == "A2"
    assert ws.auto_filter.ref is not None


def test_cargo_com_acento_e_simbolo_vira_slug_seguro(tmp_path):
    caminho = escrever_planilha(
        [_resultado("x", "aprovado", 50)],
        cargo="Analista de R&S / Sênior (Pleno)",
        pasta_saida=tmp_path,
        timestamp=datetime(2026, 1, 1, 0, 0, 0),
    )
    # Sem acentos, espaços ou símbolos no nome do arquivo
    assert caminho.name == "triagem_analista_de_r_s_senior_pleno_20260101_000000.xlsx"


def test_lista_vazia_gera_planilha_com_cabecalho(tmp_path):
    caminho = escrever_planilha([], cargo="Vaga X", pasta_saida=tmp_path)
    ws = load_workbook(caminho).active
    assert ws.max_row == 1  # só o cabeçalho
