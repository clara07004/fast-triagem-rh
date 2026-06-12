"""Fast Triagem — app web local para o time de R&S.

Interface da automação de triagem de candidatos, pensada para a Karina:
  - Rodar triagem: arrastar a exportação do PandaPé, acompanhar o progresso
    e ver o resultado num painel visual (KPIs, gráficos, ranking).
  - Vagas e critérios: cadastrar/editar vagas reusáveis (sem template Excel).
  - Histórico: dashboard das triagens passadas + re-download das planilhas.

Rodar:  atalho "Fast Triagem" da área de trabalho (scripts/criar_atalho.ps1
        cria o atalho; scripts/iniciar_triagem.vbs é o lançador) ou, no
        terminal, streamlit run app.py
"""

from __future__ import annotations

import hmac
import html
import os
import re
import shutil
import sys
import tempfile
import time
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path

# Projeto usa src-layout; garante o import sem precisar de pip install -e.
sys.path.insert(0, str(Path(__file__).parent / "src"))

import altair as alt
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from pydantic import ValidationError

from fast_triagem_rh import store
from fast_triagem_rh.models import VagaCriterios
from fast_triagem_rh.parsers.pandape import PandapeParseError, extrair_pandape
from fast_triagem_rh.pipeline import PipelineError, processar_vaga_criterios

load_dotenv()

# === Identidade Fast =======================================================
VERMELHO = "#D21217"
PRETO = "#191A1A"
CINZA_TXT = "#717578"
LOGO = Path("assets/logo_fast.png")
LOGO_ICONE = Path("assets/logo_diamante.png")  # só o losango — favicon/janela
PASTA_VAGAS = Path("vagas")
LIMITE_AVISO_VOLUME = 200  # acima disso, exige confirmação explícita


def _slug_vaga(cargo: str) -> str:
    """Gera nome de pasta seguro a partir do cargo da vaga."""
    nfkd = unicodedata.normalize("NFKD", cargo)
    ascii_str = nfkd.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_str.lower()).strip("-")
    return slug[:60] or "vaga"


def _pasta_vaga(cargo: str) -> Path:
    """Retorna (e garante) a pasta raiz da vaga: vagas/<slug>/"""
    pasta = PASTA_VAGAS / _slug_vaga(cargo)
    (pasta / "cvs").mkdir(parents=True, exist_ok=True)
    (pasta / "triagens").mkdir(parents=True, exist_ok=True)
    return pasta


# Cores por classificação (forte = texto/selo, suave = fundo, icone = Material Symbol).
CORES = {
    "aprovado": {
        "forte": "#15803D",
        "suave": "#DCFCE7",
        "rotulo": "Aprovados",
        "icone": "check_circle",
    },
    "verificar": {
        "forte": "#946C00",
        "suave": "#FFF3C4",
        "rotulo": "Verificar",
        "icone": "visibility",
    },
    "reprovado": {
        "forte": "#B91C1C",
        "suave": "#FCE3E2",
        "rotulo": "Reprovados",
        "icone": "cancel",
    },
    "erros": {
        "forte": "#4B5563",
        "suave": "#F3F4F6",
        "rotulo": "Erros",
        "icone": "error",
    },
}
ROTULOS = {
    "aprovado": "Aprovado",
    "verificar": "Verificar",
    "reprovado": "Reprovado",
    "erro_parsing": "Erro de leitura",
    "erro_api": "Erro de análise",
}
# Classificação do candidato -> chave da paleta CORES.
CHAVE_COR = {
    "aprovado": "aprovado",
    "verificar": "verificar",
    "reprovado": "reprovado",
    "erro_parsing": "erros",
    "erro_api": "erros",
}

st.set_page_config(
    page_title="Fast Triagem",
    page_icon=str(LOGO_ICONE) if LOGO_ICONE.exists() else "🔻",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap');

    /* Fonte da marca em tudo, MENOS nos ícones Material — eles são spans de
       ligadura marcados com translate="no"; trocar a fonte deles faz o nome
       do ícone (ex. "timer") aparecer como texto. */
    html, body, p, h1, h2, h3, h4, h5, h6, label, button, input, textarea,
    span:not([translate="no"]):not([data-testid="stIconMaterial"]):not(.material-symbols-rounded) {{
        font-family: 'Montserrat', 'Segoe UI', sans-serif;
    }}

    /* Área principal — menos espaço morto no topo, respiro embaixo */
    .stApp .block-container {{ padding-top: 2.2rem; padding-bottom: 4rem; }}
    [data-testid="stHeader"] {{ background: transparent; }}

    /* Hero de seção — preto institucional com acento vermelho */
    .fast-banner {{
        background: linear-gradient(135deg, #1C1D1E 0%, #121313 70%, #1C0708 100%);
        border-left: 6px solid {VERMELHO};
        color: #FFF; border-radius: 14px;
        padding: 26px 30px; margin-bottom: 18px;
        box-shadow: 0 10px 28px rgba(15, 16, 16, .28);
    }}
    .fast-banner .eyebrow {{
        font-size: 11px; font-weight: 800; letter-spacing: 2.5px;
        text-transform: uppercase; color: #E8474B; margin-bottom: 4px;
    }}
    .fast-banner h1 {{
        font-size: 28px; margin: 0; color: #FFF;
        font-weight: 800; letter-spacing: .3px;
    }}
    .fast-banner p {{
        margin: 6px 0 0 0; color: #ABAEB1; font-size: 13.5px;
        line-height: 1.5; max-width: 62ch;
    }}

    /* Chip de passo (1, 2, 3 do fluxo de triagem) */
    .passo {{ display: flex; align-items: center; gap: 10px; margin: 20px 0 4px 0; }}
    .passo .n {{
        background: {VERMELHO}; color: #FFF; width: 26px; height: 26px;
        border-radius: 50%; flex: none; display: inline-flex;
        align-items: center; justify-content: center;
        font-size: 13px; font-weight: 800;
    }}
    .passo .t {{ font-size: 15px; font-weight: 700; color: {PRETO}; }}

    /* Título de bloco dentro da página */
    .bloco-titulo {{
        font-size: 14px; font-weight: 700; color: {PRETO};
        letter-spacing: .2px; margin: 4px 0 6px 0;
    }}

    /* Cartões de KPI — card branco com chip de ícone colorido (estilo Materio) */
    .kpi {{
        display: flex; align-items: center; gap: 14px; text-align: left;
        background: #FFF; border: 1px solid #EEEEF1; border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 3px 10px rgba(46, 48, 56, .08);
        transition: transform .15s ease, box-shadow .15s ease;
    }}
    .kpi:hover {{ transform: translateY(-3px); box-shadow: 0 6px 16px rgba(46, 48, 56, .14); }}
    .kpi .ic {{
        width: 44px; height: 44px; border-radius: 12px; flex: none;
        display: inline-flex; align-items: center; justify-content: center;
        font-family: 'Material Symbols Rounded'; font-size: 24px; line-height: 1;
    }}
    .kpi .num {{
        font-size: 30px; font-weight: 800; line-height: 1.05;
        font-variant-numeric: tabular-nums; color: {PRETO};
    }}
    .kpi .label {{
        font-size: 11px; font-weight: 700; letter-spacing: 1px; color: #8A8D91;
    }}

    /* Pódio */
    .podio {{
        border: 1px solid #EEEEF1; border-left: 5px solid {VERMELHO};
        border-radius: 10px; padding: 12px 16px; margin-bottom: 8px;
        background: #FFF;
        box-shadow: 0 2px 8px rgba(46, 48, 56, .06);
        transition: transform .15s ease, box-shadow .15s ease;
    }}
    .podio:hover {{ transform: translateX(3px); box-shadow: 0 4px 14px rgba(0, 0, 0, .10); }}
    .podio .pos {{
        font-size: 13px; font-weight: 800; color: {VERMELHO};
        margin-right: 10px; font-variant-numeric: tabular-nums;
    }}
    .podio .nome {{ font-weight: 700; color: {PRETO}; }}
    .podio .meta {{ font-size: 12px; color: {CINZA_TXT}; }}
    .podio .nota {{
        float: right; font-size: 24px; font-weight: 800;
        font-variant-numeric: tabular-nums;
    }}

    /* Estado vazio — orienta o próximo passo em vez de só avisar */
    .vazio {{
        text-align: center; padding: 44px 24px; margin: 8px 0;
        border: 1.5px dashed #D9DBE0; border-radius: 16px;
        background: #FFF;
    }}
    .vazio .ic {{
        font-family: 'Material Symbols Rounded'; font-size: 46px;
        color: #C6C8CA; line-height: 1;
    }}
    .vazio .ti {{ font-size: 16px; font-weight: 700; color: {PRETO}; margin: 12px 0 4px 0; }}
    .vazio .tx {{
        font-size: 13.5px; color: {CINZA_TXT}; line-height: 1.55;
        max-width: 48ch; margin: 0 auto;
    }}

    /* Sidebar — preto institucional, marca em destaque */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #1C1D1E 0%, #121313 100%);
        border-right: none;
    }}
    /* Logo num card branco (o logotipo tem texto preto) */
    [data-testid="stSidebar"] [data-testid="stImage"] {{
        background: #FFF; border-radius: 12px; padding: 14px 18px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, .35);
    }}
    [data-testid="stSidebar"] h3 {{
        color: #FFF; font-weight: 700; letter-spacing: .3px;
    }}
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
        color: #8E9194;
    }}
    [data-testid="stSidebar"] hr {{ border-color: rgba(255, 255, 255, .12); }}

    /* Navegação da sidebar: radio vira menu — item ativo em vermelho sólido */
    [data-testid="stSidebar"] [role="radiogroup"] {{ gap: 4px; }}
    [data-testid="stSidebar"] [role="radiogroup"] > label {{
        border-radius: 10px; padding: 10px 14px; width: 100%; margin: 0;
        transition: background .15s ease;
    }}
    [data-testid="stSidebar"] [role="radiogroup"] > label p,
    [data-testid="stSidebar"] [role="radiogroup"] > label
        span[data-testid="stIconMaterial"] {{
        color: #C6C9CB; font-weight: 600;
    }}
    [data-testid="stSidebar"] [role="radiogroup"] > label:hover {{
        background: rgba(255, 255, 255, .07);
    }}
    [data-testid="stSidebar"] [role="radiogroup"] > label:hover p {{ color: #FFF; }}
    [data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked) {{
        background: {VERMELHO};
        box-shadow: 0 4px 14px rgba(210, 18, 23, .45);
    }}
    [data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked) p,
    [data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked)
        span[data-testid="stIconMaterial"] {{
        color: #FFF; font-weight: 700;
    }}
    /* Esconde a bolinha do radio — o destaque do item já marca a seleção */
    [data-testid="stSidebar"] [role="radiogroup"] > label > div:first-child {{
        display: none;
    }}

    /* Botões — vermelho sólido, sem gradiente */
    .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {{
        border-radius: 8px; font-weight: 700;
    }}
    .stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"] {{
        background: {VERMELHO}; border: 0; box-shadow: none;
        transition: background .15s ease;
    }}
    .stButton > button[kind="primary"]:hover,
    .stDownloadButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button[kind="primary"]:hover {{
        background: #B30F13;
    }}

    /* Selo de classificação (pill) */
    .selo {{
        display: inline-block; padding: 4px 14px; border-radius: 20px;
        font-size: 12px; font-weight: 700; letter-spacing: .3px;
    }}
    /* Foco visível por teclado (acessibilidade) */
    .stButton > button:focus-visible, .stDownloadButton > button:focus-visible,
    .stFormSubmitButton > button:focus-visible {{
        outline: 3px solid rgba(210, 18, 23, .40); outline-offset: 2px;
    }}

    /* Superfícies brancas flutuando sobre o canvas cinza (estilo Materio) */
    [data-testid="stForm"],
    [data-testid="stExpander"] details,
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: #FFF; border: 1px solid #EEEEF1; border-radius: 14px;
        box-shadow: 0 2px 8px rgba(46, 48, 56, .06);
    }}

    /* Métricas (histórico) */
    [data-testid="stMetric"] {{
        background: #FFF; border: 1px solid #EEEEF1;
        border-radius: 12px; padding: 14px 16px;
        box-shadow: 0 2px 8px rgba(46, 48, 56, .06);
    }}
    [data-testid="stMetricValue"] {{ font-variant-numeric: tabular-nums; }}

    /* Abas do painel de resultado */
    .stTabs [data-baseweb="tab-list"] {{ gap: 6px; }}
    .stTabs [data-baseweb="tab"] {{ font-weight: 600; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# === Componentes visuais ===================================================
def _esc(valor) -> str:
    """Escapa dado externo (CV de candidato, cadastro) antes de virar HTML.

    Obrigatório em tudo que entra num st.markdown(unsafe_allow_html=True):
    nome/contato vêm do CV do candidato — fonte não confiável.
    """
    return html.escape(str(valor))


def _banner(titulo: str, subtitulo: str = "") -> None:
    sub = f"<p>{_esc(subtitulo)}</p>" if subtitulo else ""
    st.markdown(
        f"<div class='fast-banner'>"
        f"<div class='eyebrow'>Fast · Recrutamento &amp; Seleção</div>"
        f"<h1>{_esc(titulo)}</h1>{sub}</div>",
        unsafe_allow_html=True,
    )


def _passo(numero: int, texto: str) -> None:
    """Chip numerado que marca cada passo do fluxo de triagem."""
    st.markdown(
        f"<div class='passo'><span class='n'>{numero}</span><span class='t'>{texto}</span></div>",
        unsafe_allow_html=True,
    )


def _titulo_bloco(texto: str) -> None:
    st.markdown(f"<div class='bloco-titulo'>{texto}</div>", unsafe_allow_html=True)


def _estado_vazio(icone: str, titulo: str, texto: str) -> None:
    """Estado vazio com orientação: o que está faltando e onde resolver."""
    st.markdown(
        f"<div class='vazio'><div class='ic'>{icone}</div>"
        f"<div class='ti'>{titulo}</div><div class='tx'>{texto}</div></div>",
        unsafe_allow_html=True,
    )


def _kpi_cards(contagens: dict[str, int]) -> None:
    """Cartões de KPI coloridos — mesmo desenho do Resumo da planilha."""
    erros = contagens.get("erro_parsing", 0) + contagens.get("erro_api", 0)
    valores = {
        "aprovado": contagens.get("aprovado", 0),
        "verificar": contagens.get("verificar", 0),
        "reprovado": contagens.get("reprovado", 0),
    }
    if erros:
        valores["erros"] = erros
    colunas = st.columns(len(valores))
    for col, (chave, valor) in zip(colunas, valores.items(), strict=True):
        cor = CORES[chave]
        col.markdown(
            f"<div class='kpi'>"
            f"<div class='ic' style='background:{cor['suave']}; "
            f"color:{cor['forte']};'>{cor['icone']}</div>"
            f"<div><div class='num'>{valor}</div>"
            f"<div class='label'>{cor['rotulo'].upper()}</div></div>"
            f"</div>",
            unsafe_allow_html=True,
        )


def _grafico_distribuicao(resultados: list[dict]) -> alt.Chart:
    """Rosca com a distribuição das classificações."""
    contagem = Counter(r["classificacao"] for r in resultados)
    mapa = {
        "aprovado": ("Aprovados", CORES["aprovado"]["forte"]),
        "verificar": ("Verificar", CORES["verificar"]["forte"]),
        "reprovado": ("Reprovados", CORES["reprovado"]["forte"]),
        "erro_parsing": ("Erros", CORES["erros"]["forte"]),
        "erro_api": ("Erros", CORES["erros"]["forte"]),
    }
    linhas: dict[str, dict] = {}
    for classe, qtd in contagem.items():
        rotulo, cor = mapa.get(classe, ("Outros", CINZA_TXT))
        item = linhas.setdefault(rotulo, {"Classificação": rotulo, "Candidatos": 0, "cor": cor})
        item["Candidatos"] += qtd
    df = pd.DataFrame(list(linhas.values()))
    return (
        alt.Chart(df)
        .mark_arc(innerRadius=58, cornerRadius=4)
        .encode(
            theta=alt.Theta("Candidatos:Q"),
            color=alt.Color(
                "Classificação:N",
                scale=alt.Scale(domain=df["Classificação"].tolist(), range=df["cor"].tolist()),
                legend=alt.Legend(orient="bottom", title=None),
            ),
            tooltip=["Classificação", "Candidatos"],
        )
        .properties(height=240)
    )


def _grafico_pontuacoes(resultados: list[dict]) -> alt.Chart:
    """Histograma das pontuações — mostra onde a régua da vaga está cortando."""
    df = pd.DataFrame({"Pontuação": [r["pontuacao"] for r in resultados]})
    return (
        alt.Chart(df)
        .mark_bar(color=VERMELHO, cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X(
                "Pontuação:Q", bin=alt.Bin(extent=[0, 100], step=10), title="Pontuação (0–100)"
            ),
            y=alt.Y("count():Q", title="Candidatos"),
            tooltip=["count()"],
        )
        .properties(height=240)
    )


def _podio(resultados: list[dict], topo: int = 5) -> None:
    """Top N candidatos elegíveis, em cartões."""
    elegiveis = sorted(
        (r for r in resultados if r["classificacao"] in ("aprovado", "verificar")),
        key=lambda r: -r["pontuacao"],
    )[:topo]
    if not elegiveis:
        _estado_vazio(
            "person_off",
            "Nenhum candidato elegível",
            "Esta triagem não teve aprovados nem perfis para verificar. "
            "Vale revisar se os requisitos obrigatórios da vaga não estão rígidos demais.",
        )
        return
    for i, r in enumerate(elegiveis, start=1):
        cor = CORES["aprovado" if r["classificacao"] == "aprovado" else "verificar"]["forte"]
        st.markdown(
            f"<div class='podio'>"
            f"<span class='nota' style='color:{cor};'>{r['pontuacao']}</span>"
            f"<div class='nome'><span class='pos'>{i:02d}</span>{_esc(r['nome'] or '—')}</div>"
            f"<div class='meta'>{_esc(r['contato'] or 'sem contato')}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )


def _tabela_resultados(resultados: list[dict]) -> None:
    resultados = sorted(resultados, key=lambda r: -r["pontuacao"])

    col_filtro, col_busca = st.columns([3, 2])
    with col_filtro:
        filtro = st.segmented_control(
            "Filtrar classificação",
            ["Todos", "Aprovados", "Verificar", "Reprovados", "Erros"],
            default="Todos",
            label_visibility="collapsed",
        )
    with col_busca:
        busca = st.text_input(
            "Buscar candidato",
            placeholder="Buscar por nome…",
            label_visibility="collapsed",
            icon=":material/search:",
        )

    mapa_filtro = {
        "Aprovados": ("aprovado",),
        "Verificar": ("verificar",),
        "Reprovados": ("reprovado",),
        "Erros": ("erro_parsing", "erro_api"),
    }
    if filtro in mapa_filtro:
        resultados = [r for r in resultados if r["classificacao"] in mapa_filtro[filtro]]
    if busca.strip():
        termo = busca.strip().lower()
        resultados = [r for r in resultados if termo in (r["nome"] or "").lower()]

    if not resultados:
        _estado_vazio(
            "search_off",
            "Nenhum candidato com esse filtro",
            "Tente outra classificação ou limpe a busca por nome.",
        )
        return

    df = pd.DataFrame(
        {
            "Nome": [r["nome"] or "—" for r in resultados],
            "Classificação": [
                ROTULOS.get(r["classificacao"], r["classificacao"]) for r in resultados
            ],
            "Pontuação": [r["pontuacao"] for r in resultados],
            "Contato": [r["contato"] or "—" for r in resultados],
            "Justificativa": [r["justificativa"] for r in resultados],
        }
    )
    st.dataframe(
        df,
        width="stretch",
        height=420,
        column_config={
            "Pontuação": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d"),
            "Justificativa": st.column_config.TextColumn(width="large"),
        },
    )


def _detalhe_candidato(resultados: list[dict]) -> None:
    """Análise completa de um candidato: pontos fortes, atenção e justificativa."""
    ordenados = sorted(resultados, key=lambda r: -r["pontuacao"])
    rotulos = [
        f"{i}º · {r['nome'] or r.get('arquivo_fonte') or 'Sem nome'} — {r['pontuacao']} pts"
        for i, r in enumerate(ordenados, start=1)
    ]
    escolha = st.selectbox("Escolha o candidato", rotulos, label_visibility="collapsed")
    r = ordenados[rotulos.index(escolha)]

    with st.container(border=True):
        col_nome, col_selo = st.columns([3, 1])
        with col_nome:
            st.markdown(f"### {r['nome'] or '—'}")
            fonte = (
                f" · :material/description: {r['arquivo_fonte']}" if r.get("arquivo_fonte") else ""
            )
            st.caption(f":material/call: {r['contato'] or 'sem contato'}{fonte}")
        with col_selo:
            cor = CORES[CHAVE_COR.get(r["classificacao"], "erros")]
            st.markdown(
                f"<div style='text-align:right; font-size:34px; font-weight:800; "
                f"color:{PRETO};'>{r['pontuacao']}"
                f"<span style='font-size:13px; color:{CINZA_TXT};'> /100</span></div>"
                f"<div style='text-align:right; margin-top:4px;'>"
                f"<span class='selo' style='background:{cor['suave']}; "
                f"color:{cor['forte']};'>"
                f"{_esc(ROTULOS.get(r['classificacao'], r['classificacao']))}</span></div>",
                unsafe_allow_html=True,
            )

        col_pos, col_neg = st.columns(2)
        with col_pos:
            st.markdown(":material/thumb_up: **Pontos positivos**")
            positivos = r.get("pontos_positivos") or []
            for p in positivos:
                st.markdown(f"- {p}")
            if not positivos:
                st.caption("—")
        with col_neg:
            st.markdown(":material/report: **Pontos de atenção**")
            negativos = r.get("pontos_negativos") or []
            for p in negativos:
                st.markdown(f"- {p}")
            if not negativos:
                st.caption("—")

        st.markdown(f"**Justificativa:** {r['justificativa']}")


def _dashboard_resultado(estado: dict) -> None:
    """Painel visual completo do resultado de uma triagem."""
    st.markdown("")
    _banner(
        f"Resultado — {estado['cargo']}",
        f"{estado['total']} candidatos · {estado['duracao_min']:.1f} min · {estado['quando']}",
    )
    _kpi_cards(estado["contagens"])
    st.markdown("")

    aba_visao, aba_candidatos, aba_analise = st.tabs(
        [
            ":material/monitoring: Visão geral",
            ":material/group: Todos os candidatos",
            ":material/person_search: Análise individual",
        ]
    )

    with aba_visao:
        col_g1, col_g2 = st.columns(2)
        with col_g1, st.container(border=True):
            _titulo_bloco("Distribuição das classificações")
            st.altair_chart(_grafico_distribuicao(estado["resultados"]), width="stretch")
        with col_g2, st.container(border=True):
            _titulo_bloco("Pontuações (onde a régua está cortando)")
            st.altair_chart(_grafico_pontuacoes(estado["resultados"]), width="stretch")
        _titulo_bloco("Melhores candidatos")
        _podio(estado["resultados"])

    with aba_candidatos:
        st.caption("Ranqueados por pontuação — use o filtro ou a busca para refinar.")
        _tabela_resultados(estado["resultados"])

    with aba_analise:
        st.caption("Pontos fortes, pontos de atenção e justificativa de cada candidato.")
        _detalhe_candidato(estado["resultados"])

    st.markdown("")
    st.download_button(
        "Baixar planilha completa (Excel)",
        data=estado["planilha_bytes"],
        file_name=estado["planilha_nome"],
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
        icon=":material/download:",
    )
    st.caption("A IA faz a triagem, mas a decisão final é sempre sua.")


# === Helpers de dados ======================================================
@st.cache_resource
def _limpar_uploads_orfaos() -> None:
    """Remove pastas de upload deixadas por execuções anteriores do processo.

    Roda uma vez por boot (cache_resource), antes de existir qualquer sessão —
    sem isso, uploads de sessões abandonadas acumulam no disco do servidor.
    """
    for pasta in Path(tempfile.gettempdir()).glob("fast_triagem_*"):
        shutil.rmtree(pasta, ignore_errors=True)


def _salvar_uploads(arquivos) -> Path:
    """Salva os uploads numa pasta temporária, uma por sessão.

    O Streamlit reexecuta o script a cada interação; sem limpar a pasta
    anterior, cada rerun com arquivos no uploader criaria um tempdir novo.
    """
    anterior = st.session_state.get("pasta_uploads")
    if anterior:
        shutil.rmtree(anterior, ignore_errors=True)
    pasta = Path(tempfile.mkdtemp(prefix="fast_triagem_"))
    st.session_state["pasta_uploads"] = str(pasta)
    for arq in arquivos:
        (pasta / arq.name).write_bytes(arq.getbuffer())
    return pasta


def _resolver_planilha(execucao: dict) -> Path | None:
    """Encontra a planilha de uma execução, mesmo que tenha sido movida.

    As triagens passaram a ser salvas em vagas/<slug>/triagens/; registros
    antigos do banco ainda apontam para a pasta antiga. Quando o caminho
    registrado não existe, procura pelo nome do arquivo na estrutura nova
    e corrige o registro para as próximas visitas.
    """
    caminho = Path(execucao["planilha"])
    if caminho.exists():
        return caminho
    encontrados = sorted(PASTA_VAGAS.glob(f"*/triagens/{caminho.name}"))
    if encontrados:
        store.atualizar_planilha(execucao["id"], encontrados[0])
        return encontrados[0]
    return None


def _contar_candidatos(pasta: Path) -> tuple[int, list[str]]:
    total = 0
    avisos: list[str] = []
    for arq in sorted(pasta.iterdir()):
        ext = arq.suffix.lower()
        if ext in (".xlsx", ".xlsm"):
            try:
                _meta, candidatos = extrair_pandape(arq)
                total += len(candidatos)
            except PandapeParseError as exc:
                avisos.append(f"{arq.name}: não parece uma exportação PandaPé ({exc})")
        elif ext in (".pdf", ".docx", ".doc"):
            total += 1
        else:
            avisos.append(f"{arq.name}: tipo não suportado, será ignorado.")
    return total, avisos


def _erros_pydantic_amigaveis(exc: ValidationError) -> list[str]:
    nomes = {
        "cargo": "Cargo",
        "requisitos_obrigatorios": "Requisitos obrigatórios",
    }
    mensagens = []
    for erro in exc.errors():
        campo = nomes.get(str(erro["loc"][0]), str(erro["loc"][0]))
        if "at least 1" in erro["msg"] or "too_short" in erro["type"]:
            mensagens.append(f"{campo}: preencha pelo menos um item.")
        elif "at least 1 character" in erro["msg"]:
            mensagens.append(f"{campo}: não pode ficar vazio.")
        else:
            mensagens.append(f"{campo}: {erro['msg']}")
    return mensagens


def _executar_triagem(vaga: dict, pasta_cvs: Path) -> None:
    """Roda o pipeline com barra de progresso e guarda o resultado na sessão."""
    barra = st.progress(0, text="Preparando…")
    inicio = datetime.now()
    cronometro = time.monotonic()

    def on_progresso(feitos: int, total: int, rotulo: str) -> None:
        fracao = min(feitos / total, 1.0) if total else 0.0
        texto = f"Analisando {feitos}/{total}" + (f" — {rotulo}" if rotulo else "")
        barra.progress(fracao, text=texto)

    try:
        pasta_triagens = _pasta_vaga(vaga["criterios"].cargo) / "triagens"
        caminho, resultados = processar_vaga_criterios(
            vaga["criterios"],
            pasta_cvs,
            pasta_saida=pasta_triagens,
            on_progresso=on_progresso,
        )
    except PipelineError as exc:
        barra.empty()
        st.error(f"A triagem não pôde ser concluída: {exc}")
        return
    except Exception as exc:  # rede, disco, etc.
        barra.empty()
        st.error(f"Erro inesperado: {exc}. Se persistir, chame a Clara com o print desta tela.")
        return
    finally:
        # Uploads já foram consumidos — não deixa a pasta acumular no servidor.
        shutil.rmtree(pasta_cvs, ignore_errors=True)
        if st.session_state.get("pasta_uploads") == str(pasta_cvs):
            del st.session_state["pasta_uploads"]

    duracao = time.monotonic() - cronometro
    barra.empty()

    contagens = Counter(r.classificacao for r in resultados)
    store.registrar_execucao(
        cargo=vaga["criterios"].cargo,
        duracao_segundos=duracao,
        contagens=dict(contagens),
        planilha=caminho,
        vaga_id=vaga["id"],
        iniciada_em=inicio,
    )

    # Persiste na sessão: o painel sobrevive a recarregamentos e downloads.
    st.session_state["ultima_triagem"] = {
        "cargo": vaga["criterios"].cargo,
        "quando": inicio.strftime("%d/%m/%Y %H:%M"),
        "duracao_min": duracao / 60,
        "total": len(resultados),
        "contagens": dict(contagens),
        "resultados": [
            {
                "nome": r.nome,
                "contato": r.contato,
                "classificacao": r.classificacao,
                "pontuacao": r.pontuacao,
                "justificativa": r.justificativa,
                "pontos_positivos": r.pontos_positivos,
                "pontos_negativos": r.pontos_negativos,
                "arquivo_fonte": r.arquivo_fonte,
            }
            for r in resultados
        ],
        "planilha_bytes": caminho.read_bytes(),
        "planilha_nome": caminho.name,
    }
    st.toast("Triagem concluída!", icon=":material/check_circle:")


# === Seção: Rodar triagem ==================================================
def secao_rodar() -> None:
    _banner("Rodar triagem", "Escolha a vaga, arraste os candidatos e acompanhe.")

    if not os.environ.get("ANTHROPIC_API_KEY"):
        st.error(
            "A chave da Claude API não foi encontrada. "
            "Peça à Clara para configurar o arquivo `.env` neste computador.",
            icon=":material/key_off:",
        )
        return

    vagas = store.listar_vagas()
    if not vagas:
        _estado_vazio(
            "work_outline",
            "Nenhuma vaga cadastrada ainda",
            "Crie a primeira na seção “Vagas e critérios”, no menu à esquerda. "
            "Depois é só voltar aqui e rodar a triagem.",
        )
        return

    _passo(1, "Escolha a vaga")
    opcoes = {f"{v['cargo']}  (atualizada {v['atualizada_em'][:10]})": v for v in vagas}
    escolha = st.selectbox("Vaga", list(opcoes.keys()), label_visibility="collapsed")
    vaga = opcoes[escolha]
    with st.expander(":material/checklist: Ver critérios desta vaga"):
        crit = vaga["criterios"]
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Localização:** {crit.localizacao or '—'}")
            st.markdown(f"**Contrato:** {crit.tipo_contrato or '—'}")
            if crit.observacoes:
                st.markdown(f"**Observações:** {crit.observacoes}")
        with col2:
            st.markdown("**Requisitos obrigatórios:**")
            for r in crit.requisitos_obrigatorios:
                st.markdown(f"- {r}")
            if crit.diferenciais:
                st.markdown("**Diferenciais:**")
                for d in crit.diferenciais:
                    st.markdown(f"- {d}")

    _passo(2, "Envie os candidatos")
    arquivos = st.file_uploader(
        "Arraste a exportação do PandaPé (.xlsx) e/ou CVs avulsos (PDF/Word)",
        type=["xlsx", "xlsm", "pdf", "docx", "doc"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        help="No PandaPé: filtre/avance a etapa da vaga ANTES de exportar. "
        "Nunca exporte a etapa 'Inscritos' crua (1000+ candidatos).",
    )
    if not arquivos:
        st.caption(
            "Aceita a exportação do PandaPé (.xlsx) e CVs avulsos em PDF ou Word, tudo de uma vez."
        )

    if arquivos:
        pasta_cvs = _salvar_uploads(arquivos)
        n_candidatos, avisos = _contar_candidatos(pasta_cvs)
        for aviso in avisos:
            st.warning(aviso, icon=":material/warning:")

        if n_candidatos == 0:
            st.error(
                "Nenhum candidato encontrado nos arquivos enviados.",
                icon=":material/scan_delete:",
            )
        else:
            minutos = max(1, round(n_candidatos * 4 / 60))
            st.info(
                f"**{n_candidatos} candidato(s)** detectado(s) — estimativa: ~{minutos} min.",
                icon=":material/timer:",
            )
            confirmado = True
            if n_candidatos > LIMITE_AVISO_VOLUME:
                st.warning(
                    f"São **{n_candidatos} candidatos** — isso leva ~{minutos} min e "
                    "tem custo de API proporcional. O ideal é filtrar a vaga no PandaPé "
                    "antes de exportar.",
                    icon=":material/warning:",
                )
                confirmado = st.checkbox(
                    "Entendo o tempo/custo e quero analisar todos mesmo assim."
                )
            _passo(3, "Inicie a triagem")
            if st.button(
                "Iniciar triagem",
                type="primary",
                disabled=not confirmado,
                width="stretch",
                icon=":material/rocket_launch:",
            ):
                _executar_triagem(vaga, pasta_cvs)

    # O painel da última triagem fica visível mesmo após recarregar/baixar.
    if "ultima_triagem" in st.session_state:
        _dashboard_resultado(st.session_state["ultima_triagem"])


# === Seção: Vagas e critérios ==============================================
def secao_vagas() -> None:
    _banner("Vagas e critérios", "Cadastre uma vez, reuse em todas as triagens.")

    vagas = store.listar_vagas()
    rotulo_nova = "+ Cadastrar nova vaga"
    opcoes = [rotulo_nova] + [f"{v['cargo']}  (id {v['id']})" for v in vagas]
    escolha = st.selectbox("Vaga", opcoes)

    vaga_atual = None
    if escolha != rotulo_nova:
        vaga_atual = vagas[opcoes.index(escolha) - 1]

    crit = vaga_atual["criterios"] if vaga_atual else None
    chave = f"vaga_{vaga_atual['id'] if vaga_atual else 'nova'}"

    with st.form(key=f"form_{chave}"):
        cargo = st.text_input(
            "Cargo *",
            value=crit.cargo if crit else "",
            placeholder="Ex: Auxiliar Administrativo Comercial - Centro/RJ",
        )
        col1, col2 = st.columns(2)
        with col1:
            localizacao = st.text_input(
                "Localização",
                value=crit.localizacao if crit else "",
                placeholder="Ex: Rio de Janeiro - RJ / Remoto",
            )
        with col2:
            tipo_contrato = st.text_input(
                "Tipo de contrato",
                value=crit.tipo_contrato if crit else "",
                placeholder="Ex: CLT / PJ / Estágio",
            )
        observacoes = st.text_area(
            "Observações (contexto extra para a IA)",
            value=crit.observacoes if crit else "",
            height=80,
        )

        st.markdown("**Requisitos obrigatórios** *— quem não atender é reprovado*")
        req_inicial = [{"Requisito": r} for r in (crit.requisitos_obrigatorios if crit else [])]
        req_editor = st.data_editor(
            req_inicial or [{"Requisito": ""}],
            num_rows="dynamic",
            width="stretch",
            key=f"req_{chave}",
            column_config={"Requisito": st.column_config.TextColumn(width="large")},
        )

        st.markdown("**Diferenciais** *— pesam a favor, não eliminam*")
        dif_inicial = [{"Diferencial": d} for d in (crit.diferenciais if crit else [])]
        dif_editor = st.data_editor(
            dif_inicial or [{"Diferencial": ""}],
            num_rows="dynamic",
            width="stretch",
            key=f"dif_{chave}",
            column_config={"Diferencial": st.column_config.TextColumn(width="large")},
        )

        salvar = st.form_submit_button(
            "Salvar vaga" if vaga_atual is None else "Salvar alterações",
            type="primary",
            icon=":material/save:",
        )

    if salvar:
        requisitos = [
            str(linha["Requisito"]).strip()
            for linha in req_editor
            if str(linha.get("Requisito") or "").strip()
        ]
        diferenciais = [
            str(linha["Diferencial"]).strip()
            for linha in dif_editor
            if str(linha.get("Diferencial") or "").strip()
        ]
        try:
            criterios = VagaCriterios(
                cargo=cargo.strip(),
                localizacao=localizacao.strip(),
                tipo_contrato=tipo_contrato.strip(),
                observacoes=observacoes.strip(),
                requisitos_obrigatorios=requisitos,
                diferenciais=diferenciais,
            )
        except ValidationError as exc:
            for m in _erros_pydantic_amigaveis(exc):
                st.error(m)
            return
        vaga_id = store.salvar_vaga(criterios, vaga_id=vaga_atual["id"] if vaga_atual else None)
        _pasta_vaga(criterios.cargo)  # garante vagas/<slug>/cvs/ e triagens/
        st.success(f"Vaga **{criterios.cargo}** salva (id {vaga_id}).")
        time.sleep(1)
        st.rerun()

    if vaga_atual:
        st.divider()
        with st.expander(":material/archive: Arquivar esta vaga"):
            st.caption(
                "A vaga some das listas, mas nada é apagado — o histórico fica e "
                "dá pra restaurar em **Vagas arquivadas**, aqui embaixo."
            )
            if st.button("Confirmar arquivamento", icon=":material/archive:"):
                store.arquivar_vaga(vaga_atual["id"])
                st.success("Vaga arquivada.")
                time.sleep(1)
                st.rerun()

    arquivadas = [v for v in store.listar_vagas(incluir_arquivadas=True) if v["arquivada"]]
    if arquivadas:
        st.divider()
        with st.expander(f":material/inventory_2: Vagas arquivadas ({len(arquivadas)})"):
            st.caption(
                "Restaurar traz a vaga de volta às listas. Excluir apaga o cadastro "
                "em definitivo — o histórico de triagens e as planilhas são mantidos."
            )
            for v in arquivadas:
                col_info, col_rest, col_excl = st.columns([3, 1, 1], vertical_alignment="center")
                with col_info:
                    st.markdown(f"**{v['cargo']}**  \n:gray[id {v['id']} · arquivada]")
                with col_rest:
                    if st.button(
                        "Restaurar",
                        key=f"restaurar_{v['id']}",
                        icon=":material/unarchive:",
                        width="stretch",
                    ):
                        store.desarquivar_vaga(v["id"])
                        st.success(f"Vaga **{v['cargo']}** restaurada.")
                        time.sleep(1)
                        st.rerun()
                with (
                    col_excl,
                    st.popover("Excluir", icon=":material/delete:", width="stretch"),
                ):
                        st.markdown(
                            f"Excluir **{v['cargo']}** em definitivo? Não dá pra desfazer."
                        )
                        if st.button(
                            "Sim, excluir",
                            key=f"excluir_{v['id']}",
                            type="primary",
                            icon=":material/delete_forever:",
                        ):
                            store.excluir_vaga(v["id"])
                            st.success(f"Vaga **{v['cargo']}** excluída.")
                            time.sleep(1)
                            st.rerun()


# === Seção: Histórico ======================================================
def secao_historico() -> None:
    _banner("Histórico de triagens", "O que a automação já economizou de leitura manual.")

    execucoes = store.listar_execucoes()
    if not execucoes:
        _estado_vazio(
            "history",
            "Nenhuma triagem registrada ainda",
            "Rode a primeira na seção “Rodar triagem”, no menu à esquerda. "
            "Cada execução fica registrada aqui com a planilha para baixar de novo.",
        )
        return

    total_candidatos = sum(e["total"] for e in execucoes)
    tempo_total_min = sum(e["duracao_segundos"] for e in execucoes) / 60
    _kpi_cards(
        {
            "aprovado": sum(e["aprovados"] for e in execucoes),
            "verificar": sum(e["verificar"] for e in execucoes),
            "reprovado": sum(e["reprovados"] for e in execucoes),
        }
    )
    st.markdown("")
    col1, col2, col3 = st.columns(3)
    col1.metric("Triagens realizadas", len(execucoes))
    col2.metric("Candidatos analisados", total_candidatos)
    col3.metric("Tempo de máquina", f"{tempo_total_min:.0f} min")
    st.caption(
        "Cada candidato analisado é um CV que não precisou ser lido manualmente "
        "na primeira passada."
    )

    # Gráfico: candidatos por triagem, empilhado por classificação.
    if len(execucoes) > 1:
        st.markdown("")
        linhas = []
        for e in reversed(execucoes):  # cronológico
            data = e["iniciada_em"][:16].replace("T", " ")
            etiqueta = f"{data} · {e['cargo'][:30]}"
            for chave, rotulo in (
                ("aprovados", "Aprovados"),
                ("verificar", "Verificar"),
                ("reprovados", "Reprovados"),
                ("erros", "Erros"),
            ):
                if e[chave]:
                    linhas.append(
                        {"Triagem": etiqueta, "Classificação": rotulo, "Candidatos": e[chave]}
                    )
        df = pd.DataFrame(linhas)
        grafico = (
            alt.Chart(df)
            .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
            .encode(
                x=alt.X(
                    "Triagem:N",
                    sort=None,
                    title=None,
                    axis=alt.Axis(labelAngle=-30, labelLimit=220),
                ),
                y=alt.Y("Candidatos:Q"),
                color=alt.Color(
                    "Classificação:N",
                    scale=alt.Scale(
                        domain=["Aprovados", "Verificar", "Reprovados", "Erros"],
                        range=[
                            CORES["aprovado"]["forte"],
                            CORES["verificar"]["forte"],
                            CORES["reprovado"]["forte"],
                            CORES["erros"]["forte"],
                        ],
                    ),
                    legend=alt.Legend(orient="bottom", title=None),
                ),
                tooltip=["Triagem", "Classificação", "Candidatos"],
            )
            .properties(height=280)
        )
        with st.container(border=True):
            _titulo_bloco("Triagens ao longo do tempo")
            st.altair_chart(grafico, width="stretch")

    st.divider()
    _titulo_bloco("Todas as triagens")
    for execucao in execucoes:
        with st.container(border=True):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f"**{execucao['cargo']}**")
                st.caption(
                    f"{execucao['iniciada_em'][:16].replace('T', ' às ')} · "
                    f"{execucao['total']} candidatos · "
                    f"{execucao['aprovados']} aprovados · "
                    f"{execucao['verificar']} verificar · "
                    f"{execucao['reprovados']} reprovados"
                    + (f" · {execucao['erros']} erros" if execucao["erros"] else "")
                )
            with col_b:
                planilha = _resolver_planilha(execucao)
                if planilha:
                    st.download_button(
                        "Planilha",
                        data=planilha.read_bytes(),
                        file_name=planilha.name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"dl_{execucao['id']}",
                        icon=":material/download:",
                    )
                else:
                    st.caption("Planilha não encontrada — foi movida ou apagada.")
                with st.popover("Excluir", icon=":material/delete:"):
                    st.markdown(
                        "Excluir esta triagem do histórico? A planilha dela também "
                        "será apagada. Não dá pra desfazer."
                    )
                    if st.button(
                        "Sim, excluir",
                        key=f"excluir_exec_{execucao['id']}",
                        type="primary",
                        icon=":material/delete_forever:",
                    ):
                        if planilha:
                            planilha.unlink(missing_ok=True)
                        store.excluir_execucao(execucao["id"])
                        st.success("Triagem excluída.")
                        time.sleep(1)
                        st.rerun()


# === Navegação =============================================================
SECOES = {
    ":material/play_circle: Rodar triagem": secao_rodar,
    ":material/work: Vagas e critérios": secao_vagas,
    ":material/history: Histórico": secao_historico,
}


def _porta_de_acesso() -> bool:
    """Pede a senha do time quando o app roda num servidor.

    Só ativa quando TRIAGEM_SENHA está definida no ambiente; no uso local
    (sem a variável) o app abre direto, como sempre.
    """
    senha = os.getenv("TRIAGEM_SENHA", "").strip()
    if not senha or st.session_state.get("acesso_liberado"):
        return True

    _, centro, _ = st.columns([1, 1.1, 1])
    with centro:
        st.write("")
        st.write("")
        if LOGO.exists():
            st.image(str(LOGO), width=180)
        st.markdown("### Triagem de Candidatos")
        st.caption("Acesso restrito ao time de R&S da Fast.")
        with st.form("acesso"):
            tentativa = st.text_input("Senha do time", type="password")
            entrar = st.form_submit_button("Entrar", type="primary", use_container_width=True)
        if entrar:
            if hmac.compare_digest(tentativa, senha):
                st.session_state["acesso_liberado"] = True
                st.rerun()
            st.error("Senha incorreta. Confira com a Clara Barbosa.")
    return False


def main() -> None:
    _limpar_uploads_orfaos()
    with st.sidebar:
        if LOGO.exists():
            st.image(str(LOGO), width=180)
        st.markdown("### Triagem de Candidatos")
        secao = st.radio(
            "Navegação",
            list(SECOES.keys()),
            label_visibility="collapsed",
        )
        st.divider()
        st.caption("R&S · Fast Sistemas Construtivos\n\nDúvidas? Fale com a Clara Barbosa.")

    SECOES[secao]()


if _porta_de_acesso():
    main()
