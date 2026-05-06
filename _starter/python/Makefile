.PHONY: help install lint format test run clean

help:  ## Lista os comandos disponíveis
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Instala dependências e pre-commit
	python -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install -e ".[dev]"
	. .venv/bin/activate && pre-commit install --hook-type commit-msg --hook-type pre-commit

lint:  ## Roda lint (ruff + mypy)
	ruff check src tests
	mypy src

format:  ## Formata o código (ruff format)
	ruff format src tests
	ruff check --fix src tests

test:  ## Roda testes
	pytest

run:  ## Executa a automação (ajuste se precisar)
	python -m PROJECT_NAME_PLACEHOLDER

clean:  ## Remove arquivos temporários e caches
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
