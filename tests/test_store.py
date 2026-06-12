"""Testes da persistência do app (store.py) — SQLite em diretório temporário."""

from __future__ import annotations

import pytest

from fast_triagem_rh import store
from fast_triagem_rh.models import VagaCriterios


@pytest.fixture
def db(tmp_path):
    return tmp_path / "triagem.db"


def _criterios(cargo="Vendedor Técnico"):
    return VagaCriterios(
        cargo=cargo,
        localizacao="Rio de Janeiro - RJ",
        tipo_contrato="CLT",
        requisitos_obrigatorios=["Experiência em vendas"],
        diferenciais=["Inglês"],
    )


def test_salvar_e_listar_vaga(db):
    vaga_id = store.salvar_vaga(_criterios(), db_path=db)
    vagas = store.listar_vagas(db_path=db)
    assert len(vagas) == 1
    assert vagas[0]["id"] == vaga_id
    assert vagas[0]["criterios"].cargo == "Vendedor Técnico"
    assert vagas[0]["criterios"].requisitos_obrigatorios == ["Experiência em vendas"]


def test_atualizar_vaga_existente(db):
    vaga_id = store.salvar_vaga(_criterios(), db_path=db)
    store.salvar_vaga(_criterios(cargo="Vendedor Sênior"), vaga_id=vaga_id, db_path=db)
    vagas = store.listar_vagas(db_path=db)
    assert len(vagas) == 1  # atualizou, não duplicou
    assert vagas[0]["criterios"].cargo == "Vendedor Sênior"


def test_atualizar_vaga_inexistente_falha(db):
    with pytest.raises(store.StoreError, match="não encontrada"):
        store.salvar_vaga(_criterios(), vaga_id=999, db_path=db)


def test_arquivar_esconde_da_listagem(db):
    vaga_id = store.salvar_vaga(_criterios(), db_path=db)
    store.arquivar_vaga(vaga_id, db_path=db)
    assert store.listar_vagas(db_path=db) == []
    assert len(store.listar_vagas(incluir_arquivadas=True, db_path=db)) == 1


def test_desarquivar_traz_de_volta(db):
    vaga_id = store.salvar_vaga(_criterios(), db_path=db)
    store.arquivar_vaga(vaga_id, db_path=db)
    store.desarquivar_vaga(vaga_id, db_path=db)
    vagas = store.listar_vagas(db_path=db)
    assert len(vagas) == 1
    assert vagas[0]["id"] == vaga_id
    assert vagas[0]["arquivada"] == 0


def test_excluir_vaga_some_em_definitivo(db):
    vaga_id = store.salvar_vaga(_criterios(), db_path=db)
    store.excluir_vaga(vaga_id, db_path=db)
    assert store.listar_vagas(incluir_arquivadas=True, db_path=db) == []


def test_excluir_vaga_preserva_historico(db):
    vaga_id = store.salvar_vaga(_criterios(), db_path=db)
    store.registrar_execucao(
        cargo="Vendedor Técnico",
        duracao_segundos=10.0,
        contagens={"aprovado": 2},
        planilha="triagens/triagem_x.xlsx",
        vaga_id=vaga_id,
        db_path=db,
    )
    store.excluir_vaga(vaga_id, db_path=db)
    execucoes = store.listar_execucoes(db_path=db)
    assert len(execucoes) == 1
    assert execucoes[0]["cargo"] == "Vendedor Técnico"


def test_excluir_vaga_inexistente_falha(db):
    with pytest.raises(store.StoreError, match="não encontrada"):
        store.excluir_vaga(999, db_path=db)


def test_atualizar_planilha_de_execucao(db):
    execucao_id = store.registrar_execucao(
        cargo="Vendedor Técnico",
        duracao_segundos=10.0,
        contagens={"aprovado": 1},
        planilha="triagens/triagem_x.xlsx",
        db_path=db,
    )
    store.atualizar_planilha(execucao_id, "vagas/vendedor/triagens/triagem_x.xlsx", db_path=db)
    e = store.listar_execucoes(db_path=db)[0]
    assert e["planilha"] == "vagas/vendedor/triagens/triagem_x.xlsx"


def test_atualizar_planilha_execucao_inexistente_falha(db):
    with pytest.raises(store.StoreError, match="não encontrada"):
        store.atualizar_planilha(999, "x.xlsx", db_path=db)


def test_excluir_execucao_some_do_historico(db):
    execucao_id = store.registrar_execucao(
        cargo="Vendedor Técnico",
        duracao_segundos=10.0,
        contagens={"aprovado": 1},
        planilha="triagens/triagem_x.xlsx",
        db_path=db,
    )
    store.excluir_execucao(execucao_id, db_path=db)
    assert store.listar_execucoes(db_path=db) == []


def test_excluir_execucao_inexistente_falha(db):
    with pytest.raises(store.StoreError, match="não encontrada"):
        store.excluir_execucao(999, db_path=db)


def test_registrar_e_listar_execucao(db):
    vaga_id = store.salvar_vaga(_criterios(), db_path=db)
    store.registrar_execucao(
        cargo="Vendedor Técnico",
        duracao_segundos=185.5,
        contagens={"aprovado": 10, "verificar": 5, "reprovado": 2, "erro_api": 1},
        planilha="triagens/triagem_x.xlsx",
        vaga_id=vaga_id,
        db_path=db,
    )
    execucoes = store.listar_execucoes(db_path=db)
    assert len(execucoes) == 1
    e = execucoes[0]
    assert e["total"] == 18
    assert e["aprovados"] == 10
    assert e["erros"] == 1
    assert e["planilha"].endswith("triagem_x.xlsx")
