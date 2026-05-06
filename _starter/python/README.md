# PROJECT_NAME_PLACEHOLDER

PROJECT_DESCRIPTION_PLACEHOLDER

## Stack

- Python 3.11+
- Loguru (logging estruturado)
- httpx (HTTP), Tenacity (retry)
- Pydantic (validação)
- Pytest (testes), Ruff (lint/format), MyPy (types)

## Setup

```bash
make install
cp .env.example .env
# editar .env com suas credenciais
```

## Comandos

```bash
make run        # executa a automação
make test       # roda testes
make lint       # roda lint
make format     # formata código
```

## Estrutura

```
src/PROJECT_NAME_PLACEHOLDER/
├── __init__.py
├── __main__.py     # ponto de entrada (python -m PROJECT_NAME_PLACEHOLDER)
├── logger.py       # logger estruturado (JSON em prod, console em dev)
└── envelope.py     # envelope de execução (rastreia toda run)

tests/
└── test_smoke.py   # testes mínimos
```

## Padrão de execução

Toda execução deve ser envolta em um envelope. Exemplo em `__main__.py`:

```python
from PROJECT_NAME_PLACEHOLDER.envelope import run_envelope
from PROJECT_NAME_PLACEHOLDER.logger import get_logger

log = get_logger(__name__)

def main():
    with run_envelope("nome-da-execucao") as env:
        for item in obter_dados():
            try:
                processar(item)
                env.add_processed()
            except Exception as exc:
                env.add_failed(error=str(exc))
```

Isso garante:
- Logs de início e fim com `run_id` único
- Duração rastreada
- Contagem de processados / falhos
- Exception capturada com traceback

## Variáveis de ambiente

Veja `.env.example`. Variáveis críticas:

| Variável | O que é |
|---|---|
| `PROJECT_NAME` | Identifica em logs |
| `ENVIRONMENT` | development / staging / production |
| `LOG_LEVEL` | DEBUG / INFO / WARNING / ERROR |
| `LOG_FORMAT` | json (prod) / console (dev) |

Adicionar novas conforme integrações forem entrando.

## Próximos passos sugeridos

1. Definir as integrações reais em `src/PROJECT_NAME_PLACEHOLDER/integrations/`
2. Adicionar testes unitários por módulo
3. Quando próximo de produção, preencher `RUNBOOK.md` na raiz do projeto
