"""Persistência local do app de triagem (SQLite, stdlib).

Guarda duas coisas:
  - vagas: critérios salvos pela operadora, reusáveis entre triagens.
  - execucoes: histórico agregado de cada triagem (contagens, duração,
    caminho da planilha). Por desenho, NÃO guarda dados de candidatos —
    nome, contato e análise vivem só nas planilhas geradas.

O banco fica em data/triagem.db (criado sob demanda, fora do Git).
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import VagaCriterios

_DB_PADRAO = Path("data") / "triagem.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS vagas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cargo TEXT NOT NULL,
    criterios_json TEXT NOT NULL,
    criada_em TEXT NOT NULL,
    atualizada_em TEXT NOT NULL,
    arquivada INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS execucoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vaga_id INTEGER,
    cargo TEXT NOT NULL,
    iniciada_em TEXT NOT NULL,
    duracao_segundos REAL NOT NULL,
    total INTEGER NOT NULL,
    aprovados INTEGER NOT NULL,
    verificar INTEGER NOT NULL,
    reprovados INTEGER NOT NULL,
    erros INTEGER NOT NULL,
    planilha TEXT NOT NULL,
    FOREIGN KEY (vaga_id) REFERENCES vagas (id)
);
"""


class StoreError(Exception):
    """Erro de persistência do app."""


def _conectar(db_path: str | Path = _DB_PADRAO) -> sqlite3.Connection:
    caminho = Path(db_path)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(caminho)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    return conn


def _agora() -> str:
    return datetime.now().isoformat(timespec="seconds")


# === Vagas =================================================================
def salvar_vaga(
    criterios: VagaCriterios,
    vaga_id: int | None = None,
    db_path: str | Path = _DB_PADRAO,
) -> int:
    """Cria (vaga_id=None) ou atualiza uma vaga. Retorna o id."""
    payload = criterios.model_dump_json()
    with _conectar(db_path) as conn:
        if vaga_id is None:
            cur = conn.execute(
                "INSERT INTO vagas (cargo, criterios_json, criada_em, atualizada_em)"
                " VALUES (?, ?, ?, ?)",
                (criterios.cargo, payload, _agora(), _agora()),
            )
            return int(cur.lastrowid)
        atualizadas = conn.execute(
            "UPDATE vagas SET cargo = ?, criterios_json = ?, atualizada_em = ? WHERE id = ?",
            (criterios.cargo, payload, _agora(), vaga_id),
        ).rowcount
        if not atualizadas:
            raise StoreError(f"Vaga id={vaga_id} não encontrada para atualizar.")
        return vaga_id


def listar_vagas(
    incluir_arquivadas: bool = False, db_path: str | Path = _DB_PADRAO
) -> list[dict[str, Any]]:
    """Lista vagas (mais recentes primeiro), com critérios desserializados."""
    sql = "SELECT * FROM vagas"
    if not incluir_arquivadas:
        sql += " WHERE arquivada = 0"
    sql += " ORDER BY atualizada_em DESC"
    with _conectar(db_path) as conn:
        linhas = conn.execute(sql).fetchall()
    return [_vaga_para_dict(linha) for linha in linhas]


def obter_vaga(vaga_id: int, db_path: str | Path = _DB_PADRAO) -> dict[str, Any] | None:
    with _conectar(db_path) as conn:
        linha = conn.execute("SELECT * FROM vagas WHERE id = ?", (vaga_id,)).fetchone()
    return _vaga_para_dict(linha) if linha else None


def arquivar_vaga(vaga_id: int, db_path: str | Path = _DB_PADRAO) -> None:
    """Esconde a vaga das listagens sem apagar o histórico dela."""
    with _conectar(db_path) as conn:
        conn.execute(
            "UPDATE vagas SET arquivada = 1, atualizada_em = ? WHERE id = ?",
            (_agora(), vaga_id),
        )


def _vaga_para_dict(linha: sqlite3.Row) -> dict[str, Any]:
    dados = dict(linha)
    dados["criterios"] = VagaCriterios(**json.loads(dados.pop("criterios_json")))
    return dados


# === Execuções (histórico) =================================================
def registrar_execucao(
    *,
    cargo: str,
    duracao_segundos: float,
    contagens: dict[str, int],
    planilha: str | Path,
    vaga_id: int | None = None,
    iniciada_em: datetime | None = None,
    db_path: str | Path = _DB_PADRAO,
) -> int:
    """Grava o resumo agregado de uma triagem concluída. Retorna o id."""
    inicio = (iniciada_em or datetime.now()).isoformat(timespec="seconds")
    aprovados = contagens.get("aprovado", 0)
    verificar = contagens.get("verificar", 0)
    reprovados = contagens.get("reprovado", 0)
    erros = contagens.get("erro_parsing", 0) + contagens.get("erro_api", 0)
    total = sum(contagens.values())
    with _conectar(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO execucoes (vaga_id, cargo, iniciada_em, duracao_segundos,"
            " total, aprovados, verificar, reprovados, erros, planilha)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                vaga_id,
                cargo,
                inicio,
                duracao_segundos,
                total,
                aprovados,
                verificar,
                reprovados,
                erros,
                str(planilha),
            ),
        )
        return int(cur.lastrowid)


def listar_execucoes(limite: int = 100, db_path: str | Path = _DB_PADRAO) -> list[dict[str, Any]]:
    """Histórico de triagens, mais recentes primeiro."""
    with _conectar(db_path) as conn:
        linhas = conn.execute(
            "SELECT * FROM execucoes ORDER BY iniciada_em DESC LIMIT ?", (limite,)
        ).fetchall()
    return [dict(linha) for linha in linhas]


def atualizar_planilha(
    execucao_id: int, planilha: str | Path, db_path: str | Path = _DB_PADRAO
) -> None:
    """Corrige o caminho da planilha de uma execução (ex.: arquivo movido)."""
    with _conectar(db_path) as conn:
        atualizadas = conn.execute(
            "UPDATE execucoes SET planilha = ? WHERE id = ?",
            (str(planilha), execucao_id),
        ).rowcount
        if not atualizadas:
            raise StoreError(f"Execução id={execucao_id} não encontrada para atualizar.")
