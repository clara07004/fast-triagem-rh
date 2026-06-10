# RUNBOOK — Triagem de Candidatos (R&S Fast)

> Documentação operacional. Como rodar a triagem no dia a dia e o que fazer quando algo dá errado.

## Identificação

- **Projeto:** fast-triagem-rh
- **Operadora:** Karina Salles (Coordenadora de R&S)
- **Dona / manutenção:** Clara Barbosa
- **Criticidade:** média — acelera a triagem, mas há plano B manual (não bloqueia o trabalho).
- **SLA de negócio:** entrega de perfis aos gestores em até 10 dias.
- **Ambiente:** execução **local e manual** (CLI), no computador da operadora. Não há serviço rodando em servidor.

## O que essa automação faz

Lê os critérios de uma vaga + os currículos (exportação do PandaPé e/ou PDFs/Word), analisa cada candidato com a Claude API e gera uma planilha Excel ranqueada com classificação, pontuação, contato e justificativa — pronta para a Karina revisar e decidir.

## Como ela é executada

- **Gatilho:** manual, sob demanda, uma vez por vaga.
- **Frequência:** quando há uma vaga para triar.
- **Pelo app (caminho da Karina):** duplo clique no atalho **"Fast Triagem"** da
  área de trabalho. Ele sobe o servidor local escondido e abre o app numa
  janela própria.
- **Pela linha de comando (alternativa técnica):**
  ```bash
  python -m fast_triagem_rh --vaga criterios_<vaga>.xlsx --cvs pasta_da_vaga/
  ```

## Instalação em um novo computador

Pré-requisito: **Python 3.11+** ([python.org](https://python.org), marcando
*"Add Python to PATH"*) e Chrome ou Edge instalado.

1. Clonar o projeto (`git clone https://github.com/clara07004/fast-triagem-rh.git`)
   ou baixar o ZIP pelo GitHub (*Code → Download ZIP*) e extrair.
2. Na pasta do projeto, rodar o instalador:
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\instalar.ps1
   ```
   Ele confere o Python, instala as dependências, pede a `ANTHROPIC_API_KEY`
   (pedir à Clara — transferir por canal seguro, nunca por e-mail/WhatsApp em
   texto aberto) e cria o atalho **"Fast Triagem"** na área de trabalho.
3. Pronto — duplo clique no atalho abre o app.

> O histórico de triagens (`data/`) e os CVs (`vagas/`) são locais de cada
> computador e **não** vão pro GitHub. Instalação nova começa com histórico
> zerado — é o esperado.

## ⚠️ Regra de ouro — filtrar no PandaPé antes de exportar

**Nunca exporte a etapa "Inscritos" crua.** Ela traz todo mundo que se candidatou — numa vaga real isso chega a **1000+ candidatos**. A IA analisa um por um, em sequência:

| Cenário | Candidatos | Tempo | Custo aprox. |
|---|---|---|---|
| "Inscritos" cru | ~1092 | **1h30 – 2h** | **US$ 12 – 18** |
| Filtrado no PandaPé | ~50 | ~3 min | centavos |

Antes de exportar, **avance a etapa ou aplique os filtros do PandaPé** (localização, experiência, etc.) e exporte só o subconjunto que faz sentido analisar. É o passo que torna a automação viável.

## Operação no dia a dia (passo a passo da Karina)

1. **No PandaPé:** filtre/avance a etapa da vaga (ver regra de ouro acima) e **exporte em `.xlsx`** (não CSV).
2. **Critérios:** abra `criterios_vaga_template.xlsx`, preencha os campos amarelos (cargo, localização, contrato, requisitos obrigatórios, diferenciais) e salve como `criterios_<vaga>.xlsx`.
3. **Pasta da vaga:** crie uma pasta e coloque dentro o `.xlsx` exportado do PandaPé (e quaisquer PDFs/Word de outras plataformas).
4. **Rode** o comando acima apontando para o arquivo de critérios e a pasta.
5. **Revise:** abra `triagem_<vaga>_<data>.xlsx` — comece pela aba **Resumo** (visão geral) e vá para a **Triagem** (lista ranqueada). Leia justificativa e pontos negativos antes de decidir. **A decisão final é sempre sua.**

### Verificar se rodou bem

Ao terminar, o script imprime no terminal:
```
Triagem concluida — N candidato(s) processado(s).
   X aprovados, Y para verificar, Z reprovados.
Planilha gerada: triagem_<vaga>_<data>.xlsx
```
Se aparecer isso e a planilha foi criada, deu certo. Erros aparecem como `[ERRO] ...` em linguagem simples.

### Pausar / reiniciar / forçar execução

Não se aplica — a automação não é um serviço contínuo. Cada execução é manual e sob demanda. Para interromper no meio, `Ctrl+C` no terminal (nenhum dado é perdido; basta rodar de novo).

## Problemas conhecidos e como resolver

| Sintoma | Causa provável | Como resolver |
|---|---|---|
| Travou por mais de 1h / custo alto | Exportou "Inscritos" cru (1000+ candidatos) | Cancele (`Ctrl+C`), filtre no PandaPé e exporte um subconjunto |
| `[ERRO] ... Permission denied` ao gerar a planilha | A planilha de saída está **aberta no Excel** | Feche o arquivo no Excel e rode de novo |
| `Headers obrigatórios não encontrados` | O arquivo não é uma exportação válida do PandaPé (ou veio em CSV) | Reexporte a vaga em **.xlsx** pelo PandaPé |
| `Critérios inválidos` / sem requisito | Template de critérios sem nenhum requisito obrigatório preenchido | Preencha ao menos **um** requisito obrigatório |
| `A chave da Claude API não foi encontrada` | `.env` ausente ou sem `ANTHROPIC_API_KEY` | Copie `.env.example` para `.env` e preencha a chave |
| Localização imprecisa no ranqueamento | Dado de cidade/estado vem incompleto do PandaPé (ex: cidade vazia, estado = "Brasil") | Revise manualmente esses candidatos |
| "Não menciona Excel/Word" recorrente nos pontos negativos | Requisito difícil de comprovar pelo texto do CV | Confirme na entrevista, ou mova "pacote Office" de obrigatório para diferencial |

## Em caso de falha

1. Leia a mensagem `[ERRO]` — ela é escrita em linguagem simples.
2. Procure o sintoma na tabela acima.
3. Se não resolver, chame a **Clara** com o print da mensagem do terminal.

## Onde estão os logs

- **Local:** terminal (stdout) durante a execução. **Não são salvos em arquivo** por padrão.
- **Para guardar um log:** redirecione a saída, ex:
  ```bash
  python -m fast_triagem_rh --vaga criterios_x.xlsx --cvs pasta/ > triagem.log 2>&1
  ```
- Campos sensíveis (chaves, tokens) são mascarados automaticamente no log.

## Onde estão as credenciais

- **Armazenamento:** arquivo `.env` local (ignorado pelo Git — nunca é commitado).
- **Variável:** `ANTHROPIC_API_KEY` (Claude API).
- **Quem tem acesso:** Clara Barbosa.
- **Como rotacionar:** gerar nova chave no console da Anthropic (console.anthropic.com), substituir no `.env` e revogar a antiga.

## Dependências externas

| Dependência | Impacto se cair |
|---|---|
| Claude API (Anthropic) | A análise não roda. Fallback: triagem manual. Custo é por candidato analisado. |
| PandaPé | Sem a exportação não há candidatos para triar. É a fonte principal de CVs. |

## Plano de Disaster Recovery

A automação **não é bloqueante**: se parar por qualquer motivo, a Karina volta ao processo manual de triagem (o que era feito antes). O time aguenta sem ela — o objetivo dela é recuperar horas e o SLA de 10 dias, não viabilizar a operação. Prioridade de retorno: média.

## Contatos

- **Dona / manutenção:** Clara Barbosa — clara.barbosa@fastdrywall.com.br
- **Operadora:** Karina Salles (Coordenadora de R&S)

---

Ver também: [README.md](README.md) (setup e uso técnico) · [PROCESS_MAP.md](PROCESS_MAP.md) (processo manual vs automatizado) · [SOLUTION_DESIGN.md](SOLUTION_DESIGN.md) (arquitetura).
