---
name: syncar
description: >
  Sincroniza o projeto com o GitHub: mostra o que mudou, faz commit com
  mensagem em Conventional Commits e faz push para origin/main.
  Use quando quiser salvar e publicar o estado atual do projeto.
---

# /syncar — Sincronizar com GitHub

## O que fazer

1. Rodar `git status` para ver arquivos modificados, novos e deletados.
2. Rodar `git diff --stat HEAD` para ter dimensão do que mudou.
3. Apresentar resumo do que será commitado — máximo 5 linhas.
4. **Avisar e pular** qualquer arquivo que possa conter segredos: `.env`, `*.key`, `*credentials*`, `*secret*`.
5. Se o usuário não passou mensagem de commit, inferir uma a partir do diff seguindo Conventional Commits (ver abaixo).
6. Rodar `git add` nos arquivos relevantes (nunca `git add -A` sem revisar).
7. Criar o commit.
8. Rodar `git push origin main`.
9. Confirmar: "Sincronizado. Commit: `<hash curto>` — `<mensagem>`."

## Conventional Commits

Prefixos usados nesse projeto:

| Prefixo | Quando usar |
|---|---|
| `feat:` | Nova funcionalidade |
| `fix:` | Correção de bug |
| `docs:` | Mudança só em documentação |
| `chore:` | Setup, dependências, config |
| `refactor:` | Refatoração sem mudança de comportamento |
| `test:` | Adição ou correção de testes |

Exemplos:
- `docs: adiciona BACKLOG_PROJETO e CRONOGRAMA_SEMANAL`
- `feat: implementa parser de PDF com pdfplumber`
- `chore: adiciona dependências anthropic e openpyxl`

## Comportamento

- Se não houver nada para commitar, avisar: "Nada a sincronizar — working tree limpa."
- Se o remote não estiver configurado, avisar: "Remote origin não encontrado. Configure com `git remote add origin <url>` e tente novamente."
- Se o push falhar por divergência (remote à frente), avisar e **não** forçar: "O remote tem commits que você não tem localmente. Rode `git pull --rebase origin main` e depois `/syncar` novamente."
- Nunca usar `--force` ou `--no-verify`.
- Nunca commitar `.env` ou arquivos de credenciais.

## Quando usar

- Ao final de uma sessão de trabalho com mudanças relevantes.
- Antes de compartilhar o projeto com alguém.
- Após gerar documentação com `/novo-projeto`, `/planejar-automacao` ou `/gerar-tarefas`.
