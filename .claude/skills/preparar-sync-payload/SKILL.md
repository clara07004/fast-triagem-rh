---
name: preparar-sync-payload
description: >
  Chamada por /gerar-tarefas (Etapa 4). Monta o bloco SYNC_PAYLOAD em JSON estruturado
  a partir do BACKLOG_PROJETO.md e CRONOGRAMA_SEMANAL.md. Pode ser consumido por
  uma automação separada de sincronização com Notion ou outra ferramenta de tasks.
---

# preparar-sync-payload

## Chamada por

`/gerar-tarefas` — Etapa 4

## Missão

Recebe o `BACKLOG_PROJETO.md` e o `CRONOGRAMA_SEMANAL.md` gerados pelo comando `/gerar-tarefas` e monta o bloco `SYNC_PAYLOAD` em JSON. O usuário pode usar esse JSON com uma automação externa de sync, ou copiar manualmente.

---

## Estrutura do SYNC_PAYLOAD

Todos os campos são obrigatórios:

```json
{
  "project_name": "nome-do-projeto",
  "stack": "python|node",
  "tasks": [
    {
      "name": "Nome da tarefa",
      "description": "O que precisa ser feito",
      "priority": "P1",
      "phase": "MVP",
      "estimated_hours": 3,
      "dependencies": ["nome-de-outra-tarefa"]
    }
  ],
  "weekly_schedule": [
    {
      "phase": "MVP",
      "goal": "Fluxo básico funcionando ponta a ponta",
      "tasks": ["Nome da tarefa"]
    }
  ],
  "future_improvements": [
    { "idea": "Dashboard de monitoramento", "impact": "Médio", "effort": "Alto" }
  ],
  "estimated_total_hours": 28
}
```

---

## Retorno

Retornar o bloco `SYNC_PAYLOAD` formatado em markdown com bloco de código JSON. Confirmar pro comando pai que o payload está pronto pra ser consumido.
