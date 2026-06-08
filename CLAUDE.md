# Fast — Template de Automação Interna

> Esse arquivo é o ponto de entrada do contexto pro Claude Code. Quando você clonar esse template pra começar um projeto novo, **edite as seções marcadas com `[PREENCHER]`** ou rode `/novo-projeto` que faz isso por entrevista.

## Sobre esse projeto

Automação de triagem de candidatos para o time de Recrutamento & Seleção da Fast. Coleta CVs de múltiplas plataformas (PandaPé, Indeed, Catho, Engenha, LinkedIn), analisa automaticamente com IA contra os critérios de cada vaga e gera uma planilha ranqueada com os melhores candidatos, justificativas e pontos de atenção.

**Operadora:** Karina Salles, Coordenadora de R&S (não-técnica — interface deve ser simples).
**Mantenedora:** Clara Barbosa.

## Objetivo

Eliminar 3 a 5 horas semanais de triagem manual, reduzindo o tempo de entrega de perfis aos gestores e recuperando o SLA de 10 dias que hoje é sistematicamente ultrapassado.

## Stack

Python 3.11+ com API externa de IA (Claude). Dependências principais: pdfplumber, python-docx, openpyxl, httpx, pydantic, loguru.

## Integrações

| Sistema | Tipo | Observação |
|---|---|---|
| PandaPé | Exportação de dados | Plataforma principal — tem exportação estruturada |
| Indeed, Catho, Engenha, LinkedIn | Leitura de PDF/Word | CVs chegam como arquivos |
| Excel (openpyxl) | Escrita | Planilha de triagem `.xlsx` local que Karina abre e revisa |
| Claude API (Anthropic) | IA | Análise e ranqueamento de perfis |

## Restrições

- Interface de operação deve ser simples — Karina não é técnica. Karina informará os critérios de cada vaga como input estruturado (formato a definir).
- CVs geralmente não contêm dados sensíveis → API externa de IA permitida. Tratar dados sensíveis como evolução futura (LGPD).
- Human-in-the-loop obrigatório: Karina sempre revisa e pré-aprova antes de encaminhar perfis aos gestores.
- **Prazo:** 6 dias para MVP (qualidade prioritária sobre prazo).

## Critérios de sucesso

- Karina consegue rodar a triagem de uma vaga sem ajuda técnica.
- Planilha gerada tem candidatos ranqueados com: justificativa, contato, pontos positivos e negativos.
- Tempo de triagem por vaga reduz visivelmente (baseline a medir com Karina).
- SLA de 10 dias para entrega de perfis começa a ser cumprido.

## A confirmar com Karina

- Critérios base comuns a todas as vagas (ex: localização, tipo de contrato).
- Volume médio de vagas por semana e candidatos por vaga (sem dashboard hoje).

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
