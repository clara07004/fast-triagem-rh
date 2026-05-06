# fast-triagem-rh

Automação de triagem de candidatos com IA para o time de Recrutamento & Seleção da Fast Sistemas Construtivos.

Coleta CVs de múltiplas plataformas (PandaPé, Indeed, Catho, Engenha, LinkedIn), analisa automaticamente com a Claude API contra os critérios de cada vaga e gera uma planilha ranqueada com os melhores candidatos — liberando a Karina para focar na decisão humana, não na leitura braçal de currículos.

## Stack

- Python 3.11+
- Claude API (Anthropic) — análise e ranqueamento de CVs
- pdfplumber + python-docx — extração de texto de PDF e Word
- gspread / openpyxl — escrita na planilha do time
- Pydantic — validação de critérios e respostas da IA
- Loguru — logging estruturado
- httpx + Tenacity — HTTP com retry

## Setup

```bash
make install
cp .env.example .env
# editar .env com ANTHROPIC_API_KEY e credenciais do Google Sheets
```

## Uso

```bash
# Triagem de uma vaga
python -m fast_triagem_rh --vaga criterios.yaml --cvs pasta/cvs/

# Onde:
# criterios.yaml — arquivo com os critérios da vaga (ver exemplo em docs/)
# pasta/cvs/     — pasta com PDFs/Word + exportação do PandaPé
```

## Comandos de desenvolvimento

```bash
make run        # executa a automação
make test       # roda testes
make lint       # roda lint
make format     # formata código
```

## Estrutura

```
src/fast_triagem_rh/
├── __init__.py
├── __main__.py         # ponto de entrada CLI
├── pipeline.py         # orquestrador principal
├── analyzer.py         # integração Claude API
├── parsers/
│   ├── pdf.py          # extração de PDF
│   ├── docx.py         # extração de Word
│   └── pandape.py      # leitura de exportação PandaPé
├── output/
│   └── sheets.py       # escrita na planilha
├── logger.py           # logger estruturado
└── envelope.py         # envelope de execução

tests/
└── test_smoke.py
```

## Variáveis de ambiente

| Variável | O que é |
|---|---|
| `ANTHROPIC_API_KEY` | Chave da Claude API |
| `GOOGLE_SHEETS_CREDENTIALS` | Path para credenciais Google (JSON) |
| `GOOGLE_SHEETS_ID` | ID da planilha de triagem |
| `ENVIRONMENT` | development / staging / production |
| `LOG_LEVEL` | DEBUG / INFO / WARNING / ERROR |

## Documentação

- [PROJECT_BRIEF.md](PROJECT_BRIEF.md) — contexto e critérios de aceite do MVP
- [PROCESS_MAP.md](PROCESS_MAP.md) — processo atual vs automatizado
- [SOLUTION_DESIGN.md](SOLUTION_DESIGN.md) — arquitetura técnica
- [TASKS.md](TASKS.md) — backlog e progresso
