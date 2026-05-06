# RUNBOOK

> Documentação operacional. Preencher antes de entrar em produção.
> Cópia do template. Mover pra raiz do projeto e renomear pra `RUNBOOK.md`.

## Identificação

- **Projeto:** [nome]
- **Dono:** Clara Barbosa
- **Criticidade:** [baixa / média / alta]
- **SLA:** [se aplicável — ex: deve rodar diariamente até 9h]
- **Ambiente:** [onde roda — Render / Railway / cron local / etc]

## O que essa automação faz

[Uma frase. Pra quem está chegando agora.]

## Como ela é executada

- **Gatilho:** [cron / webhook / manual]
- **Frequência:** [diária 06:00 / a cada hora / sob demanda]
- **Comando manual:** `[python -m projeto / npm start / etc]`

## Operação no dia a dia

### Verificar se está saudável

```bash
# Comando que mostra última execução
[comando]
```

Sinais de saúde:
- [Última execução teve `status: ok` no log]
- [Métrica X dentro de Y]
- [Sem alertas nas últimas 24h]

### Pausar a automação

```bash
[comando ou passo]
```

### Reiniciar

```bash
[comando]
```

### Forçar execução manual

```bash
[comando]
```

## Problemas conhecidos e como resolver

| Sintoma | Causa provável | Como resolver |
|---|---|---|
| | | |

## Em caso de falha

1. [primeiro passo a verificar]
2. [segundo passo]
3. Se não conseguir resolver em [tempo], [próxima ação — escalar pra...]

## Onde estão os logs

- **Local:** [caminho ou serviço]
- **Como acessar:** [comando / link]
- **Retenção:** [quanto tempo]

## Onde estão as credenciais

- **Armazenamento:** [.env local / 1Password / doppler / variáveis no host]
- **Quem tem acesso:** [Clara / outras pessoas]
- **Como rotacionar:** [procedimento]

## Dependências externas

[Lista de APIs e serviços externos que essa automação depende. Se algum cair, o que acontece.]

| Dependência | Impacto se cair |
|---|---|
| | |

## Plano de Disaster Recovery

[Se essa automação parar de funcionar por um dia, o que acontece com a operação?
Existe plano B manual? Quanto tempo o time aguenta sem ela?]

## Contatos de emergência

- **Dono:** Clara Barbosa — clara.barbosa@fastdrywall.com.br
- **Sponsor:** [se aplicável]
- **Suporte do fornecedor crítico:** [se aplicável]
