# fast-template-automacao

Template-base para novos projetos de automação interna na **Fast Sistemas Construtivos**.

Padroniza estrutura de pastas, ferramentas, documentação e fluxo de trabalho — pra cada automação nova nascer já organizada e profissional.

---

## Como usar

### 1. Criar repositório novo a partir desse template

No GitHub, clica em **Use this template** → **Create a new repository**.
Nomeia algo como `fast-<nome-da-automacao>` (privado).

### 2. Clonar localmente

```bash
git clone git@github.com:<seu-usuario>/fast-<nome-da-automacao>.git
cd fast-<nome-da-automacao>
```

### 3. Inicializar o projeto

```bash
# Linux/Mac:
./init.sh

# Windows (PowerShell):
.\init.ps1
```

O script vai te perguntar:
- Nome do projeto
- Stack (Python ou Node)
- Descrição curta

E vai:
- Mover o starter da stack escolhida pra raiz
- Atualizar `pyproject.toml`/`package.json` com o nome certo
- Gerar README do projeto
- Configurar pre-commit hooks
- Fazer o primeiro commit estruturado

### 4. Estruturar com Claude Code

Abre o VS Code, roda `claude` no terminal, e chama:

```
/novo-projeto
```

Isso te entrevista pra preencher CLAUDE.md, PROJECT_BRIEF.md, etc.

### 5. Continuar com o fluxo padrão

```
/planejar-automacao    # arquitetura
/gerar-tarefas         # backlog
# implementa
```

---

## O que vem no template

```
fast-template-automacao/
├── _contexto/                  # memória compartilhada (empresa + padrões)
├── _starter/
│   ├── python/                 # starter Python (uv, ruff, pytest)
│   └── node/                   # starter Node (ESM, eslint, vitest)
├── docs/                       # templates de PROJECT_BRIEF, RUNBOOK, ADR, etc
├── .claude/                    # comandos e skills do Claude Code
├── .github/                    # CI, templates de issue/PR
├── init.sh                     # bootstrap interativo (Linux/Mac)
├── init.ps1                    # bootstrap interativo (Windows)
├── .pre-commit-config.yaml     # gitleaks, lint, conventional commits
├── CLAUDE.md
├── CONTRIBUTING.md
├── SECURITY.md
└── .env.example
```

---

## Princípios

- **Clareza sobre esperteza.** Código de automação é lido por muitas pessoas no decorrer do tempo.
- **Falha visível, nunca silenciosa.** Logs estruturados e envelope de execução.
- **Segredos nunca no código.** `.env` local + gerenciador de secrets em produção.
- **Convenção sobre configuração.** Quanto menos decidir caso a caso, melhor.
- **Documentação operacional obrigatória antes de produção.** RUNBOOK preenchido = critério de release.

---

## Manutenção do template

Quando esse template evoluir, novos projetos a partir daqui pegam o estado atual. Projetos antigos **não** recebem atualização automática — quando uma melhoria for crítica, é caso a caso.

Pra abstrações que devem se propagar entre todos os projetos (logger, retry, integração com APIs Fast), usar a biblioteca compartilhada `fast-utils` (a ser criada na Fase 3 da reestruturação).

---

## Dúvidas

Esse template é mantido por Clara Barbosa. Veja `CONTRIBUTING.md` pra contribuir.
