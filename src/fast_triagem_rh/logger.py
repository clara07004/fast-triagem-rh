"""Logger estruturado padrão da Fast.

Emite JSON em produção e console legível em desenvolvimento.
Mascara automaticamente campos sensíveis (token, password, api_key, etc).

Uso:
    from fast_triagem_rh.logger import get_logger
    log = get_logger(__name__)
    log.info("Processo iniciado", extra={"items": 42})
"""

from __future__ import annotations

import os
import re
import sys
from typing import Any

from loguru import logger

# Padrões de campos a mascarar em logs
SENSITIVE_PATTERNS = [
    re.compile(r"(token|password|api_key|secret|authorization|bearer)[\"':=\s]+[\w\-./+=]+", re.IGNORECASE),
]


def _mask_sensitive(message: str) -> str:
    """Mascara valores sensíveis em strings de log."""
    masked = message
    for pattern in SENSITIVE_PATTERNS:
        masked = pattern.sub(lambda m: f"{m.group(1)}=***", masked)
    return masked


def _format_record(record: dict[str, Any]) -> str:
    """Formato de console legível pra desenvolvimento."""
    record["message"] = _mask_sensitive(record["message"])
    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "{message}\n{exception}"
    )


def setup_logger() -> None:
    """Configura o logger global. Chamar uma vez no início da aplicação."""
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_format = os.environ.get("LOG_FORMAT", "console").lower()
    project_name = os.environ.get("PROJECT_NAME", "fast_triagem_rh")
    environment = os.environ.get("ENVIRONMENT", "development")

    logger.remove()  # remove handler padrão

    if log_format == "json":
        logger.add(
            sys.stdout,
            level=log_level,
            serialize=True,  # JSON
            backtrace=False,
            diagnose=False,
        )
    else:
        logger.add(
            sys.stdout,
            level=log_level,
            format=_format_record,
            backtrace=True,
            diagnose=True,
        )

    logger.configure(extra={"project": project_name, "environment": environment})


def get_logger(name: str) -> Any:
    """Retorna um logger com binding do nome do módulo."""
    return logger.bind(module=name)


# Setup ao importar
setup_logger()
