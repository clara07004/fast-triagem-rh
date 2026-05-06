# Fast — Template de Automação Interna

> Esse arquivo é o ponto de entrada do contexto pro Claude Code. Quando você clonar esse template pra começar um projeto novo, **edite as seções marcadas com `[PREENCHER]`** ou rode `/novo-projeto` que faz isso por entrevista.

## Sobre esse repositório

Template-base padronizado pra novos projetos de automação interna na Fast Sistemas Construtivos. Cada novo projeto é criado a partir desse template (clone + `init.sh`), vira repositório próprio no GitHub e segue essas convenções.

**Este arquivo é o template — não edite aqui se quiser que mudanças se propaguem pra projetos.** Edições no template valem só pra projetos criados a partir daqui em diante.

## O que é esse projeto (preenchido após init)

[PREENCHER] — uma a duas linhas descrevendo o que essa automação faz e pra quem.

## Objetivo

[PREENCHER] — qual problema essa automação resolve e qual ganho concreto entrega (horas/semana economizadas, erros eliminados, escala viabilizada).

## Stack

[PREENCHER após escolha no `init.sh`] — Python ou Node + dependências principais.

## Integrações

[PREENCHER] — APIs internas Fast (SAP, Sults, Piperun, Nasajon, portal de orçamentos), serviços externos, MCPs configurados.

## Restrições

[PREENCHER] — restrições de segurança, LGPD, ferramentas obrigatórias/proibidas.

## Critérios de sucesso

[PREENCHER] — como saber que está funcionando bem (métricas, indicadores).

## Manutenção

Responsabilidade: Clara Barbosa. Cada projeto tem seu próprio `RUNBOOK.md` quando entra em produção.

---

## Contexto compartilhado

Antes de qualquer resposta, ler:

1. `_contexto/empresa.md` — quem é a Fast, contexto de negócio.
2. `_contexto/padroes.md` — tom de voz, padrões técnicos, regras de código.

Esses arquivos vêm do template e definem o piso comum de todos os projetos.

## Comandos disponíveis

| Comando | Quando usar |
|---|---|
| `/iniciar` | Início de cada sessão de trabalho |
| `/novo-projeto` | Logo após clonar o template, pra estruturar o projeto via entrevista |
| `/planejar-automacao` | Depois de `/novo-projeto`, pra definir arquitetura técnica |
| `/gerar-tarefas` | Depois de `/planejar-automacao`, pra montar backlog executável |
| `/atualizar` | Quando suspeitar que docs estão desalinhados do código |

## Padrão de trabalho

1. Toda automação nova começa por esse template.
2. Roda `./init.sh` (ou `init.ps1` no Windows) pra escolher stack (Python/Node) e gerar starter.
3. Roda `/novo-projeto` pra estruturar via entrevista — preenche CLAUDE.md, PROJECT_BRIEF, etc.
4. Roda `/planejar-automacao` pra arquitetura.
5. Roda `/gerar-tarefas` pra backlog.
6. Implementa, com commits em Conventional Commits (ver `CONTRIBUTING.md`).
7. Antes de produção: preenche `RUNBOOK.md`.
8. Em produção: registra incidentes em `POSTMORTEM.md` e decisões grandes em `ADR/`.

## Onde tudo vive

- `_contexto/` — memória compartilhada do template (empresa + padrões).
- `_starter/` — starters de stack (python e node). O `init.sh` move o escolhido pra raiz.
- `docs/` — templates de documentos do ciclo de vida do projeto.
- `.claude/` — comandos e skills do Claude Code.
- `.github/` — workflows de CI, templates de issue/PR.
- `CONTRIBUTING.md`, `SECURITY.md`, `.env.example`, `.pre-commit-config.yaml` — governança.

## Aprender com correções

Quando o usuário corrigir algo ou der instrução permanente ("prefiro assim", "evita...", "sempre que..."), perguntar:

> "Quer que eu salve isso pra não precisar repetir?"

Se sim:
- Sobre o negócio Fast → `_contexto/empresa.md`
- Sobre tom, estilo, padrões técnicos → `_contexto/padroes.md`
- Sobre regra específica desse projeto → esse `CLAUDE.md`

Não perguntar pra correções óbvias do contexto imediato.
