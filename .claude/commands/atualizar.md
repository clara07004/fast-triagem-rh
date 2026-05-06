---
name: atualizar
description: >
  Varre o estado atual do projeto e atualiza os arquivos de contexto que ficaram
  desatualizados. Compara o que existe no código e nas pastas com o que está
  documentado em CLAUDE.md, _contexto/, README.md e RUNBOOK.md.
  Use quando o usuário chamar /atualizar, ou disser "atualiza o contexto",
  "os arquivos tão desatualizados", "sincroniza a memória".
---

# /atualizar — Manutenção de Contexto

## O que fazer

Varredura comparando o **estado real do projeto** com o que está **documentado nos arquivos de contexto**. Identificar diferenças e propor atualizações pro usuário aprovar.

## Passo 1 — Levantar o estado real

Ler e anotar:

1. **Estrutura de pastas** — ignorar `.git`, `node_modules`, `__pycache__`, `.venv`, `dist`.
2. **Stack** — detectar via `pyproject.toml`/`requirements.txt` (Python) ou `package.json` (Node).
3. **Dependências instaladas** — listar as principais (não todas).
4. **Skills e comandos locais** — `.claude/commands/*.md` e `.claude/skills/*/`.
5. **Arquivos recentes** — `git diff --name-only HEAD~5..HEAD` (ou menos commits se não houver).
6. **Mudanças não commitadas** — `git status`.
7. **Existência de RUNBOOK.md** — sinaliza se está em produção.
8. **Existência de ADRs** — `ADR/` ou `docs/ADR/`.

## Passo 2 — Ler os arquivos de contexto

1. `CLAUDE.md` — estrutura, stack, integrações, restrições.
2. `_contexto/empresa.md` — contexto Fast geral.
3. `_contexto/padroes.md` — preferências e padrões.
4. `README.md` — descrição pública e instruções de uso.
5. `RUNBOOK.md` (se existir) — operação em produção.
6. `SOLUTION_DESIGN.md` (se existir) — arquitetura documentada.

## Passo 3 — Comparar e identificar gaps

### CLAUDE.md
- Stack listada bate com `pyproject.toml`/`package.json`?
- Integrações mencionadas estão de fato implementadas?
- Restrições continuam válidas?

### README.md
- Instruções de "como rodar" funcionam de fato?
- `.env.example` lista todas as variáveis usadas no código?
- Dependências mencionadas batem com o lockfile?

### RUNBOOK.md
- Comandos de operação ainda funcionam?
- Contatos/responsáveis ainda corretos?
- Procedimentos de emergência atualizados?

### SOLUTION_DESIGN.md
- Arquitetura documentada bate com a implementada?
- Decisões importantes estão registradas em ADR?

## Passo 4 — Apresentar diagnóstico

Formato:

```
## Diagnóstico de contexto

### Em dia
- [lista do que está atualizado]

### Desatualizado
- **[arquivo]:** [o que está errado e o que deveria ser]

### Não documentado
- [coisas que existem no código mas não estão em nenhum doc]
```

Se tudo estiver em dia: "Tudo atualizado. Os arquivos refletem o estado atual do projeto."

## Passo 5 — Aplicar correções (com aprovação)

Pra cada item desatualizado, mostrar a mudança proposta e perguntar se aplica.
Se sim, aplicar todas de uma vez. Mostrar resumo.

## Regras

- Nunca reformatar arquivo inteiro. Só editar linhas relevantes.
- Se não tem certeza se algo mudou, perguntar em vez de assumir.
- Não inventar informação. Se não consegue inferir do código, perguntar.
- Tom direto. Não exagerar diagnóstico de coisas triviais.
- Se o projeto acabou de ser inicializado (poucos commits, sem RUNBOOK), dizer que está tudo certo e não forçar atualizações.
