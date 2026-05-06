# Segurança

## Tratamento de credenciais

### O que **nunca** fazer

- Hardcoded credenciais em código (token, senha, API key, string de conexão).
- Commitar arquivo `.env` ou qualquer arquivo com valor sensível real.
- Postar credenciais em chat, ticket, screenshot, ou comentário de PR.
- Compartilhar `.env` por email ou Drive sem necessidade.

### O que **sempre** fazer

- Usar `.env` local pra desenvolvimento. Nunca commitar.
- `.env.example` com **chaves vazias e descrição** de cada variável.
- Em produção, usar variáveis de ambiente do host (Render, Railway, Cloudflare) ou um gerenciador de segredos (1Password CLI, doppler, Bitwarden Secrets).
- Logs **mascaram** automaticamente campos sensíveis (já configurado no logger do starter — campos com `token`, `password`, `api_key`, `secret`, `authorization` viram `***`).
- Pre-commit hook **gitleaks** roda antes de cada commit detectando padrões de credenciais.
- CI roda **gitleaks** em cada PR (segunda camada).

## Dados sensíveis (LGPD)

Quando a automação processar dados pessoais (emails de pessoas, CPFs, dados de RH, dados de cliente):

- **Minimização:** processar só o necessário. Não persistir o que não precisa.
- **Retenção:** definir prazo claro pra apagar dados processados. Documentar em `SOLUTION_DESIGN.md` seção Segurança.
- **Anonimização:** quando armazenar pra log/auditoria, ofuscar o que não precisa ser identificável.
- **Acessos:** princípio do menor privilégio. Se uma automação só lê de um sistema, não dar permissão de escrita.

## Reportar vulnerabilidade

Se você (ou qualquer pessoa) encontrar uma vulnerabilidade de segurança nesse projeto, **não abra issue pública**. Reporte direto pra:

- **Clara Barbosa** — clara.barbosa@fastdrywall.com.br

Resposta esperada em até 5 dias úteis.

## Rotação de credenciais

- **Periódica:** todo segredo de produção deve ser rotacionado pelo menos a cada 6 meses.
- **Após exposição:** se houver suspeita de vazamento (ex: gitleaks pegou no PR), rotacionar imediatamente.

Procedimento de rotação fica no `RUNBOOK.md` de cada projeto.

## Auditoria

Em automações críticas (que mexem em dados financeiros, comunicação externa em nome da Fast, ou alterações em SAP/CRM), manter:

- **Log de execuções** — toda execução registra envelope completo
- **Log de aprovações** — quando há HITL, registrar quem aprovou e quando
- **Imutabilidade** — logs de produção não podem ser editados retroativamente
