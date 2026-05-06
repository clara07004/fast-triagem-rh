# docs/

Templates dos documentos do ciclo de vida de cada projeto.

## Como usar

Quando um projeto novo precisa de um documento, copia o `.template.md` correspondente pra raiz do projeto e tira o `.template`:

```bash
cp docs/RUNBOOK.template.md ./RUNBOOK.md
```

Depois preenche.

## Documentos disponíveis

| Template | Quando usar |
|---|---|
| `PROJECT_BRIEF.template.md` | Após `/novo-projeto` |
| `SOLUTION_DESIGN.template.md` | Após `/planejar-automacao` |
| `IMPLEMENTATION_PLAN.template.md` | Após `/planejar-automacao` |
| `AUTOMATION_FLOWS.template.md` | Após `/planejar-automacao` |
| `RUNBOOK.template.md` | **Antes** de produção |
| `POSTMORTEM.template.md` | A cada incidente em produção |
| `ADR/000-template.md` | A cada decisão arquitetural não-trivial |
