"""Testes do analyzer sem tocar na Claude API.

A construção do cliente Anthropic e a chamada HTTP são substituídas por stubs.
O foco é a lógica local: atalho de CV vazio, mapeamento do JSON da IA para
ResultadoCandidato e o tratamento de resposta fora do contrato (rede de
segurança — o structured output da API normalmente garante o formato).
"""

from __future__ import annotations

import json

import pytest

import fast_triagem_rh.analyzer as analyzer
from fast_triagem_rh.analyzer import analisar_candidato
from fast_triagem_rh.models import VagaCriterios


@pytest.fixture
def vaga():
    return VagaCriterios(cargo="Vendedor", requisitos_obrigatorios=["Vendas"])


@pytest.fixture
def sem_api(monkeypatch):
    """Neutraliza a obtenção do cliente Anthropic (não há rede nos testes)."""
    monkeypatch.setattr(analyzer, "_get_client", lambda: object())


def _stub_resposta(monkeypatch, texto: str):
    monkeypatch.setattr(analyzer, "_chamar_claude", lambda client, prompt: texto)


def test_cv_vazio_retorna_erro_parsing(vaga):
    # Não chama API: atalho antes de construir o cliente
    resultado = analisar_candidato(vaga, "   ", nome_arquivo="vazio.pdf")
    assert resultado.classificacao == "erro_parsing"
    assert resultado.arquivo_fonte == "vazio.pdf"


def test_json_valido_e_parseado(vaga, sem_api, monkeypatch):
    resposta = json.dumps({
        "classificacao": "aprovado",
        "pontuacao": 88,
        "pontos_positivos": ["experiência sólida"],
        "pontos_negativos": [],
        "justificativa": "Atende bem.",
        "nome_extraido": "Ana Souza",
        "email_extraido": "ana@x.com",
        "telefone_extraido": "21 99999-0000",
    })
    _stub_resposta(monkeypatch, resposta)

    r = analisar_candidato(vaga, "texto do cv", nome_arquivo="ana.pdf")
    assert r.classificacao == "aprovado"
    assert r.pontuacao == 88
    assert r.nome == "Ana Souza"
    assert "ana@x.com" in r.contato
    assert "21 99999-0000" in r.contato


def test_campos_de_contato_nulos_viram_none(vaga, sem_api, monkeypatch):
    payload = {
        "classificacao": "verificar", "pontuacao": 55,
        "pontos_positivos": [], "pontos_negativos": [],
        "justificativa": "Na margem.", "nome_extraido": None,
        "email_extraido": None, "telefone_extraido": None,
    }
    _stub_resposta(monkeypatch, json.dumps(payload))

    r = analisar_candidato(vaga, "texto", nome_arquivo="x.pdf")
    assert r.classificacao == "verificar"
    assert r.contato is None


def test_classificacao_fora_do_enum_vira_erro_api(vaga, sem_api, monkeypatch):
    payload = {
        "classificacao": "talvez", "pontuacao": 55,
        "pontos_positivos": [], "pontos_negativos": [],
        "justificativa": "?", "nome_extraido": None,
        "email_extraido": None, "telefone_extraido": None,
    }
    _stub_resposta(monkeypatch, json.dumps(payload))

    r = analisar_candidato(vaga, "texto", nome_arquivo="x.pdf")
    assert r.classificacao == "erro_api"


def test_resposta_nao_json_vira_erro_api(vaga, sem_api, monkeypatch):
    _stub_resposta(monkeypatch, "desculpe, não consegui analisar")
    r = analisar_candidato(vaga, "texto", nome_arquivo="x.pdf")
    assert r.classificacao == "erro_api"
