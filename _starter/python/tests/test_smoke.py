"""Smoke tests — garantem que módulos básicos importam e logger/envelope funcionam."""

from __future__ import annotations

import PROJECT_NAME_PLACEHOLDER
from PROJECT_NAME_PLACEHOLDER.envelope import run_envelope
from PROJECT_NAME_PLACEHOLDER.logger import get_logger


def test_pacote_tem_versao():
    assert PROJECT_NAME_PLACEHOLDER.__version__


def test_logger_funciona():
    log = get_logger("test")
    log.info("teste")  # não deve levantar exceção


def test_envelope_sucesso():
    with run_envelope("test-sucesso") as env:
        env.add_processed(5)
        env.set("origem", "teste")

    assert env.processed == 5
    assert env.failed == 0
    assert env.metadata["origem"] == "teste"
    assert env.duration_seconds >= 0


def test_envelope_falha_propaga_excecao():
    import pytest

    with pytest.raises(ValueError):
        with run_envelope("test-falha") as env:
            env.add_processed(1)
            raise ValueError("erro proposital")
