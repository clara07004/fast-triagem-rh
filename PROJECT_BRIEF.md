# PROJECT_BRIEF — fast-triagem-rh

> Resumo estruturado da entrevista de kickoff. Gerado em 2026-05-06.

## Identificação

- **Nome:** fast-triagem-rh
- **Área da Fast:** RH — Recrutamento & Seleção
- **Origem da demanda:** Iniciativa interna / sobrecarga operacional identificada
- **Solicitante:** Clara Barbosa (automação) / Karina Salles (operação)
- **Data de kickoff:** 2026-05-06

## O problema

Karina Salles, Coordenadora de R&S, realiza hoje a triagem de candidatos manualmente em 5 plataformas: PandaPé, Indeed, Catho, Engenha e LinkedIn. O processo exige abrir e analisar currículo por currículo, avaliar aderência aos critérios da vaga, e depois registrar status e justificativas em uma planilha compartilhada com o time.

Esse processo consome entre 3 e 5 horas semanais — volume que cresce conforme o número de vagas abertas aumenta. O SLA de entrega de perfis aos gestores é de 10 dias, e ele é sistematicamente ultrapassado. Não há dashboards ou indicadores que meçam o volume de candidatos por vaga; tudo está na cabeça da Karina e na planilha.

Os critérios de avaliação variam por vaga, o que impossibilita uma triagem padronizada sem contexto. Não há automação ou triagem prévia — todo candidato passa pelo olhar humano antes de ser descartado ou avançado.

## A solução proposta

Uma automação em Python que recebe como input os critérios de uma vaga (definidos pela Karina de forma simples, sem interface técnica) e os CVs dos candidatos (via exportação da PandaPé ou arquivos PDF/Word das demais plataformas). A IA (Claude API) lê cada currículo, avalia contra os critérios e retorna uma análise estruturada por candidato.

O resultado é gravado diretamente na planilha já usada pelo time, com colunas como: nome, contato, classificação (aprovado/reprovado/verificar), pontuação de aderência, pontos positivos, pontos negativos e justificativa da IA.

Karina mantém o controle total: ela revisa a planilha gerada e pré-aprova os perfis antes de encaminhar aos gestores. A automação não toma decisões finais — elimina o trabalho bruto de leitura e triagem inicial.

## Ganho esperado

| Métrica | Hoje | Esperado | Como medir |
|---|---|---|---|
| Tempo de triagem/semana | 3–5 horas | < 1 hora | Registro manual por Karina |
| SLA de entrega ao gestor | 10 dias (estourado) | ≤ 10 dias | Data abertura vs entrega |
| Candidatos triados por hora | ~X (a levantar) | 5–10x mais | Contagem por run |
| Erros/esquecimentos de candidato | Ocorre | Próximo de zero | Comparação de volume |

> Volume de vagas/semana e candidatos/vaga ainda não têm indicador — levantar com Karina na primeira reunião.

## Escopo

### Está incluído (MVP)
- Leitura de CVs em PDF e Word
- Exportação/importação via PandaPé
- Análise com IA usando critérios definidos por vaga
- Gravação dos resultados na planilha do time
- Interface de input simples pra Karina informar os critérios da vaga
- Human-in-the-loop: Karina revisa antes de enviar aos gestores

### Não está incluído (fora do MVP)
- API direta com Indeed, Catho, Engenha, LinkedIn (scraping ou integração)
- Tratamento de CVs com dados sensíveis (LGPD — evolução futura)
- Sugestão automática de perguntas de entrevista
- Relatórios automáticos para gestores
- Busca ativa de candidatos por vaga via API

## Premissas

- PandaPé continua oferecendo exportação estruturada de candidatos.
- CVs das demais plataformas chegam como arquivos PDF ou Word baixados manualmente (por enquanto).
- Karina terá disponibilidade para um treinamento de entrega (~1 hora).
- A planilha de triagem em Excel (`.xlsx` local) é o destino aceito pelo time — confirmado em `/planejar-automacao`.
- A Claude API tem latência e custo aceitáveis para o volume de CVs processados.

## Riscos identificados

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Critérios por vaga mal definidos levam a triagem ruim | Alta | Alto | Template de critérios + validação por Karina antes de rodar |
| PandaPé muda formato de exportação | Média | Médio | Parser tolerante + log de erros de parsing |
| CV em formato não suportado (imagem, escaneado) | Média | Baixo | Registrar como erro, pular com aviso |
| IA retorna classificação errada em casos limítrofes | Alta | Baixo | Human-in-the-loop obrigatório — Karina sempre revisa |
| Karina não adota por interface complexa | Média | Alto | Interface simples, treinamento na entrega |

## Stakeholders

- **Sponsor:** Clara Barbosa
- **Operação:** Karina Salles (Coordenadora de R&S) e time de R&S
- **Impactados indiretamente:** Gestores que recebem os perfis selecionados
- **Manutenção:** Clara Barbosa

## Critérios de aceite (MVP)

- [ ] Karina consegue rodar uma triagem completa sem ajuda técnica após o treinamento
- [ ] Planilha gerada tem: nome, contato, classificação, pontos positivos/negativos e justificativa
- [ ] CVs em PDF e Word são processados sem erro manual
- [ ] Exportação da PandaPé é lida e processada corretamente
- [ ] Tempo de triagem por vaga é menor do que o processo atual
- [ ] Clara consegue manter e evoluir o código sem documentação adicional
