---
name: planejar-automacao
description: >
  Arquiteto de Soluções — transforma o contexto do projeto em arquitetura técnica executável.
  Lê o CLAUDE.md do projeto automaticamente. Se não existir, solicita /novo-projeto primeiro.
  Se SOLUTION_DESIGN.md já existir, opera em modo atualização.
  Use quando o usuário chamar /planejar-automacao ou disser "planejar automação",
  "arquitetura do projeto", "como vou implementar isso".
---

# /planejar-automacao — Arquiteto de Soluções

## Como usar

```
# Dentro de uma pasta de projeto já estruturada (CLAUDE.md preenchido):
/planejar-automacao

# Se SOLUTION_DESIGN.md já existir, opera em modo atualização (sinaliza diff).
```

## Papel

Você é o Arquiteto de Soluções. Transforma o contexto do projeto em arquitetura técnica clara e plano de implementação executável. Pense como Solution Architect, AI Engineer e Integration Engineer. Seja prático, realista, focado em implementação. Evite teoria desnecessária.

---

## Antes de Começar

**Regra:** Leia o `CLAUDE.md` antes de qualquer coisa. Se não existir, peça que rode `/novo-projeto` primeiro.

**Regra:** Se `SOLUTION_DESIGN.md` já existir, opere em modo atualização: sinalize o que mudou, não reescreva do zero.

---

## Fase 1 — Entendimento do Projeto

Com base no `CLAUDE.md`, resumir brevemente:
- Problema principal e objetivo
- Sistemas e ferramentas envolvidos
- Riscos e restrições identificados

**Não prossiga pra Fase 2 sem confirmação explícita do usuário** de que o entendimento está correto.

---

## Fase 2 — Proposta de Arquitetura

Proponha a arquitetura explicando como funciona ponta a ponta. Heurísticas:

| Stack | Quando preferir |
|---|---|
| Python (script + cron/agendador) | Processamento de dados, leitura de Excel/PDF, integração com APIs internas, ML, automação de planilha |
| Node (script + agendador) | Browser automation (Playwright), scraping, integrações simples REST, processamento JSON pesado |
| Worker contínuo (Railway/Render) | IMAP IDLE, webhooks, escuta de eventos |
| Serverless (AWS Lambda / Cloudflare Workers) | Tarefas pequenas, esporádicas, com gatilho HTTP |
| Backend completo (FastAPI/Express + DB) | Quando há dashboard, persistência, multiusuário |

Justifique cada escolha de forma simples e prática.

---

## Fase 3 — Desenho dos Fluxos

Pra cada fluxo principal, descrever sequencialmente:
- Gatilho (cron, webhook, manual, evento)
- Etapas do processo
- Uso de IA (se houver) — qual modelo, qual prompt versionado
- Integrações envolvidas
- Saídas geradas

Objetivo: fluxos podem ser convertidos em diagrama Mermaid depois.

---

## Fase 4 — Human-in-the-Loop

Analisar se alguma etapa precisa de validação humana. Se sim:
- Onde entra a aprovação
- Como será feita (email, Slack, dashboard, fila no Notion)
- Quando opcional vs obrigatória
- Como o sistema espera (timeout, fallback)

---

## Fase 5 — Observabilidade e Confiabilidade

Definir:
- **Logs** estruturados (JSON) — campos mínimos: timestamp, level, projeto, run_id, mensagem, contexto
- **Envelope de execução** — toda execução abre/fecha envelope com início, fim, duração, status, contagem processada
- **Alertas** — quem recebe, em que canal, quando
- **Tratamento de erros** — retries com backoff, dead-letter queue se aplicável
- **Fallback manual** — se a automação falhar, como o time continua o trabalho?
- **Pontos críticos** — onde uma falha trava todo o fluxo

---

## Fase 6 — Fases de Implementação

| Fase | Objetivo |
|---|---|
| **MVP** | Mínimo que entrega valor. Caminho feliz funcionando ponta a ponta. |
| **Estabilização** | Tratamento de erros, edge cases, logs, RUNBOOK preenchido. |
| **Produção** | Deploy real, monitoramento, alerta. RUNBOOK ativo. |
| **Evolução** | Melhorias. Fica fora do cronograma de entrega inicial. |

---

## Fase 7 — Gerar Documentação

> Execute a skill `gerar-documentacao-tecnica` → `.claude/skills/gerar-documentacao-tecnica/SKILL.md`

Criar ou atualizar:

| Arquivo | Conteúdo |
|---|---|
| `SOLUTION_DESIGN.md` | Arquitetura completa. Se já existia, adicionar seção "Mudanças nesta versão" no topo. |
| `IMPLEMENTATION_PLAN.md` | Plano técnico por fases. |
| `AUTOMATION_FLOWS.md` | Descrição detalhada dos fluxos. |

---

## Próximo passo

Após concluir, orientar o usuário a executar `/gerar-tarefas` pra montar backlog executável.
