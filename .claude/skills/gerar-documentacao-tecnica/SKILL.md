---
name: gerar-documentacao-tecnica
description: >
  Chamada por /planejar-automacao (Fase 7). Recebe o output das fases anteriores
  e escreve (ou atualiza) os arquivos de documentação técnica do projeto:
  SOLUTION_DESIGN.md, IMPLEMENTATION_PLAN.md e AUTOMATION_FLOWS.md.
---

# gerar-documentacao-tecnica

## Chamada por

`/planejar-automacao` — Fase 7

## Missão

Recebe o output das Fases 1–6 do comando `/planejar-automacao` e escreve (ou atualiza) os arquivos de documentação técnica do projeto.

---

## Comportamento

**Regra:** Se o arquivo já existir, adicionar seção **"Mudanças nesta versão"** no topo com a data. Nunca sobrescrever histórico.

---

### SOLUTION_DESIGN.md

Conteúdo:
- Visão geral da solução
- Stack escolhida com justificativas
- Decisões de arquitetura (linkar pra ADR quando relevante)
- Integrações principais
- Pontos críticos (single point of failure, dependências externas)

Se já existia: preservar conteúdo anterior e adicionar seção nova com data.

---

### IMPLEMENTATION_PLAN.md

Conteúdo:
- Plano técnico dividido por fases: MVP → Estabilização → Produção → Evolução
- Objetivos claros e executáveis por fase
- Pré-requisitos pra começar (acessos, credenciais, dados de teste)

---

### AUTOMATION_FLOWS.md

Cada fluxo com:
- Nome
- Gatilho (cron, webhook, manual, evento)
- Etapas sequenciais
- Uso de IA (modelo, prompt versionado em `prompts/`)
- Integrações
- Saídas geradas
- Pontos de aprovação humana (se houver)

Formato que permita conversão futura em diagrama Mermaid.

---

## Retorno

Após escrever, retornar:
- Lista de arquivos criados
- Lista de arquivos atualizados
- Confirmação para o comando pai prosseguir
