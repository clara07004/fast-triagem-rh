# Contributing — Padrões de Trabalho

Este documento define como trabalhar nos projetos de automação interna da Fast. Vale pra você (Clara), e pra qualquer pessoa que entre no projeto depois.

---

## Antes de codar

1. **Entenda o problema antes de propor solução.** Se ambíguo, pergunte o essencial. Não invente requisito.
2. **Confirme a stack.** Cada projeto é Python OU Node. Os padrões abaixo se aplicam à sua stack.
3. **Verifique se já existe.** Antes de criar do zero, procure no template, em outros projetos Fast, e na biblioteca compartilhada `fast-utils` (quando disponível).

---

## Ao escrever código

### Geral

- Clareza sobre esperteza. Código de automação é lido por muitas pessoas no decorrer do tempo.
- Funções pequenas e testáveis.
- Tratamento de erros explícito. Nunca falhar em silêncio.
- Logs estruturados, mensagens informativas.
- Variáveis sensíveis sempre via `.env` ou secret manager — nunca hardcoded. Inclua `.env.example` quando criar variável nova.
- Comentários só onde agregam: explique o **porquê**, não o **o quê**.

### Python

- PEP 8 (validado por `ruff`).
- Type hints em funções públicas.
- `pathlib` em vez de `os.path`.
- `loguru` ou `structlog` pra logging.
- Testes com `pytest`.
- Formatação com `ruff format`.

### Node

- Module type ESM (`"type": "module"`).
- `async/await`, não callbacks.
- `pino` pra logging estruturado.
- `package.json` enxuto.
- Testes com `vitest` ou `node:test`.
- Lint com ESLint (flat config), formato Prettier.

---

## Convenção de commits

**Conventional Commits** — formato `<tipo>(escopo opcional): mensagem curta`.

Tipos:

| Tipo | Quando usar |
|---|---|
| `feat:` | Nova funcionalidade |
| `fix:` | Correção de bug |
| `docs:` | Mudança em documentação |
| `refactor:` | Refatoração sem mudar comportamento |
| `chore:` | Manutenção (deps, configs, infra) |
| `test:` | Adicionar ou ajustar testes |
| `ci:` | Mudanças em CI/CD |
| `perf:` | Melhoria de performance |
| `build:` | Mudança no sistema de build |

Mensagens curtas, descritivas, em português. Detalhes no corpo do commit se precisar.

Exemplos:

```
feat(triagem): adiciona regra de classificação por remetente
fix: corrige loop infinito em retry de API
docs: atualiza RUNBOOK com procedimento de rotação de credenciais
chore(deps): atualiza loguru pra 0.7.3
```

O hook de pre-commit (configurado em `.pre-commit-config.yaml`) **valida o formato da mensagem automaticamente**.

---

## Convenção de branches

| Prefixo | Quando usar |
|---|---|
| `feature/<nome-curto>` | Nova funcionalidade |
| `fix/<nome-curto>` | Correção |
| `docs/<nome-curto>` | Só documentação |
| `chore/<nome-curto>` | Manutenção |
| `refactor/<nome-curto>` | Refatoração |

Nomes em kebab-case, curtos e descritivos. Ex: `feature/classificador-prioridade-alta`.

---

## Pull Requests

Mesmo trabalhando solo, **abra PR pra mudanças não-triviais**. Você se força a revisar o que fez antes de mergear na main.

PR deve ter:
- **O que mudou** — em 2-3 linhas
- **Por quê** — qual problema resolve
- **Como testar** — passos pra quem revisa (ou pra você daqui a 3 meses)

O template de PR (`.github/PULL_REQUEST_TEMPLATE.md`) já força isso.

---

## Documentação obrigatória

| Arquivo | Obrigatório quando |
|---|---|
| `README.md` | Sempre — instruções de uso |
| `CLAUDE.md` | Sempre — contexto pro Claude Code |
| `.env.example` | Sempre que houver variável sensível |
| `PROJECT_BRIEF.md` | Após `/novo-projeto` |
| `SOLUTION_DESIGN.md` | Após `/planejar-automacao` |
| `RUNBOOK.md` | **Antes** de entrar em produção |
| `ADR/<numero>-<decisao>.md` | Pra toda decisão arquitetural não-trivial |
| `POSTMORTEM-<data>.md` | Pra todo incidente em produção |

---

## Setup inicial (depois de `init.sh`/`init.ps1`)

### Python
```bash
python -m venv .venv
source .venv/bin/activate           # Linux/Mac
# .\.venv\Scripts\Activate.ps1     # Windows

pip install -e ".[dev]"
pre-commit install --hook-type commit-msg --hook-type pre-commit
cp .env.example .env  # editar com credenciais
```

### Node
```bash
npm install
npx pre-commit install --hook-type commit-msg --hook-type pre-commit
cp .env.example .env  # editar com credenciais
```

---

## O que evitar

- Bibliotecas obscuras ou abandonadas quando há alternativa estável.
- Soluções "mágicas" que ninguém vai conseguir manter depois.
- Reescrever do zero quando a biblioteca compartilhada (`fast-utils`) já resolve.
- Concordar só por concordar. Se algo está errado, fala.
- Commit gigante misturando feat + fix + refactor + docs. Quebra em commits menores.

---

## Em caso de dúvida

Pergunta antes de assumir. Vale mais ajustar uma decisão antes do código que retrabalhar depois.
