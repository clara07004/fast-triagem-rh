"""Modelos de dados do pipeline de triagem.

VagaCriterios  — input de Karina (critérios da vaga)
ResultadoCandidato — output da análise por candidato
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class VagaCriterios(BaseModel):
    """Critérios de uma vaga. Preenchido por Karina via template Excel."""

    cargo: str = Field(..., min_length=1, description="Título da vaga")
    requisitos_obrigatorios: list[str] = Field(
        ...,
        min_length=1,
        description=(
            "Itens eliminatórios — candidato reprovado se não atender. "
            "Pelo menos um é obrigatório: sem requisito eliminatório não há o que triar."
        ),
    )
    diferenciais: list[str] = Field(
        default_factory=list,
        description="Itens que pesam positivamente na classificação",
    )
    localizacao: str = Field(
        default="",
        description="Cidade/estado aceitos. Ex: 'São Paulo - SP' ou 'Remoto'",
    )
    tipo_contrato: str = Field(
        default="",
        description="CLT, PJ, Estágio, etc.",
    )
    observacoes: str = Field(
        default="",
        description="Qualquer informação adicional relevante para a triagem",
    )


Classificacao = Literal["aprovado", "reprovado", "verificar", "erro_parsing", "erro_api"]


class ResultadoCandidato(BaseModel):
    """Resultado da análise de um candidato. Uma linha na planilha de output."""

    nome: str | None = Field(None, description="Nome completo extraído do CV")
    contato: str | None = Field(None, description="Email e/ou telefone extraídos do CV")
    classificacao: Classificacao = Field(..., description="Resultado da triagem")
    pontuacao: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Aderência geral à vaga (0 = nenhuma, 100 = perfeita)",
    )
    pontos_positivos: list[str] = Field(default_factory=list)
    pontos_negativos: list[str] = Field(default_factory=list)
    justificativa: str = Field(
        default="",
        description="2-3 frases explicando a classificação",
    )
    arquivo_fonte: str = Field(
        default="",
        description="Nome do arquivo de origem (PDF, DOCX, PandaPé, etc.)",
    )
    data_triagem: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp do processamento",
    )
