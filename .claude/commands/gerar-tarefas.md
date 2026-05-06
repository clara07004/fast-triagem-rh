---
name: gerar-tarefas
description: >
  Gerador de Backlog — transforma o plano técnico em backlog executável.
  Lê os arquivos do projeto após /planejar-automacao ter sido executado.
  Gera BACKLOG_PROJETO.md e CRONOGRAMA_SEMANAL.md. Se houver conector Notion configurado,
  prepara payload pra sincronização.
  Use quando o usuário chamar /gerar-tarefas ou disser "gerar backlog", "criar tarefas",
  "montar cronograma do projeto".
---

# /gerar-tarefas — Backlog e Cronograma

## Como usar

```
# Após /planejar-automacao ter sido executado:
/gerar-tarefas
```

## Contexto que o Comando Deve Usar

Ler antes de gerar. Se algum arquivo não existir, sinalizar e prosseguir com o que tiver:

- `CLAUDE.md`
- `SOLUTION_DESIGN.md`
- `AUTOMATION_FLOWS.md`
- `IMPLEMENTATION_PLAN.md`
- Qualquer outro `.md` relevante no projeto

---

## Etapa 1 — Gerar BACKLOG_PROJETO.md

Quebrar o projeto em tarefas técnicas reais. Cada tarefa deve conter:

| Campo | Descrição |
|---|---|
| **Nome** | Nome claro e objetivo. |
| **Descrição** | O que precisa ser feito, executável. |
| **Prioridade** | P1 = bloqueia o projeto · P2 = importante mas não bloqueante · P3 = melhorias/otimizações |
| **Horas** | Estimativa realista. Honesta, não otimista. |
| **Dependências** | Outras tarefas que precisam estar prontas antes. |
| **Fase** | MVP · Estabilização · Produção · Evolução |

---

## Etapa 2 — Gerar CRONOGRAMA_SEMANAL.md

Converter o backlog em plano de execução semanal:
- Distribuição respeitando dependências e prioridades
- Máximo recomendado: 6h de foco produtivo por dia
- Fase **Evolução** fica fora do cronograma de entrega

Cada fase deve ter:
- Nome
- Objetivo
- Lista de tarefas com horas estimadas e prioridade

---

## Etapa 3 — Backlog de Evolução

Critério: vai pra Evolução qualquer tarefa que não seja bloqueante para MVP nem pra estabilização.

Inclui:
- Otimizações
- Melhorias de monitoramento
- Escalabilidade
- Novas features
- UX/dashboard

> Tarefas de Evolução **não** entram no cronograma semanal.

---

## Etapa 4 — Sincronização com Notion (se aplicável)

Se o conector Notion estiver configurado nesse projeto (verificar via `claude mcp list`):

> Execute a skill `preparar-sync-payload` → `.claude/skills/preparar-sync-payload/SKILL.md`

A skill gera bloco `SYNC_PAYLOAD` em JSON estruturado. O usuário pode então copiar pro Notion ou usar uma automação separada de sincronização.

Se o conector **não** estiver configurado, pular essa etapa silenciosamente. Não tentar instalar.

---

## Encerramento

Ao finalizar, exibir:

> "Backlog e cronograma gerados em `BACKLOG_PROJETO.md` e `CRONOGRAMA_SEMANAL.md`.
> Próximo passo: começar pela primeira tarefa P1 da Fase MVP."

Se gerou `SYNC_PAYLOAD`, mencionar:

> "Payload pro Notion disponível abaixo — copia e cola no destino que você usa pra acompanhar tarefas."
