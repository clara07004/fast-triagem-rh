# IMPLEMENTATION_PLAN — fast-triagem-rh

> Plano técnico por fases. Gerado em 2026-05-06. Prazo MVP: 6 dias.

## Pré-requisitos antes de começar

- [ ] `ANTHROPIC_API_KEY` obtida e adicionada ao `.env`
- [ ] Arquivo de exportação do PandaPé recebido (para modelar o parser)
- [ ] Planilha de triagem atual da Karina recebida (para modelar as colunas do output)
- [ ] Exemplo de CV em PDF real para testes de parsing
- [ ] Confirmar com Karina: critérios base comuns a todas as vagas

---

## Fase 1 — MVP (Dias 1–5)

**Objetivo:** pipeline completo funcionando ponta a ponta. Karina entra com critérios + CVs, sai com planilha ranqueada.

### Dia 1 — Setup e parsers
- [ ] Adicionar dependências: `anthropic`, `pdfplumber`, `python-docx`, `openpyxl` ao `pyproject.toml`
- [ ] Criar `src/fast_triagem_rh/models.py` — modelos Pydantic: `VagaCriterios`, `ResultadoCandidato`
- [ ] Criar `src/fast_triagem_rh/parsers/pdf.py` — extração de texto com pdfplumber
- [ ] Criar `src/fast_triagem_rh/parsers/docx.py` — extração de texto com python-docx
- [ ] Criar `src/fast_triagem_rh/parsers/criterios.py` — leitura do template Excel de critérios
- [ ] Criar template `criterios_vaga_template.xlsx` na raiz do projeto
- [ ] Testar parsers com arquivos reais

### Dia 2 — Parser PandaPé + integração IA
- [ ] Criar `src/fast_triagem_rh/parsers/pandape.py` — leitura do export (após receber arquivo)
- [ ] Criar `src/fast_triagem_rh/analyzer.py` — chamada à Claude API com prompt versionado
- [ ] Criar `prompts/triagem_v1.md` — prompt documentado e versionado
- [ ] Testar análise com CVs reais e critérios de vaga exemplo
- [ ] Ajustar prompt até output ser claro e útil

### Dia 3 — Output e orquestrador
- [ ] Criar `src/fast_triagem_rh/output/excel.py` — escreve planilha de resultado com openpyxl
- [ ] Definir colunas: Nome | Contato | Classificação | Pontuação | Pontos Positivos | Pontos Negativos | Justificativa | Fonte | Data Triagem
- [ ] Criar `src/fast_triagem_rh/pipeline.py` — orquestrador que conecta parsers → analyzer → output
- [ ] Testar fluxo ponta a ponta com dados reais

### Dia 4 — CLI e tratamento de erros
- [ ] Criar CLI em `__main__.py`: `python -m fast_triagem_rh --vaga criterios.xlsx --cvs pasta/`
- [ ] Tratar falha de parsing (pular CV + log + incluir na planilha com status `erro_parsing`)
- [ ] Tratar falha de API (retry 3x com backoff, status `erro_api` na planilha se persistir)
- [ ] Validar critérios com Pydantic antes de processar (falha rápida com mensagem legível)

### Dia 5 — Testes e ajustes
- [ ] Teste completo com leva real de CVs (mínimo 10 candidatos)
- [ ] Revisar output com Karina: colunas, formatação, legibilidade
- [ ] Ajustes no prompt se necessário
- [ ] Garantir que o arquivo de saída abre normalmente no Excel

**Critério de saída:** Karina consegue rodar o script e abrir a planilha gerada sem ajuda técnica.

---

## Fase 2 — Estabilização (Dia 6)

**Objetivo:** tratar edge cases, documentar operação, treinar Karina.

- [ ] Testar com CVs problemáticos: PDF escaneado, arquivo protegido por senha, Word antigo (.doc)
- [ ] Garantir que erros aparecem de forma clara na planilha (não apenas no log)
- [ ] Adicionar resumo de execução no final: "X candidatos processados, Y com erro"
- [ ] Preencher `RUNBOOK.md` com instruções operacionais
- [ ] Preparar passo a passo simples para Karina (1 página)
- [ ] Treinamento com Karina: demo + ela executa sozinha
- [ ] Ajustes pós-treinamento se necessário

**Critério de saída:** Karina executa o fluxo completo sem ajuda. RUNBOOK preenchido.

---

## Fase 3 — Produção

> Sem prazo definido. Avançar quando MVP estiver validado em uso real.

- [ ] Avaliar necessidade de empacotamento (exe, instalador) para facilitar uso no computador da Karina
- [ ] Definir onde ficam os arquivos de entrada/saída (pasta local, OneDrive, rede?)
- [ ] Avaliar custo mensal da Claude API com volume real de uso
- [ ] RUNBOOK ativo e validado

---

## Fase 4 — Evolução

> Itens fora do cronograma de entrega. Priorizar com Karina após MVP validado.

- [ ] Integração via API direta com PandaPé (sem exportação manual)
- [ ] Integração com Indeed, LinkedIn, Catho (quando APIs disponíveis)
- [ ] Sugestão de perguntas de entrevista por candidato aprovado
- [ ] Tratamento de dados sensíveis (LGPD) — detecção e anonimização
- [ ] Dashboard de volume e tempo de triagem por vaga
- [ ] Relatório automático para gestores
