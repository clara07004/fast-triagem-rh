# TASKS — fast-triagem-rh

> Lista inicial de tarefas do MVP. Gerado em 2026-05-06. Prazo: 6 dias.

## Status

- [ ] = pendente
- [x] = concluído
- [~] = em andamento

---

## Fase 0 — Alinhamento (Dia 1)

- [ ] Reunião rápida com Karina para levantar:
  - Critérios base comuns a todas as vagas
  - Volume médio de vagas/semana e candidatos/vaga
  - Formato atual da planilha de triagem (Google Sheets ou Excel?)
  - Exemplo de exportação do PandaPé (estrutura do CSV/XLSX)
- [ ] Confirmar destino da planilha de output (Google Sheets vs Excel local)
- [ ] Obter exemplo de CV de candidato (PDF real) para testes

---

## Fase 1 — Setup e parsing (Dias 1–2)

- [ ] Adicionar dependências ao `pyproject.toml`: pdfplumber, python-docx, gspread (ou openpyxl), anthropic
- [ ] Criar módulo `src/fast_triagem_rh/parsers/pdf.py` — extração de texto de PDF
- [ ] Criar módulo `src/fast_triagem_rh/parsers/docx.py` — extração de texto de Word
- [ ] Criar módulo `src/fast_triagem_rh/parsers/pandape.py` — leitura do CSV/XLSX exportado
- [ ] Testar parsing com CVs reais (PDF, Word, exportação PandaPé)
- [ ] Criar modelo Pydantic `VagaCriterios` para validar input de critérios
- [ ] Definir formato de input de critérios (YAML por vaga)

---

## Fase 2 — Integração com IA (Dias 2–3)

- [ ] Configurar `ANTHROPIC_API_KEY` no `.env`
- [ ] Criar módulo `src/fast_triagem_rh/analyzer.py` — chamada à Claude API
- [ ] Criar prompt de triagem com critérios + CV
- [ ] Criar modelo Pydantic `ResultadoCandidato` para validar resposta da IA
- [ ] Testar análise com CVs reais e critérios de vaga exemplo
- [ ] Ajustar prompt até resultado ser claro e útil para Karina

---

## Fase 3 — Output na planilha (Dias 3–4)

- [ ] Configurar integração com Google Sheets (gspread + credenciais) ou Excel (openpyxl)
- [ ] Criar módulo `src/fast_triagem_rh/output/sheets.py` — escrita dos resultados
- [ ] Definir estrutura de colunas da planilha com Karina
- [ ] Testar escrita de resultados reais na planilha

---

## Fase 4 — Orquestração e interface (Dias 4–5)

- [ ] Criar orquestrador principal `src/fast_triagem_rh/pipeline.py`
- [ ] Criar CLI simples (`python -m fast_triagem_rh --vaga criterios.yaml --cvs pasta/`)
- [ ] Adicionar log por candidato (arquivo processado, resultado, status)
- [ ] Tratar erros de parsing (CV ilegível → pular + log)
- [ ] Tratar erros de API (retry automático com tenacity)
- [ ] Testar fluxo completo ponta a ponta com dados reais

---

## Fase 5 — Entrega (Dia 6)

- [ ] Revisar README com instruções claras de uso
- [ ] Preparar material de treinamento para Karina (passo a passo simples)
- [ ] Treinamento com Karina (demo + prática)
- [ ] Ajustes pós-treinamento se necessário
- [ ] Preencher `RUNBOOK.md` com instruções operacionais

---

## Backlog (pós-MVP)

- [ ] Integração via API direta com PandaPé (sem exportação manual)
- [ ] Sugestão de perguntas de entrevista por candidato aprovado
- [ ] Dashboard de volume e tempo de triagem por vaga
- [ ] Integração com Indeed, LinkedIn, Catho
- [ ] Tratamento de dados sensíveis (LGPD)
- [ ] Relatório automático para gestores
