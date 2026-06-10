"""Testes do orquestrador (pipeline.py) com a análise por IA stubada.

Nenhum teste aqui chama a Claude API — analisar_candidato é substituído por um
stub determinístico. O foco é o dispatch por tipo de arquivo, a resiliência a
CVs problemáticos e o tratamento dos dados estruturados da PandaPé.
"""

from __future__ import annotations

from datetime import datetime

import pytest

import fast_triagem_rh.pipeline as pipeline
from fast_triagem_rh.models import ResultadoCandidato
from fast_triagem_rh.pipeline import PipelineError, processar_vaga


@pytest.fixture(autouse=True)
def stub_analyzer(monkeypatch):
    """Substitui a chamada à IA por um resultado fixo, sem rede."""

    def _fake(vaga, texto_cv, nome_arquivo="x"):
        return ResultadoCandidato(
            nome="IA Nome",
            contato="ia@x.com",
            classificacao="aprovado",
            pontuacao=80,
            pontos_positivos=["forte"],
            pontos_negativos=[],
            justificativa="stub",
            arquivo_fonte=nome_arquivo,
            data_triagem=datetime(2026, 6, 8, 10, 0, 0),
        )

    monkeypatch.setattr(pipeline, "analisar_candidato", _fake)


def test_criterios_invalidos_e_fatal(criar_criterios, tmp_path):
    # parse de critérios falhando deve abortar com PipelineError (erro fatal)
    criterios = criar_criterios(requisitos=[])  # sem requisitos → inválido
    cvs = tmp_path / "cvs"
    cvs.mkdir()
    (cvs / "x.docx").write_bytes(b"x")
    with pytest.raises(PipelineError, match="Critérios"):
        processar_vaga(criterios, cvs, pasta_saida=tmp_path)


def test_pasta_cvs_inexistente_e_fatal(criar_criterios, tmp_path):
    criterios = criar_criterios()
    with pytest.raises(PipelineError, match="não encontrada"):
        processar_vaga(criterios, tmp_path / "nao_existe", pasta_saida=tmp_path)


def test_pasta_vazia_e_fatal(criar_criterios, tmp_path):
    criterios = criar_criterios()
    cvs = tmp_path / "cvs"
    cvs.mkdir()
    with pytest.raises(PipelineError, match="Nenhum arquivo"):
        processar_vaga(criterios, cvs, pasta_saida=tmp_path)


def test_pandape_gera_um_resultado_por_candidato(criar_criterios, criar_pandape, tmp_path):
    criterios = criar_criterios()
    cvs = tmp_path / "cvs"
    cvs.mkdir()
    pandape = criar_pandape(
        candidatos=[
            {"Nome": "Ana", "Sobrenome": "Souza", "E-mail": "ana@x.com", "Telefone": "21 1"},
            {"Nome": "Bruno", "Sobrenome": "Lima", "E-mail": "bruno@x.com"},
        ],
        nome="export.xlsx",
    )
    pandape.rename(cvs / "export.xlsx")

    _caminho, resultados = processar_vaga(criterios, cvs, pasta_saida=tmp_path)

    assert len(resultados) == 2
    # nome e contato vêm do dado estruturado da PandaPé, não do stub da IA
    nomes = {r.nome for r in resultados}
    assert nomes == {"Ana Souza", "Bruno Lima"}
    ana = next(r for r in resultados if r.nome == "Ana Souza")
    assert ana.contato == "ana@x.com / 21 1"


def test_cv_ilegivel_nao_para_o_pipeline(criar_criterios, criar_docx, tmp_path):
    criterios = criar_criterios()
    cvs = tmp_path / "cvs"
    cvs.mkdir()
    # um CV bom + um corrompido + um tipo não suportado
    docx_ok = criar_docx(paragrafos=["Candidato válido"], nome="bom.docx")
    docx_ok.rename(cvs / "bom.docx")
    (cvs / "ruim.pdf").write_bytes(b"nao e pdf")
    (cvs / "ignorar.txt").write_text("ignorado")

    _caminho, resultados = processar_vaga(criterios, cvs, pasta_saida=tmp_path)

    # 2 resultados: o bom (aprovado) e o corrompido (erro_parsing). O .txt é ignorado.
    classifs = sorted(r.classificacao for r in resultados)
    assert classifs == ["aprovado", "erro_parsing"]


def test_resultado_anexa_arquivo_fonte(criar_criterios, criar_docx, tmp_path):
    criterios = criar_criterios()
    cvs = tmp_path / "cvs"
    cvs.mkdir()
    docx = criar_docx(paragrafos=["Texto"], nome="joao.docx")
    docx.rename(cvs / "joao.docx")

    _caminho, resultados = processar_vaga(criterios, cvs, pasta_saida=tmp_path)
    assert resultados[0].arquivo_fonte == "joao.docx"


def test_callback_de_progresso_acompanha_candidatos(
    criar_criterios, criar_pandape, tmp_path
):
    criterios = criar_criterios()
    cvs = tmp_path / "cvs"
    cvs.mkdir()
    pandape = criar_pandape(candidatos=[
        {"Nome": "Ana", "Sobrenome": "Souza", "E-mail": "ana@x.com"},
        {"Nome": "Bruno", "Sobrenome": "Lima", "E-mail": "b@x.com"},
        {"Nome": "Carla", "Sobrenome": "Reis", "E-mail": "c@x.com"},
    ])
    pandape.rename(cvs / "export.xlsx")

    eventos: list[tuple[int, int, str]] = []
    processar_vaga(
        criterios, cvs, pasta_saida=tmp_path,
        on_progresso=lambda f, t, r: eventos.append((f, t, r)),
    )

    # 1 arquivo expandiu pra 3 candidatos: total final = 3, feitos termina em 3
    assert eventos[-1][0] == 3
    assert eventos[-1][1] == 3
    # cada candidato gerou um avanco com o nome no rotulo
    rotulos = [e[2] for e in eventos if e[2]]
    assert rotulos == ["Ana Souza", "Bruno Lima", "Carla Reis"]


def test_processar_vaga_criterios_aceita_modelo_direto(criar_pandape, tmp_path):
    from fast_triagem_rh.models import VagaCriterios
    from fast_triagem_rh.pipeline import processar_vaga_criterios

    vaga = VagaCriterios(cargo="Vendedor", requisitos_obrigatorios=["Vendas"])
    cvs = tmp_path / "cvs"
    cvs.mkdir()
    criar_pandape().rename(cvs / "export.xlsx")

    caminho, resultados = processar_vaga_criterios(vaga, cvs, pasta_saida=tmp_path)
    assert caminho.exists()
    assert len(resultados) == 1
