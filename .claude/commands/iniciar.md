---
name: iniciar
description: >
  Carrega o contexto do projeto no início da sessão. Lê CLAUDE.md, _contexto/empresa.md
  e _contexto/padroes.md, mostra um resumo curto e pergunta o que vamos fazer.
  Use no começo de cada sessão de trabalho.
---

# /iniciar — Início da Sessão

## O que fazer

1. Ler `CLAUDE.md` na raiz do projeto.
2. Ler `_contexto/empresa.md` (contexto Fast).
3. Ler `_contexto/padroes.md` (preferências de comunicação e padrões técnicos).
4. Se existir, ler `RUNBOOK.md` da raiz (sinal de que está em produção).
5. Apresentar resumo curto e perguntar o que fazer.

## Formato do resumo

```
Contexto carregado.

**Projeto:** [nome — uma linha do CLAUDE.md]
**Stack:** [Python ou Node — detectado por pyproject.toml ou package.json]
**Status:** [se RUNBOOK.md existe → "em produção" | senão → "em desenvolvimento"]

O que vamos fazer hoje?
```

Máximo 5 linhas. Não listar tudo que foi lido.

## Comportamento

- Tom direto, sem boas-vindas formais.
- Não enumerar arquivos lidos.
- Se houver `TASKS.md` no projeto e tiver itens pendentes, mencionar os 3 primeiros.
- Se for a primeira sessão num projeto recém-clonado do template (sem `_contexto/empresa.md` preenchido), avisar: "Esse projeto parece ter acabado de sair do template. Roda `./init.sh` ou me chama com `/novo-projeto` pra estruturar."

## Quando usar

- Início de toda sessão nova de trabalho.
- Depois de ficar muitos dias sem mexer no projeto.
- Após mudanças grandes na documentação (testar se o resumo bate).
