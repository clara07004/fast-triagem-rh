# Padrões Técnicos e de Comunicação

## Tom de comunicação

- Português brasileiro, direto e objetivo. Sem rodeios.
- Sem linguagem corporativa genérica.
- Listas e estrutura quando ajudam clareza, não como padrão.
- Respostas curtas pra perguntas simples; aprofunda quando o tema pede.
- Não concordar só por concordar. Se algo está errado, falar.

## Antes de codar

- Entender o problema antes de propor solução. Se ambíguo, perguntar o essencial.
- Confirmar a stack antes de assumir (Python, Node, RPA?).
- Verificar se já existe algo parecido no template ou em outros projetos antes de criar do zero.

## Padrões de código (geral)

- Clareza sobre esperteza.
- Funções pequenas e testáveis.
- Tratamento de erros explícito. Nunca falhar em silêncio.
- Logs úteis e mensagens informativas. Logs estruturados (JSON) em produção.
- Variáveis sensíveis sempre via `.env` ou secret manager — nunca hardcoded.
- `.env.example` obrigatório quando criar projeto novo.
- Comentários só onde agregam: explicar o **porquê**, não o **o quê**.

## Padrões Python

- Seguir PEP 8 (validado por `ruff`).
- Type hints em funções públicas.
- `pathlib` em vez de `os.path`.
- `loguru` ou `structlog` pra logging estruturado.
- Gerenciar dependências com `uv` ou `pip` + `requirements.txt`.
- Testes com `pytest`.
- Formatação com `black` ou `ruff format`.

## Padrões Node

- Module type ESM (`"type": "module"` no package.json).
- `async/await`, não callbacks.
- `pino` pra logging estruturado.
- `package.json` enxuto — não instalar lib só por curiosidade.
- Testes com `vitest` ou `node:test`.
- Lint com `eslint` (flat config).

## Convenção de commits

Conventional Commits — `<tipo>(escopo opcional): mensagem curta`.

Tipos comuns:
- `feat:` nova funcionalidade
- `fix:` correção de bug
- `docs:` mudança em documentação
- `refactor:` refatoração sem mudar comportamento
- `chore:` manutenção (deps, configs)
- `test:` adicionar ou ajustar testes
- `ci:` mudanças em CI/CD

Mensagens em português, curtas e descritivas. Detalhes no corpo do commit se precisar.

## Convenção de branches

- `feature/<nome-curto>` — nova feature
- `fix/<nome-curto>` — correção
- `docs/<nome-curto>` — só documentação
- `chore/<nome-curto>` — manutenção

## Pull Requests

PR deve ter:
- O que mudou
- Por que
- Como testar

Sem essas três coisas, o revisor (futura Clara, ou outra pessoa) não tem contexto.

## Documentação obrigatória por projeto

| Arquivo | Obrigatório quando |
|---|---|
| `README.md` | Sempre |
| `CLAUDE.md` | Sempre |
| `.env.example` | Sempre que houver variável sensível |
| `PROJECT_BRIEF.md` | Após `/novo-projeto` |
| `SOLUTION_DESIGN.md` | Após `/planejar-automacao` |
| `RUNBOOK.md` | Antes de entrar em produção |
| `ADR/<numero>-<decisao>.md` | Pra toda decisão arquitetural não trivial |
| `POSTMORTEM-<data>.md` | Pra todo incidente em produção |

## O que evitar

- Bibliotecas obscuras ou abandonadas quando há alternativa estável.
- Soluções "mágicas" que ninguém vai conseguir manter depois.
- Reescrever do zero quando já existe biblioteca compartilhada (`fast-utils` — a criar).
- Concordar só por concordar.

---

*Esse arquivo vem do template e define os padrões compartilhados de todos os projetos da Fast. Pode ser ajustado por projeto se houver razão clara — registrar a exceção em ADR.*
