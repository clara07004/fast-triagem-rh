"""Parser de exportação PandaPé.

Lê arquivo Excel exportado da plataforma PandaPé e extrai metadados da vaga
+ lista de candidatos com seus dados de contato e CV.

Estrutura esperada (PandaPé 2024-2025):
  Linhas 1-4: Metadados (Nome da vaga, Referência, Etapa, Tags)
  Linha 5: Vazia
  Linha 6: Headers (Nome, Sobrenome, Email, Telefone, etc.)
  Linhas 7+: Candidatos
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import openpyxl


class PandapeParseError(Exception):
    """Falha ao extrair dados do arquivo PandaPé."""


@dataclass
class MetadadosPandape:
    """Metadados da vaga no arquivo PandaPé."""

    cargo: str
    referencia_id: str
    etapa: str
    tags: str


@dataclass
class CandidatoPandape:
    """Dados de um candidato extraído da exportação PandaPé."""

    nome: str
    sobrenome: str
    email: str | None
    telefone: str | None
    celular: str | None
    estado: str | None
    cidade: str | None
    titulo_profissional: str | None
    experiencia_profissional: str | None
    tags_cv: str | None
    idiomas: str | None
    data_inscricao: str | None


def extrair_pandape(
    arquivo_xlsx: str | Path,
) -> tuple[MetadadosPandape, list[CandidatoPandape]]:
    """Extrai metadados e candidatos do arquivo PandaPé.

    Args:
        arquivo_xlsx: Caminho para o arquivo .xlsx exportado da PandaPé.

    Returns:
        Tupla (metadados, lista de candidatos).

    Raises:
        PandapeParseError: Se o arquivo não existir, estrutura for inválida,
                          ou não conseguir ler os dados.
    """
    arquivo_xlsx = Path(arquivo_xlsx)

    if not arquivo_xlsx.exists():
        raise PandapeParseError(f"Arquivo não encontrado: {arquivo_xlsx}")

    try:
        wb = openpyxl.load_workbook(arquivo_xlsx, data_only=True)
    except Exception as exc:
        raise PandapeParseError(f"Não foi possível abrir o arquivo: {exc}") from exc

    if not wb.sheetnames:
        raise PandapeParseError("Arquivo Excel vazio (sem abas)")

    ws = wb.active

    # === Extrair metadados (linhas 1-4, coluna B) ===
    try:
        cargo = str(ws.cell(1, 2).value or "").strip()
        referencia_id = str(ws.cell(2, 2).value or "").strip()
        etapa = str(ws.cell(3, 2).value or "").strip()
        tags = str(ws.cell(4, 2).value or "").strip()

        if not cargo:
            raise PandapeParseError("Campo 'Nome da vaga' (B1) vazio ou inválido")

        metadados = MetadadosPandape(
            cargo=cargo,
            referencia_id=referencia_id,
            etapa=etapa,
            tags=tags,
        )
    except PandapeParseError:
        raise
    except Exception as exc:
        raise PandapeParseError(
            f"Erro ao extrair metadados da vaga: {exc}"
        ) from exc

    # === Mapear headers (linha 6) ===
    headers_linha = 6
    headers_map: dict[str, int] = {}  # {nome_coluna: numero_coluna}

    for col in range(1, ws.max_column + 1):
        header = ws.cell(headers_linha, col).value
        if header:
            headers_map[str(header).strip().lower()] = col

    # Validar headers obrigatórios
    obrigatorios = {"nome", "sobrenome", "e-mail"}
    encontrados = set(headers_map.keys())
    if not obrigatorios.issubset(encontrados):
        faltantes = obrigatorios - encontrados
        raise PandapeParseError(
            f"Headers obrigatórios não encontrados: {faltantes}. "
            f"Verifique se o arquivo é uma exportação válida da PandaPé."
        )

    # === Extrair candidatos (linhas 7+) ===
    candidatos: list[CandidatoPandape] = []

    for row in range(headers_linha + 1, ws.max_row + 1):
        # Verificar se linha tem dados (ao menos nome)
        nome_val = ws.cell(row, headers_map.get("nome", 1)).value
        if not nome_val:
            continue  # Pular linhas vazias no final

        try:
            # Funções auxiliares para extrair valores de forma robusta
            def get_col(header_name: str) -> str | None:
                """Retorna valor da célula para um header, ou None."""
                col = headers_map.get(header_name.lower())
                if col:
                    val = ws.cell(row, col).value
                    return str(val).strip() if val else None
                return None

            nome = get_col("nome") or ""
            sobrenome = get_col("sobrenome") or ""
            email = get_col("e-mail")
            telefone = get_col("telefone")
            celular = get_col("celular")
            estado = get_col("estado")
            cidade = get_col("cidade")
            titulo = get_col("título")
            experiencia = get_col("experiência profissional")
            tags_cv = get_col("tag's do cv do candidato")
            idiomas = get_col("idiomas")
            data_inscricao = get_col("data de inscrição")

            candidato = CandidatoPandape(
                nome=nome,
                sobrenome=sobrenome,
                email=email,
                telefone=telefone,
                celular=celular,
                estado=estado,
                cidade=cidade,
                titulo_profissional=titulo,
                experiencia_profissional=experiencia,
                tags_cv=tags_cv,
                idiomas=idiomas,
                data_inscricao=data_inscricao,
            )
            candidatos.append(candidato)

        except Exception as exc:
            raise PandapeParseError(
                f"Erro ao extrair candidato da linha {row}: {exc}"
            ) from exc

    if not candidatos:
        raise PandapeParseError(
            "Nenhum candidato encontrado no arquivo. "
            "Verifique se o formato está correto."
        )

    return metadados, candidatos
