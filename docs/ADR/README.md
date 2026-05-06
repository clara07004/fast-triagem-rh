# Architecture Decision Records (ADR)

Pasta com decisões arquiteturais importantes do projeto.

## O que é um ADR

Documento curto que registra **uma decisão técnica não-trivial**: o que foi decidido, por que, quais alternativas foram consideradas, e quais consequências esperadas.

## Quando criar um ADR

- Escolha de stack ou framework principal
- Decisão de NÃO usar algo que parecia óbvio
- Trade-off entre alternativas (segurança vs performance, custo vs flexibilidade)
- Padrão arquitetural adotado (event-driven, RAG, polling vs webhook)
- Mudança grande de direção em projeto existente

**Quando NÃO criar:** decisões triviais (qual nome de variável, ordem de funções), bugs, ajustes de configuração.

## Formato

Numeração sequencial: `001-titulo-curto.md`, `002-...`. **Nunca renumerar.** Se um ADR for substituído, criar um novo que aponta pra ele e marcar o original como `Superseded`.

Use `000-template.md` como base.

## Status possíveis

- **Proposed** — em discussão
- **Accepted** — decisão tomada e em vigor
- **Deprecated** — não recomendado mais, mas ainda em uso
- **Superseded by ADR-XXX** — substituído por outro ADR

## Índice

Atualizar conforme criar novos ADRs:

| # | Título | Status | Data |
|---|---|---|---|
| 001 | [Título] | Accepted | YYYY-MM-DD |
