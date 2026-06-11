# RUNBOOK — Triagem de Candidatos (R&S Fast)

> Documentação operacional. Como rodar a triagem no dia a dia e o que fazer quando algo dá errado.

## Identificação

- **Projeto:** fast-triagem-rh
- **Operadora:** Karina Salles (Coordenadora de R&S)
- **Dona / manutenção:** Clara Barbosa
- **Criticidade:** média — acelera a triagem, mas há plano B manual (não bloqueia o trabalho).
- **SLA de negócio:** entrega de perfis aos gestores em até 10 dias.
- **Ambiente:** app web central num **VPS (SaveinCloud)**, usado pelo navegador. Vagas, histórico e planilhas ficam no servidor, compartilhados pelo time.

## O que essa automação faz

Lê os critérios de uma vaga + os currículos (exportação do PandaPé e/ou PDFs/Word), analisa cada candidato com a Claude API e gera uma planilha Excel ranqueada com classificação, pontuação, contato e justificativa — pronta para a Karina revisar e decidir.

## Como ela é executada

- **Gatilho:** manual, sob demanda, uma vez por vaga.
- **Frequência:** quando há uma vaga para triar.
- **Pelo navegador (caminho da Karina):** acessar
  `https://triagem.fastdrywall.com.br` e informar a senha do time.
  Funciona de qualquer computador, sem instalar nada.
- **Pela linha de comando (alternativa técnica, máquina da Clara):**
  ```bash
  python -m fast_triagem_rh --vaga criterios_<vaga>.xlsx --cvs pasta_da_vaga/
  ```

## Acesso

Não há instalação: o app roda num servidor central e abre direto no navegador
(Chrome ou Edge). Para dar acesso a alguém do time, basta passar a URL acima e
a senha do time (quem tem é a Clara) — **por canal seguro**, nunca por
e-mail/WhatsApp em texto aberto.

## Atualizar a versão do app (manutenção — Clara)

Na máquina da Clara, na pasta do projeto:

```powershell
.\scripts\deploy_vps.ps1
```

O script empacota o código local, envia ao VPS e reconstrói os containers
(pede a senha root do servidor). Detalhes e troubleshooting do servidor em
[docs/DEPLOY_VPS_SAVEINCLOUD.md](docs/DEPLOY_VPS_SAVEINCLOUD.md).

## ⚠️ Regra de ouro — filtrar no PandaPé antes de exportar

**Nunca exporte a etapa "Inscritos" crua.** Ela traz todo mundo que se candidatou — numa vaga real isso chega a **1000+ candidatos**. A IA analisa um por um, em sequência:

| Cenário | Candidatos | Tempo | Custo aprox. |
|---|---|---|---|
| "Inscritos" cru | ~1092 | **1h30 – 2h** | **US$ 12 – 18** |
| Filtrado no PandaPé | ~50 | ~3 min | centavos |

Antes de exportar, **avance a etapa ou aplique os filtros do PandaPé** (localização, experiência, etc.) e exporte só o subconjunto que faz sentido analisar. É o passo que torna a automação viável.

## Operação no dia a dia (passo a passo da Karina)

1. **No PandaPé:** filtre/avance a etapa da vaga (ver regra de ouro acima) e **exporte em `.xlsx`** (não CSV).
2. **No app, seção "Vagas e critérios":** confira se a vaga já existe; se não, cadastre-a (cargo, localização, contrato, requisitos obrigatórios, diferenciais). A vaga fica salva para as próximas triagens.
3. **Seção "Rodar triagem":** escolha a vaga e arraste a exportação do PandaPé (e quaisquer PDFs/Word de outras plataformas).
4. **Acompanhe** a barra de progresso até o fim da análise.
5. **Revise:** o resultado aparece na tela (visão geral, candidatos ranqueados, análise) e a planilha pode ser baixada pelo botão de download. Leia justificativa e pontos negativos antes de decidir. **A decisão final é sempre sua.** Triagens anteriores ficam na seção **"Histórico"**.

### Verificar se rodou bem

Ao terminar, o app mostra o painel da triagem — total de candidatos, aprovados, para verificar, reprovados — e o botão para baixar a planilha. Se isso apareceu, deu certo. Erros aparecem na própria tela, em linguagem simples.

### Pausar / reiniciar / forçar execução

Cada triagem é manual e sob demanda. Para interromper no meio, feche ou recarregue a página (nenhum dado é perdido; basta rodar de novo). O app em si fica sempre no ar: os containers reiniciam sozinhos se o servidor reiniciar.

## Problemas conhecidos e como resolver

| Sintoma | Causa provável | Como resolver |
|---|---|---|
| A URL não abre / app fora do ar | Servidor ou containers parados | Chame a **Clara** (verificar os containers no VPS) |
| Travou por mais de 1h / custo alto | Exportou "Inscritos" cru (1000+ candidatos) | Recarregue a página, filtre no PandaPé e rode de novo com a exportação filtrada |
| `Headers obrigatórios não encontrados` | O arquivo não é uma exportação válida do PandaPé (ou veio em CSV) | Reexporte a vaga em **.xlsx** pelo PandaPé |
| Erro ao salvar a vaga / critérios inválidos | Vaga sem nenhum requisito obrigatório preenchido | Preencha ao menos **um** requisito obrigatório |
| "A chave da Claude API não foi encontrada" | `.env` do servidor ausente ou sem `ANTHROPIC_API_KEY` | Chame a **Clara** (configurar o `.env` no servidor) |
| Localização imprecisa no ranqueamento | Dado de cidade/estado vem incompleto do PandaPé (ex: cidade vazia, estado = "Brasil") | Revise manualmente esses candidatos |
| "Não menciona Excel/Word" recorrente nos pontos negativos | Requisito difícil de comprovar pelo texto do CV | Confirme na entrevista, ou mova "pacote Office" de obrigatório para diferencial |

## Em caso de falha

1. Leia a mensagem de erro na tela — ela é escrita em linguagem simples.
2. Procure o sintoma na tabela acima.
3. Se não resolver, chame a **Clara** com o print da tela.

## Onde estão os logs

- **No servidor:** `docker logs fast-triagem` (via Web SSH da SaveinCloud ou PuTTY — acesso da Clara).
- **Execução via CLI (alternativa técnica):** terminal (stdout); para guardar, redirecione a saída (`> triagem.log 2>&1`).
- Campos sensíveis (chaves, tokens) são mascarados automaticamente no log.

## Onde estão as credenciais

- **Armazenamento:** arquivo `.env` no servidor (`/root/fast-triagem-rh`), fora do Git.
- **Variáveis:** `ANTHROPIC_API_KEY` (Claude API) e `TRIAGEM_SENHA` (senha do time no app).
- **Quem tem acesso:** Clara Barbosa (inclusive a senha root do VPS).
- **Como rotacionar:** gerar nova chave no console da Anthropic (console.anthropic.com), substituir no `.env` do servidor, reiniciar os containers e revogar a antiga. Para trocar a senha do time, alterar `TRIAGEM_SENHA` no mesmo `.env` e reiniciar.

## Dependências externas

| Dependência | Impacto se cair |
|---|---|
| Claude API (Anthropic) | A análise não roda. Fallback: triagem manual. Custo é por candidato analisado. |
| PandaPé | Sem a exportação não há candidatos para triar. É a fonte principal de CVs. |
| VPS SaveinCloud | App fora do ar para o time. Fallback: rodar via CLI na máquina da Clara, ou triagem manual. |

## Plano de Disaster Recovery

A automação **não é bloqueante**: se parar por qualquer motivo, a Karina volta ao processo manual de triagem (o que era feito antes). O time aguenta sem ela — o objetivo dela é recuperar horas e o SLA de 10 dias, não viabilizar a operação. Prioridade de retorno: média.

## Contatos

- **Dona / manutenção:** Clara Barbosa — clara.barbosa@fastdrywall.com.br
- **Operadora:** Karina Salles (Coordenadora de R&S)

---

Ver também: [README.md](README.md) (setup e uso técnico) · [PROCESS_MAP.md](PROCESS_MAP.md) (processo manual vs automatizado) · [SOLUTION_DESIGN.md](SOLUTION_DESIGN.md) (arquitetura).
