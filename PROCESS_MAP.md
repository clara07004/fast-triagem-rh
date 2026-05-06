# PROCESS_MAP — fast-triagem-rh

> Processo atual vs processo automatizado. Gerado em 2026-05-06.

## Processo atual (manual)

**Quem executa:** Karina Salles e time de R&S  
**Frequência:** Contínua, ao longo da semana  
**Tempo estimado:** 3–5 horas/semana

```
1. Vaga aberta no sistema
        ↓
2. Karina acessa cada plataforma manualmente
   (PandaPé, Indeed, Catho, Engenha, LinkedIn)
        ↓
3. Abre candidato por candidato
   → Lê o currículo
   → Avalia mentalmente contra os critérios da vaga
        ↓
4. Classifica manualmente na planilha do time
   → Status: aprovado / reprovado / em análise
   → Justificativa escrita à mão
   → Contato copiado manualmente
        ↓
5. Karina ou gestor recebe a lista final
   → SLA: 10 dias (frequentemente ultrapassado)
```

**Dores identificadas:**
- Repetitivo e braçal — mesmo fluxo pra cada candidato
- Critérios da vaga estão só na cabeça de quem triagem
- Nenhum indicador de volume ou tempo gasto
- SLA estourado por acúmulo de trabalho manual
- Risco de candidatos bons ficarem perdidos no volume

---

## Processo automatizado (target)

**Quem executa:** Karina inicia / IA processa / Karina valida  
**Frequência:** Por demanda (por vaga)  
**Tempo estimado:** < 1 hora/semana (Karina só valida)

```
1. Vaga aberta → Karina preenche os critérios da vaga
   (formulário simples: cargo, requisitos obrigatórios,
    diferenciais, localização, tipo de contrato, etc.)
        ↓
2. Karina coleta os CVs
   → PandaPé: exportação direta
   → Demais plataformas: download de PDFs/Word (por enquanto)
        ↓
3. Automação processa os arquivos
   → Extrai texto de cada CV (PDF / Word / exportação PandaPé)
   → Envia para Claude API com os critérios da vaga
   → Recebe: classificação + justificativa + pontos positivos/negativos
        ↓
4. Resultado gravado na planilha do time
   → Candidatos ranqueados por aderência
   → Colunas: nome | contato | classificação | pontuação |
              pontos positivos | pontos negativos | justificativa IA
        ↓
5. Karina revisa a planilha
   → Pré-aprova candidatos que avançam
   → Encaminha aos gestores
   → SLA de 10 dias recuperado
```

**O que muda:**
- Karina passa de leitora de CV para validadora de resultado
- Critérios da vaga ficam documentados por escrito (não mais só na memória)
- Volume processado deixa de ser gargalo
- Planilha gerada automaticamente, sem digitação manual

---

## Comparação

| Etapa | Hoje | Automatizado |
|---|---|---|
| Coletar candidatos | Manual (5 plataformas) | Semi-auto (PandaPé auto, resto manual por ora) |
| Ler currículos | 100% humano | IA lê todos |
| Avaliar aderência | Mental, subjetivo | IA contra critérios escritos |
| Registrar na planilha | Digitação manual | Automático |
| Tempo total | 3–5h/semana | < 1h/semana (estimado) |
| Rastreabilidade | Baixa | Alta (critérios documentados por vaga) |

---

## Evolução futura

- **Fase 2:** Integração via API com Indeed, Catho, LinkedIn — eliminar o download manual de CVs.
- **Fase 3:** Geração automática de sugestões de perguntas de entrevista por candidato.
- **Fase 4:** Relatório consolidado direto para o gestor, sem passar pela planilha.
