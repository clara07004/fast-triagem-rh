/**
 * Ponto de entrada da automação.
 *
 * Uso:
 *   npm start
 */

import 'dotenv/config';

import { runEnvelope } from './envelope.js';
import { getLogger } from './logger.js';

const log = getLogger('main');

async function main() {
  await runEnvelope('PROJECT_NAME_PLACEHOLDER-main', async (env) => {
    log.info('Iniciando automação');

    // === Sua lógica aqui ===
    // Exemplo:
    // for (const item of await obterDados()) {
    //   try {
    //     await processar(item);
    //     env.addProcessed();
    //   } catch (err) {
    //     env.addFailed(err.message);
    //   }
    // }

    log.info('Automação concluída');
  });
}

main().catch((err) => {
  log.fatal({ err }, 'Falha fatal — encerrando processo');
  process.exit(1);
});
