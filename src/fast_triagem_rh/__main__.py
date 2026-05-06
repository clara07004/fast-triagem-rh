"""Ponto de entrada da automação.

Uso:
    python -m fast_triagem_rh
"""

from __future__ import annotations

from dotenv import load_dotenv

from .envelope import run_envelope
from .logger import get_logger

load_dotenv()

log = get_logger(__name__)


def main() -> None:
    """Executa a automação dentro de um envelope."""
    with run_envelope("fast_triagem_rh-main") as env:
        log.info("Iniciando automação")

        # === Sua lógica aqui ===
        # Exemplo:
        # for item in obter_dados():
        #     try:
        #         processar(item)
        #         env.add_processed()
        #     except Exception as exc:
        #         env.add_failed(error=str(exc))

        log.info("Automação concluída")


if __name__ == "__main__":
    main()
