"""Interface de linha de comando da triagem.

Uso:
    python -m fast_triagem_rh --vaga criterios.xlsx --cvs pasta/cvs/

Pensado para a Karina rodar sem ajuda técnica: mensagens de erro em
linguagem simples (sem traceback) e um resumo claro ao final.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

from .logger import get_logger
from .models import Classificacao
from .pipeline import PipelineError, processar_vaga

load_dotenv()

log = get_logger(__name__)

# Rótulos legíveis por classificação, para o resumo final.
_RESUMO_ROTULO: dict[Classificacao, str] = {
    "aprovado": "aprovados",
    "verificar": "para verificar",
    "reprovado": "reprovados",
    "erro_parsing": "com erro de leitura",
    "erro_api": "com erro de análise",
}


def _erro(mensagem: str) -> None:
    """Imprime um erro amigável no stderr e encerra com código 1."""
    print(f"\n[ERRO] {mensagem}\n", file=sys.stderr)
    sys.exit(1)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="fast_triagem_rh",
        description="Triagem automática de candidatos contra os critérios de uma vaga.",
    )
    parser.add_argument(
        "--vaga",
        required=True,
        metavar="criterios.xlsx",
        help="Caminho do template Excel com os critérios da vaga.",
    )
    parser.add_argument(
        "--cvs",
        required=True,
        metavar="pasta/",
        help="Pasta com os currículos (PDF/Word) e/ou a exportação do PandaPé.",
    )
    parser.add_argument(
        "--saida",
        default=".",
        metavar="pasta/",
        help="Pasta onde gravar a planilha de triagem (padrão: pasta atual).",
    )
    return parser.parse_args(argv)


def _imprimir_resumo(caminho: Path, resultados: list) -> None:
    """Mostra o resumo final da triagem em linguagem simples."""
    contagem = Counter(r.classificacao for r in resultados)
    total = len(resultados)

    partes = [
        f"{contagem[c]} {rotulo}"
        for c, rotulo in _RESUMO_ROTULO.items()
        if contagem.get(c)
    ]
    detalhe = ", ".join(partes) if partes else "nenhum candidato"

    print(f"\nTriagem concluida — {total} candidato(s) processado(s).")
    print(f"   {detalhe}.")
    print(f"\nPlanilha gerada: {caminho}\n")


def main(argv: list[str] | None = None) -> None:
    """Ponto de entrada da CLI."""
    args = _parse_args(argv)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        _erro(
            "A chave da Claude API não foi encontrada.\n"
            "   Crie um arquivo .env (copie de .env.example) e preencha "
            "ANTHROPIC_API_KEY=sk-..."
        )

    try:
        caminho, resultados = processar_vaga(args.vaga, args.cvs, pasta_saida=args.saida)
    except PipelineError as exc:
        _erro(str(exc))
    except KeyboardInterrupt:
        _erro("Triagem interrompida pelo usuário.")
    except Exception as exc:  # rede a API, disco cheio, etc.
        log.exception("Erro inesperado na triagem")
        _erro(
            f"Ocorreu um erro inesperado: {exc}\n"
            "   Se persistir, chame a Clara com o print desta mensagem."
        )

    _imprimir_resumo(caminho, resultados)


if __name__ == "__main__":
    main()
