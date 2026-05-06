# BACKLOG_PROJETO — fast-triagem-rh

> Gerado em 2026-05-06. Total estimado: 27h (MVP + Estabilização + Produção).

---

## Pré-requisitos (desbloqueiam o projeto)

Antes de implementar, confirmar:

- [ ] `ANTHROPIC_API_KEY` obtida e adicionada ao `.env`
- [ ] Arquivo de exportação do PandaPé recebido (**bloqueia T07**)
- [ ] Planilha atual da Karina recebida (para modelar colunas do output)
- [ ] Exemplo de CV em PDF real para testes
- [ ] Critérios base comuns a todas as vagas confirmados com Karina

---

## Fase MVP

### T01 — Setup de dependências

**Descrição:** Adicionar `anthropic`, `pdfplumber`, `python-docx`, `openpyxl` ao `pyproject.toml`. Rodar `make install` e verificar que todas instalam sem conflito.

| Campo | Valor |
|---|---|
| Prioridade | P1 |
| Horas | 0.5h |
| Dependências | — |
| Fase | MVP |

---

### T02 — Modelos Pydantic

**Descrição:** Criar `src/fast_triagem_rh/models.py` com dois modelos:
- `VagaCriterios`: `cargo`, `requisitos_obrigatorios` (list[str]), `diferenciais` (list[str]), `localizacao`, `tipo_contrato`, `observacoes`
- `ResultadoCandidato`: `nome`, `contato`, `classificacao` (Literal["aprovado","reprovado","verificar","erro_parsing","erro_api"]), `pontuacao` (int 0–100), `pontos_positivos` (list[str]), `pontos_negativos` (list[str]), `justificativa`, `arquivo_fonte`, `data_triagem`

| Campo | Valor |
|---|---|
| Prioridade | P1 |
| Horas | 1h |
| Dependências | T01 |
| Fase | MVP |

---

### T03 — Template Excel de critérios

**Descrição:** Criar `criterios_vaga_template.xlsx` na raiz do projeto com uma aba "Critérios" contendo os campos de `VagaCriterios` como linhas (campo na coluna A, valor na coluna B). Incluir uma aba "Instruções" com passo a passo simples. Karina duplica esse arquivo por vaga.

| Campo | Valor |
|---|---|
| Prioridade | P1 |
| Horas | 0.5h |
| Dependências | T02 |
| Fase | MVP |

---

### T04 — Parser de critérios (Excel → Pydantic)

**Descrição:** Criar `src/fast_triagem_rh/parsers/criterios.py`. Lê `criterios_vaga.xlsx` com `openpyxl`, mapeia para `VagaCriterios`. Falha rápida com mensagem legível se campo obrigatório ausente ou inválido.

| Campo | Valor |
|---|---|
| Prioridade | P1 |
| Horas | 1h |
| Dependências | T02, T03 |
| Fase | MVP |

---

### T05 — Parser PDF

**Descrição:** Criar `src/fast_triagem_rh/parsers/pdf.py`. Usa `pdfplumber` para extrair texto de todas as páginas. Retorna texto concatenado. Se falhar (PDF protegido, escaneado, corrompido), levanta exceção customizada capturável pelo pipeline.

| Campo | Valor |
|---|---|
| Prioridade | P1 |
| Horas | 2h |
| Dependências | T01 |
| Fase | MVP |

---

### T06 — Parser Word

**Descrição:** Criar `src/fast_triagem_rh/parsers/docx.py`. Usa `python-docx` para extrair parágrafos de `.docx`. Concatena em texto único. Tratar `.doc` antigo (sinalizar como não suportado, não travar).

| Campo | Valor |
|---|---|
| Prioridade | P1 |
| Horas | 1.5h |
| Dependências | T01 |
| Fase | MVP |

---

### T07 — Parser PandaPé ⚠️ BLOQUEADO

**Descrição:** Criar `src/fast_triagem_rh/parsers/pandape.py`. Ler o arquivo de exportação do PandaPé (CSV ou XLSX), mapear colunas para texto estruturado por candidato. **Implementar somente após receber o arquivo de exportação real** — a estrutura de colunas é desconhecida até lá.

| Campo | Valor |
|---|---|
| Prioridade | P1 |
| Horas | 2h |
| Dependências | T01, **arquivo PandaPé recebido** |
| Fase | MVP |

---

### T08 — Analyzer (Claude API)

**Descrição:** Criar `src/fast_triagem_rh/analyzer.py`. Recebe `VagaCriterios` + texto do CV, monta prompt v1 (`prompts/triagem_v1.md`), chama `claude-sonnet-4-6`. Retry 3x com backoff exponencial (Tenacity). Valida JSON retornado com Pydantic. Se falhar após retries, retorna `ResultadoCandidato` com `classificacao="erro_api"`.

| Campo | Valor |
|---|---|
| Prioridade | P1 |
| Horas | 2h |
| Dependências | T02, T01 |
| Fase | MVP |

---

### T09 — Output Excel

**Descrição:** Criar `src/fast_triagem_rh/output/excel.py`. Recebe lista de `ResultadoCandidato`, ordena (aprovado > verificar > reprovado > erros, por pontuação dentro de cada grupo), escreve `triagem_<cargo>_<YYYYMMDD_HHMMSS>.xlsx` com openpyxl. Colunas: Nome, Contato, Classificação, Pontuação, Pontos Positivos, Pontos Negativos, Justificativa, Arquivo Fonte, Data Triagem.

| Campo | Valor |
|---|---|
| Prioridade | P1 |
| Horas | 2h |
| Dependências | T02 |
| Fase | MVP |

---

### T10 — Pipeline orquestrador

**Descrição:** Criar `src/fast_triagem_rh/pipeline.py`. Sequência: valida critérios → varre pasta → identifica tipo de cada arquivo → parseia → analisa com IA → acumula resultados → escreve Excel. Log por candidato com `run_id`. CVs com erro de parsing: incluir na planilha com `classificacao="erro_parsing"`, não parar execução.

| Campo | Valor |
|---|---|
| Prioridade | P1 |
| Horas | 2.5h |
| Dependências | T04, T05, T06, T07, T08, T09 |
| Fase | MVP |

---

### T11 — CLI

**Descrição:** Atualizar `src/fast_triagem_rh/__main__.py` com CLI via `argparse`: `--vaga` (path do Excel de critérios) e `--cvs` (path da pasta). Mensagens de erro claras para Karina (sem traceback bruto). Exibir resumo ao final: "X candidatos processados — Y aprovados, Z verificar, W reprovados, V erros."

| Campo | Valor |
|---|---|
| Prioridade | P1 |
| Horas | 1h |
| Dependências | T10 |
| Fase | MVP |

---

### T12 — Teste ponta a ponta com dados reais

**Descrição:** Rodar o pipeline completo com ≥10 CVs reais e critérios de uma vaga real. Revisar output com Karina: classificações fazem sentido? Colunas estão claras? Formatação abre bem no Excel? Ajustar prompt e/ou colunas conforme feedback.

| Campo | Valor |
|---|---|
| Prioridade | P1 |
| Horas | 3h |
| Dependências | T11 |
| Fase | MVP |

---

## Fase Estabilização

### T13 — CVs problemáticos (edge cases)

**Descrição:** Testar com: PDF escaneado (sem camada de texto), PDF protegido por senha, `.doc` (Word antigo), arquivo vazio, arquivo com nome em caracteres especiais. Garantir que cada caso é tratado graciosamente: pula + loga + aparece na planilha com status claro (não apenas no terminal).

| Campo | Valor |
|---|---|
| Prioridade | P2 |
| Horas | 2h |
| Dependências | T12 |
| Fase | Estabilização |

---

### T14 — Ajuste fino do prompt

**Descrição:** Com base nos resultados reais do T12, avaliar se a IA está classificando corretamente casos limítrofes. Se necessário, criar `prompts/triagem_v2.md` com ajustes. Documentar diferença entre versões no arquivo de prompt.

| Campo | Valor |
|---|---|
| Prioridade | P2 |
| Horas | 1.5h |
| Dependências | T12 |
| Fase | Estabilização |

---

### T15 — RUNBOOK.md

**Descrição:** Preencher `RUNBOOK.md` com: como instalar, como rodar, onde ficam os arquivos, erros comuns e como resolver, como atualizar o template de critérios, quem chamar se quebrar.

| Campo | Valor |
|---|---|
| Prioridade | P2 |
| Horas | 1h |
| Dependências | T12 |
| Fase | Estabilização |

---

### T16 — Guia de uso para Karina

**Descrição:** Criar documento de 1 página (`docs/guia_karina.md` ou PDF) com passo a passo em linguagem simples: como preencher o template de critérios, como organizar a pasta de CVs, como rodar o script, o que fazer com o arquivo gerado. Sem jargão técnico.

| Campo | Valor |
|---|---|
| Prioridade | P2 |
| Horas | 1h |
| Dependências | T12 |
| Fase | Estabilização |

---

### T17 — Treinamento com Karina

**Descrição:** Sessão presencial ou remota (~1h): Clara demonstra o fluxo completo, depois Karina executa sozinha com uma vaga real. Coletar feedback e registrar ajustes necessários.

| Campo | Valor |
|---|---|
| Prioridade | P2 |
| Horas | 1.5h |
| Dependências | T15, T16 |
| Fase | Estabilização |

---

## Fase Produção

### T18 — Avaliação de deploy para Karina

**Descrição:** Verificar se Karina consegue rodar Python diretamente ou se precisa de empacotamento (PyInstaller → .exe). Definir onde ficam arquivos de entrada/saída (pasta local, OneDrive, rede compartilhada). Documentar decisão no RUNBOOK.

| Campo | Valor |
|---|---|
| Prioridade | P2 |
| Horas | 1h |
| Dependências | T17 |
| Fase | Produção |

---

### T19 — Validação de custo da API

**Descrição:** Com base no volume real de uso após treinamento, estimar custo mensal da Claude API (tokens por CV × candidatos por mês). Documentar no RUNBOOK. Ajustar modelo para `claude-haiku-4-5-20251001` se custo justificar.

| Campo | Valor |
|---|---|
| Prioridade | P2 |
| Horas | 0.5h |
| Dependências | T17 |
| Fase | Produção |

---

## Fase Evolução (fora do cronograma de entrega)

| ID | Tarefa | Impacto | Esforço |
|---|---|---|---|
| EV01 | API direta PandaPé (sem exportação manual) | Alto | Médio |
| EV02 | API Indeed, LinkedIn, Catho | Alto | Alto |
| EV03 | Sugestão de perguntas de entrevista por candidato aprovado | Médio | Baixo |
| EV04 | Detecção e anonimização de dados sensíveis (LGPD) | Alto | Alto |
| EV05 | Dashboard de volume e tempo de triagem por vaga | Médio | Alto |
| EV06 | Relatório automático para gestores | Médio | Médio |

---

## Resumo de horas

| Fase | Horas |
|---|---|
| MVP | 18.5h |
| Estabilização | 7h |
| Produção | 1.5h |
| **Total** | **27h** |
