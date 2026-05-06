# CRONOGRAMA_SEMANAL — fast-triagem-rh

> Gerado em 2026-05-06. Prazo: 6 dias úteis. Carga: ~5h de foco produtivo/dia.
> ⚠️ T07 (Parser PandaPé) depende de receber o arquivo de exportação — pode deslocar para Dia 3 se arquivo chegar tarde.

---

## Fase MVP — Dias 1 a 5

**Objetivo:** pipeline completo funcionando ponta a ponta.

---

### Dia 1 — Setup e base (5h)

| Tarefa | Horas | Prioridade |
|---|---|---|
| T01 — Setup de dependências | 0.5h | P1 |
| T02 — Modelos Pydantic | 1h | P1 |
| T03 — Template Excel de critérios | 0.5h | P1 |
| T04 — Parser de critérios | 1h | P1 |
| T05 — Parser PDF | 2h | P1 |

**Saída do dia:** parsers de PDF e critérios funcionando, modelos definidos.

---

### Dia 2 — Parsers restantes + IA (5.5h)

| Tarefa | Horas | Prioridade |
|---|---|---|
| T06 — Parser Word | 1.5h | P1 |
| T07 — Parser PandaPé ⚠️ | 2h | P1 |
| T08 — Analyzer (Claude API) | 2h | P1 |

> Se arquivo PandaPé ainda não chegou: implementar T08 e deixar T07 para o Dia 3 assim que o arquivo chegar.

**Saída do dia:** todos os parsers prontos, chamada à Claude API funcionando com CV de teste.

---

### Dia 3 — Output e orquestrador (5h)

| Tarefa | Horas | Prioridade |
|---|---|---|
| T09 — Output Excel | 2h | P1 |
| T10 — Pipeline orquestrador | 2.5h | P1 |
| T07 — Parser PandaPé (se pendente) | 0.5h buffer | P1 |

**Saída do dia:** pipeline completo do início ao fim, sem CLI ainda. Planilha gerada a partir de um lote de CVs de teste.

---

### Dia 4 — CLI e tratamento de erros (2.5h + buffer)

| Tarefa | Horas | Prioridade |
|---|---|---|
| T11 — CLI | 1h | P1 |
| Buffer para ajustes no pipeline | 1.5h | — |

> Dia mais leve intencionalmente — absorve atrasos acumulados e permite ajustes finos no pipeline antes do teste real.

**Saída do dia:** `python -m fast_triagem_rh --vaga criterios.xlsx --cvs pasta/` funcionando.

---

### Dia 5 — Teste real e ajustes (4h)

| Tarefa | Horas | Prioridade |
|---|---|---|
| T12 — Teste ponta a ponta com dados reais | 3h | P1 |
| Ajustes de prompt / colunas pós-teste | 1h | P1 |

**Saída do dia:** pipeline validado com CVs reais. Planilha revisada por Karina. MVP concluído.

---

## Fase Estabilização — Dia 6

**Objetivo:** edge cases tratados, Karina treinada, RUNBOOK preenchido.

---

### Dia 6 — Estabilização e entrega (5h)

| Tarefa | Horas | Prioridade |
|---|---|---|
| T13 — CVs problemáticos (edge cases) | 2h | P2 |
| T14 — Ajuste fino do prompt (se necessário) | 0.5h | P2 |
| T15 — RUNBOOK.md | 1h | P2 |
| T16 — Guia de uso para Karina | 1h | P2 |
| T17 — Treinamento com Karina | 1.5h | P2 |

> T14 pode ser pulado se o teste do Dia 5 não revelou problemas de classificação.

**Saída do dia:** Karina executa o fluxo completo sem ajuda. RUNBOOK preenchido. Projeto entregue.

---

## Fase Produção — Pós-entrega

**Sem prazo definido. Executar após validação em uso real (1–2 semanas após entrega).**

| Tarefa | Horas | Prioridade |
|---|---|---|
| T18 — Avaliação de deploy para Karina | 1h | P2 |
| T19 — Validação de custo da API | 0.5h | P2 |

---

## Fase Evolução — Fora do cronograma

> Priorizar com Karina após MVP validado em produção.

| Tarefa | Impacto | Esforço |
|---|---|---|
| EV01 — API direta PandaPé | Alto | Médio |
| EV02 — API Indeed, LinkedIn, Catho | Alto | Alto |
| EV03 — Perguntas de entrevista por candidato | Médio | Baixo |
| EV04 — LGPD: dados sensíveis | Alto | Alto |
| EV05 — Dashboard de volume | Médio | Alto |
| EV06 — Relatório automático para gestores | Médio | Médio |

---

## Visão geral da semana

```
Dia 1  [████████████████░░░░]  Setup + Modelos + Parsers PDF/Critérios    5h
Dia 2  [████████████████████]  Parsers Word + PandaPé + IA               5.5h
Dia 3  [████████████████████]  Output Excel + Pipeline                     5h
Dia 4  [██████████░░░░░░░░░░]  CLI + buffer de ajustes                   2.5h
Dia 5  [████████████████░░░░]  Teste real + ajustes                        4h
Dia 6  [████████████████████]  Edge cases + RUNBOOK + Treinamento          5h
                                                              Total MVP: 27h
```
