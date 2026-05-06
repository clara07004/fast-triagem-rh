#!/usr/bin/env bash
# Bootstrap interativo de um novo projeto a partir do template.
# Uso: ./init.sh
#
# O que faz:
#   1. Pergunta nome do projeto, stack (python/node), descrição.
#   2. Move o starter da stack escolhida pra raiz.
#   3. Substitui PROJECT_NAME_PLACEHOLDER e PROJECT_DESCRIPTION_PLACEHOLDER pelos valores reais.
#   4. Remove o starter da stack não escolhida.
#   5. Remove o próprio init.sh e init.ps1 (não precisa mais).
#   6. Faz primeiro commit estruturado.

set -euo pipefail

# === Cores pra terminal ===
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
RESET="\033[0m"

info() { echo -e "${GREEN}==>${RESET} $1"; }
warn() { echo -e "${YELLOW}!! ${RESET} $1"; }
err()  { echo -e "${RED}xx ${RESET} $1" >&2; }

# === Validações iniciais ===
if [ ! -d "_starter" ]; then
  err "Pasta _starter/ não encontrada. Você está rodando isso na raiz do template?"
  exit 1
fi

if [ ! -d "_starter/python" ] || [ ! -d "_starter/node" ]; then
  err "Starters esperados (python e node) não encontrados em _starter/."
  exit 1
fi

# === Coleta de dados ===
echo
info "Bootstrap de novo projeto Fast"
echo

# Nome do projeto — com validação. Aceita só letras, números, hífen e underscore.
default_name=$(basename "$(pwd)")
valid_pattern='^[a-zA-Z][a-zA-Z0-9_-]*$'

while true; do
  read -rp "Nome do projeto [snake_case_ou_kebab-case] (default: ${default_name}): " project_name
  project_name=${project_name:-$default_name}

  if [[ "$project_name" =~ $valid_pattern ]]; then
    break
  fi

  err "Nome inválido: '$project_name'"
  echo "  Regras:"
  echo "    - Começar com letra (a-z, A-Z)"
  echo "    - Conter apenas letras, números, hífen (-) ou underscore (_)"
  echo "    - Sem espaços, pontos, barras ou caracteres especiais"
  echo "  Exemplos válidos:  triagem-emails, importador_sap, fast-relatorio-vendas"
  echo ""
done

# Normaliza pra snake_case (Python aceita só isso) e kebab pro nome do package
python_name=$(echo "$project_name" | tr '-' '_' | tr '[:upper:]' '[:lower:]')
package_name=$(echo "$project_name" | tr '_' '-' | tr '[:upper:]' '[:lower:]')

# Stack
echo
echo "Stack:"
echo "  1) Python"
echo "  2) Node"
read -rp "Escolha [1/2]: " stack_choice

case $stack_choice in
  1) stack="python"; project_id="$python_name" ;;
  2) stack="node"; project_id="$package_name" ;;
  *) err "Escolha inválida."; exit 1 ;;
esac

# Descrição
echo
read -rp "Descrição curta (uma linha): " project_desc
project_desc=${project_desc:-"Automação interna Fast Sistemas Construtivos"}

echo
info "Resumo:"
echo "  Nome     : $project_id"
echo "  Stack    : $stack"
echo "  Descrição: $project_desc"
echo
read -rp "Confirma? [s/N]: " confirm
if [[ ! "$confirm" =~ ^[sSyY]$ ]]; then
  warn "Cancelado."
  exit 0
fi

# === Move starter escolhido pra raiz ===
info "Movendo starter $stack pra raiz..."
shopt -s dotglob
cp -r "_starter/$stack/"* ./
shopt -u dotglob

# === Substitui placeholders ===
info "Substituindo placeholders..."
# Renomeia pasta src/PROJECT_NAME_PLACEHOLDER (só Python tem)
if [ -d "src/PROJECT_NAME_PLACEHOLDER" ]; then
  mv "src/PROJECT_NAME_PLACEHOLDER" "src/$project_id"
fi

# Substitui em todos os arquivos texto relevantes
find . -type f \( \
  -name "*.py" -o -name "*.js" -o -name "*.ts" -o \
  -name "*.toml" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o \
  -name "*.md" -o -name "Makefile" -o -name ".env.example" \
\) -not -path "./_starter/*" -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./.venv/*" \
  -exec sed -i.bak "s/PROJECT_NAME_PLACEHOLDER/$project_id/g; s/PROJECT_DESCRIPTION_PLACEHOLDER/$project_desc/g" {} \;

# Remove arquivos .bak gerados pelo sed
find . -name "*.bak" -not -path "./.git/*" -delete

# === Limpa starters ===
info "Removendo _starter/..."
rm -rf _starter

# === Remove o próprio init ===
info "Removendo scripts de bootstrap..."
rm -f init.sh init.ps1

# === Setup inicial da stack ===
echo
info "Próximos passos:"
if [ "$stack" = "python" ]; then
  echo "  1. python -m venv .venv && source .venv/bin/activate"
  echo "  2. pip install -e \".[dev]\""
  echo "  3. cp .env.example .env  (e preencher)"
  echo "  4. pre-commit install"
  echo "  5. make test"
else
  echo "  1. npm install"
  echo "  2. cp .env.example .env  (e preencher)"
  echo "  3. npm test"
fi

echo
echo "  Depois: abra o VS Code, rode 'claude' e chame /novo-projeto pra estruturar."
echo

# === Commit inicial ===
if [ -d ".git" ]; then
  read -rp "Fazer primeiro commit agora? [S/n]: " do_commit
  if [[ ! "$do_commit" =~ ^[nN]$ ]]; then
    git add -A
    git commit -m "chore: inicializa projeto $project_id ($stack) a partir do template"
    info "Commit feito. Próximo passo: configurar remote e fazer push."
  fi
fi

info "Pronto. Boa automação."
