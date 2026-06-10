"""Builders de fixtures para os testes.

Geram arquivos reais (.docx, .xlsx) em diretórios temporários, espelhando o
layout que cada parser espera. Evita depender de arquivos versionados ou de
dados reais de candidatos.
"""

from __future__ import annotations

from pathlib import Path

import openpyxl
import pytest
from docx import Document


@pytest.fixture
def criar_criterios(tmp_path: Path):
    """Cria um criterios.xlsx no layout esperado por parse_criterios."""

    def _criar(
        cargo: str = "Vendedor Técnico",
        localizacao: str = "Miguel Pereira - RJ",
        tipo_contrato: str = "CLT",
        observacoes: str = "",
        requisitos: list[str] | None = None,
        diferenciais: list[str] | None = None,
        nome: str = "criterios.xlsx",
        aba: str = "Critérios",
    ) -> Path:
        requisitos = requisitos if requisitos is not None else ["Experiência em vendas"]
        diferenciais = diferenciais or []

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = aba
        ws.cell(3, 2, cargo)
        ws.cell(4, 2, localizacao)
        ws.cell(5, 2, tipo_contrato)
        ws.cell(6, 2, observacoes)
        for i, req in enumerate(requisitos[:4]):  # linhas 8–11
            ws.cell(8 + i, 2, req)
        for i, dif in enumerate(diferenciais[:4]):  # linhas 13–16
            ws.cell(13 + i, 2, dif)

        caminho = tmp_path / nome
        wb.save(caminho)
        return caminho

    return _criar


@pytest.fixture
def criar_docx(tmp_path: Path):
    """Cria um .docx real com parágrafos e (opcionalmente) uma tabela."""

    def _criar(
        paragrafos: list[str] | None = None,
        tabela: list[tuple[str, str]] | None = None,
        nome: str = "cv.docx",
    ) -> Path:
        doc = Document()
        for p in paragrafos or []:
            doc.add_paragraph(p)
        if tabela:
            t = doc.add_table(rows=len(tabela), cols=2)
            for linha, (a, b) in zip(t.rows, tabela, strict=False):
                linha.cells[0].text = a
                linha.cells[1].text = b
        caminho = tmp_path / nome
        doc.save(caminho)
        return caminho

    return _criar


@pytest.fixture
def criar_pandape(tmp_path: Path):
    """Cria uma exportação PandaPé real no layout esperado pelo parser."""

    headers_padrao = [
        "Nome", "Sobrenome", "E-mail", "Telefone", "Celular", "Estado",
        "Cidade", "Título", "Experiência Profissional", "Idiomas",
        "Data de Inscrição",
    ]

    def _criar(
        cargo: str = "Vendedor Técnico",
        candidatos: list[dict] | None = None,
        headers: list[str] | None = None,
        nome: str = "pandape.xlsx",
    ) -> Path:
        candidatos = candidatos if candidatos is not None else [
            {
                "Nome": "Ana", "Sobrenome": "Souza", "E-mail": "ana@x.com",
                "Telefone": "21 99999-0000", "Cidade": "Miguel Pereira",
                "Estado": "RJ", "Título": "Vendedora Pleno",
                "Experiência Profissional": "5 anos em vendas", "Idiomas": "Português",
            }
        ]
        cols = headers if headers is not None else headers_padrao

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.cell(1, 2, cargo)
        ws.cell(2, 2, "REF-001")
        ws.cell(3, 2, "Inscritos")
        ws.cell(4, 2, "tag")
        for col, h in enumerate(cols, start=1):
            ws.cell(6, col, h)
        for linha_idx, cand in enumerate(candidatos, start=7):
            for col, h in enumerate(cols, start=1):
                if h in cand:
                    ws.cell(linha_idx, col, cand[h])

        caminho = tmp_path / nome
        wb.save(caminho)
        return caminho

    return _criar
