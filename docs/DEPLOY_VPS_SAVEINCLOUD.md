# Deploy em VPS na SaveinCloud — Fast Triagem como app de servidor

Este guia transforma o app de instalação local (um banco por máquina) em um
app central: roda num VPS da SaveinCloud, todo mundo do R&S acessa pelo
navegador e compartilha as mesmas vagas, histórico e planilhas.

**O que muda pra quem usa:** em vez do atalho na área de trabalho, abre um
link no navegador e digita a senha do time. Todo o resto (telas, fluxo) é igual.

**Arquitetura no VPS:** dois containers via Docker Compose —
o app (Streamlit) e o **Caddy**, um proxy que publica o app nas portas
80/443 com certificado HTTPS automático (Let's Encrypt). O banco SQLite
(`data/triagem.db`) e a pasta `vagas/` (CVs + planilhas) viram volumes que
sobrevivem a atualizações.

---

## Pré-requisitos

- Conta na SaveinCloud (painel `app.jelastic.saveincloud.net`).
- Token de acesso do GitHub com leitura no repositório
  `clara07004/fast-triagem-rh` (GitHub → Settings → Developer settings →
  Fine-grained tokens → só esse repo, permissão *Contents: Read*).
- A `ANTHROPIC_API_KEY` da Fast.
- Uma senha de time escolhida (vai virar a `TRIAGEM_SENHA`).

## Passo 1 — Criar o VPS

1. No painel: **NOVO AMBIENTE** → aba **VPS** → **Ubuntu** (versão LTS mais
   recente oferecida, ex. 22.04).
2. Recursos: 4–8 cloudlets resolvem (o app é leve; o trabalho pesado é da
   API da Anthropic).
3. Confirme que o **IPv4 público** está habilitado (no VPS ele costuma vir
   por padrão — é cobrado à parte, confira o custo no resumo).
4. Dê um nome ao ambiente (ex.: `triagem`) e crie.
5. A senha de **root** chega no seu e-mail (e/ou aparece no painel).
   **Anote também o IP público e o hostname** do VPS — o hostname (algo como
   `node1234-triagem.sp1.br.saveincloud.net.br`) será o endereço do app.

## Passo 2 — Entrar no VPS

No painel, clique no ícone **Web SSH** (`>_`) do nó. Logue como `root` com a
senha recebida. (Alternativa: qualquer cliente SSH apontando pro IP público.)

## Passo 3 — Instalar o Docker

```bash
curl -fsSL https://get.docker.com | sh
docker --version && docker compose version
```

## Passo 4 — Baixar o código

```bash
cd /root
git clone https://SEU_TOKEN@github.com/clara07004/fast-triagem-rh.git
cd fast-triagem-rh
```

> Troque `SEU_TOKEN` pelo token do GitHub. Se preferir não deixar o token na
> URL salva, use `git clone https://github.com/clara07004/fast-triagem-rh.git`
> e digite usuário + token quando pedir.

## Passo 5 — Configurar o `.env` do servidor

```bash
cat > .env << 'EOF'
ANTHROPIC_API_KEY=coloque-a-chave-aqui
TRIAGEM_SENHA=senha-do-time-aqui
DOMINIO=hostname-do-vps-aqui
ENVIRONMENT=production
EOF
```

- `TRIAGEM_SENHA` ativa a tela de login do app. Sem ela o app abre sem
  senha — nunca suba sem definir.
- `DOMINIO` é o endereço que o Caddy usa pra emitir o certificado HTTPS:
  o hostname do VPS (Passo 1) ou um domínio próprio (Passo 8).

## Passo 6 — Subir o app

```bash
docker compose up -d --build
```

A primeira build leva alguns minutos. Depois confira:

```bash
docker compose ps          # fast-triagem e fast-caddy "running"
docker compose logs -f     # Ctrl+C pra sair
```

Abra `https://<DOMINIO>` no navegador. Deve aparecer a tela de senha e,
depois dela, o app normal. (O primeiro acesso pode demorar ~30 s enquanto o
Caddy emite o certificado.)

> Se não abrir: confira se as portas 80 e 443 estão liberadas no firewall do
> nó (painel → nó → Firewall) e se o `DOMINIO` do `.env` resolve pro IP do
> VPS (`ping <DOMINIO>` da sua máquina).

## Passo 7 — (Não se aplica) Migrar dados da instalação local

Decisão de junho/2026: as vagas passam a ser cadastradas direto no servidor,
conforme a demanda — o banco antigo da instalação local **não será migrado**.
O servidor começa vazio e isso é o esperado.

Se um dia for preciso trazer dados de uma instalação local: copiar
`data\triagem.db` e a pasta `vagas\` da máquina e enviar via SFTP (WinSCP,
IP público, usuário `root`) pra `/root/fast-triagem-rh/data/` e
`/root/fast-triagem-rh/vagas/`, e rodar `docker compose restart`. Atenção:
isso **sobrescreve** o banco do servidor — só faz sentido antes do time
começar a usar.

## Passo 8 — (Opcional) Domínio próprio

Se quiser `triagem.fastdrywall.com.br` em vez do hostname da SaveinCloud:

1. No DNS da Fast, crie um registro **A** apontando pro IP público do VPS.
2. No `.env` do servidor, troque o `DOMINIO` pelo novo endereço.
3. `docker compose restart caddy` — o certificado novo sai sozinho.

## Atualizações futuras

O deploy real (11/06/2026) foi feito **sem git no servidor**: o código vai
empacotado da máquina da Clara via `pscp` (PuTTY). Pra publicar uma nova
versão, rode na raiz do projeto:

```powershell
.\scripts\deploy_vps.ps1
```

O script pede a senha root do VPS, empacota o código local, envia e
reconstrói os containers. Os dados não são tocados — `data/` e `vagas/`
são volumes fora da imagem.

## Como foi o deploy real (registro)

- VPS criado como **camada adicional** no ambiente `CLARA` (Alterar
  topologia → bloco VPS) — nó 268825, Ubuntu 22.04, IP `200.150.196.205`,
  limite 8 cloudlets. As camadas Node.js/LB do outro projeto não foram
  tocadas.
- O firewall interno do VPS veio fechado: foi liberado com
  `iptables -I INPUT -p tcp -m multiport --dports 22,80,443 -j ACCEPT`
  (via Web SSH do painel) e persistido com `iptables-persistent`.
- App acessível em
  `https://node268825-env-0048116.sp1.br.saveincloud.net.br`
  (HTTPS automático via Caddy/Let's Encrypt).

## Problemas comuns

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| Página não abre | Container parado ou firewall | `docker compose ps` / `logs`; liberar portas 80 e 443 no painel |
| "Conexão não é segura" persistente | Caddy não conseguiu emitir o certificado | `docker compose logs caddy`; conferir `DOMINIO` no `.env` e o DNS |
| Pede senha mas nenhuma funciona | `TRIAGEM_SENHA` diferente do combinado | Conferir `.env` e `docker compose restart` |
| Triagem falha na análise | `ANTHROPIC_API_KEY` ausente/errada | Conferir `.env` e `docker compose restart` |
| Sumiu vaga/histórico após update | Volume não montado | Conferir se rodou o compose de dentro de `/root/fast-triagem-rh` |
| App lento ou caiu após reinício do VPS | Docker não subiu junto | `systemctl enable docker` e `docker compose up -d` |

## Depois do go-live

- [ ] Atualizar o `RUNBOOK.md`: o "como abrir o app" vira "acesse o link e
      digite a senha do time".
- [ ] Repassar URL + senha pra Karina e time de R&S. (O app local nunca chegou
      a ser usado de verdade — o servidor é o primeiro uso real, do zero.)
