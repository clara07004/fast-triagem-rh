"""Envelope de execução — padrão pra toda execução de automação.

Garante que toda execução tenha:
- timestamp de início
- timestamp de fim
- duração
- status (ok / error)
- contagem de itens processados
- run_id único (rastreável em logs)

Uso:
    from fast_triagem_rh.envelope import run_envelope

    @run_envelope("triagem-emails")
    def main():
        # ... lógica da automação ...
        return {"processed": 42, "failed": 1}

Ou como context manager:
    with run_envelope("triagem-emails") as env:
        env.add_processed(10)
        # ...
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable, Generator
from contextlib import contextmanager
from functools import wraps
from typing import Any

from .logger import get_logger

log = get_logger(__name__)


class ExecutionEnvelope:
    """Envelope que rastreia uma execução."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.run_id = str(uuid.uuid4())[:8]
        self.start_time = time.time()
        self.end_time: float | None = None
        self.processed = 0
        self.failed = 0
        self.errors: list[str] = []
        self.metadata: dict[str, Any] = {}

    @property
    def duration_seconds(self) -> float:
        end = self.end_time or time.time()
        return round(end - self.start_time, 3)

    def add_processed(self, n: int = 1) -> None:
        self.processed += n

    def add_failed(self, n: int = 1, error: str | None = None) -> None:
        self.failed += n
        if error:
            self.errors.append(error)

    def set(self, key: str, value: Any) -> None:
        self.metadata[key] = value

    def to_dict(self) -> dict[str, Any]:
        return {
            "envelope": self.name,
            "run_id": self.run_id,
            "duration_seconds": self.duration_seconds,
            "processed": self.processed,
            "failed": self.failed,
            "errors": self.errors[:5],  # primeiros 5 erros só
            "metadata": self.metadata,
        }


@contextmanager
def run_envelope(name: str) -> Generator[ExecutionEnvelope, None, None]:
    """Context manager que abre/fecha um envelope.

    Loga início, fim e exception (se houver).
    """
    env = ExecutionEnvelope(name)
    log.info(
        "Envelope iniciado",
        extra={"envelope": name, "run_id": env.run_id},
    )
    try:
        yield env
        env.end_time = time.time()
        log.info(
            "Envelope concluído com sucesso",
            extra={**env.to_dict(), "status": "ok"},
        )
    except Exception as exc:
        env.end_time = time.time()
        env.add_failed(error=str(exc))
        log.exception(
            "Envelope concluído com erro",
            extra={**env.to_dict(), "status": "error"},
        )
        raise


def envelope_decorator(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator que envolve uma função em um envelope."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with run_envelope(name) as env:
                kwargs.setdefault("envelope", env)
                return func(*args, **kwargs)

        return wrapper

    return decorator
