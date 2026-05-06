# PROJECT_NAME_PLACEHOLDER

PROJECT_DESCRIPTION_PLACEHOLDER

## Stack

- Node.js 20+ (ESM)
- pino (logging estruturado)
- dotenv (variáveis de ambiente)
- Vitest (testes), ESLint + Prettier (lint/format)

## Setup

```bash
npm install
cp .env.example .env
# editar .env com suas credenciais
```

## Scripts

```bash
npm start        # executa a automação
npm run dev      # executa com --watch (recarrega ao salvar)
npm test         # roda testes
npm run lint     # roda lint
npm run format   # formata código
```

## Estrutura

```
src/
├── index.js      # ponto de entrada
├── logger.js     # logger estruturado (JSON em prod, pretty em dev)
└── envelope.js   # envelope de execução (rastreia toda run)

tests/
└── smoke.test.js
```

## Padrão de execução

Toda execução deve ser envolta em um envelope. Exemplo em `src/index.js`:

```javascript
import { runEnvelope } from './envelope.js';
import { getLogger } from './logger.js';

const log = getLogger('main');

await runEnvelope('nome-da-execucao', async (env) => {
  for (const item of await obterDados()) {
    try {
      await processar(item);
      env.addProcessed();
    } catch (err) {
      env.addFailed(err.message);
    }
  }
});
```

Isso garante:
- Logs de início e fim com `run_id` único
- Duração rastreada
- Contagem de processados / falhos
- Exception capturada com stack

## Variáveis de ambiente

Veja `.env.example`. Variáveis críticas:

| Variável | O que é |
|---|---|
| `PROJECT_NAME` | Identifica em logs |
| `ENVIRONMENT` | development / staging / production |
| `LOG_LEVEL` | trace / debug / info / warn / error |
| `LOG_FORMAT` | pretty (dev) / json (prod) |

## Próximos passos sugeridos

1. Definir as integrações reais em `src/integrations/`
2. Adicionar testes por módulo
3. Quando próximo de produção, preencher `RUNBOOK.md` na raiz
