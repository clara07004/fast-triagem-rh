# Bootstrap interativo de um novo projeto a partir do template (Windows / PowerShell).
# Uso: .\init.ps1
#
# Equivalente ao init.sh — escolhe stack, substitui placeholders, faz primeiro commit.

$ErrorActionPreference = "Stop"

function Write-Info($msg) { Write-Host "==> $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "!!  $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "xx  $msg" -ForegroundColor Red }

# Validações
if (-not (Test-Path "_starter")) {
    Write-Err "Pasta _starter/ não encontrada. Está rodando na raiz do template?"
    exit 1
}
if (-not (Test-Path "_starter/python") -or -not (Test-Path "_starter/node")) {
    Write-Err "Starters esperados (python e node) não encontrados em _starter/."
    exit 1
}

Write-Host ""
Write-Info "Bootstrap de novo projeto Fast"
Write-Host ""

# Nome — com validação. Aceita só letras, números, hífen e underscore.
$defaultName = (Get-Item -Path ".").Name
$validNamePattern = '^[a-zA-Z][a-zA-Z0-9_-]*$'

while ($true) {
    $projectName = Read-Host "Nome do projeto (default: $defaultName)"
    if ([string]::IsNullOrWhiteSpace($projectName)) { $projectName = $defaultName }

    if ($projectName -match $validNamePattern) {
        break
    }

    Write-Err "Nome inválido: '$projectName'"
    Write-Host "  Regras:"
    Write-Host "    - Começar com letra (a-z, A-Z)"
    Write-Host "    - Conter apenas letras, números, hífen (-) ou underscore (_)"
    Write-Host "    - Sem espaços, pontos, barras ou caracteres especiais"
    Write-Host "  Exemplos válidos:  triagem-emails, importador_sap, fast-relatorio-vendas"
    Write-Host ""
}

$pythonName = $projectName.ToLower() -replace '-', '_'
$packageName = $projectName.ToLower() -replace '_', '-'

# Stack
Write-Host ""
Write-Host "Stack:"
Write-Host "  1) Python"
Write-Host "  2) Node"
$stackChoice = Read-Host "Escolha [1/2]"

switch ($stackChoice) {
    "1" { $stack = "python"; $projectId = $pythonName }
    "2" { $stack = "node"; $projectId = $packageName }
    default { Write-Err "Escolha inválida."; exit 1 }
}

Write-Host ""
$projectDesc = Read-Host "Descrição curta (uma linha)"
if ([string]::IsNullOrWhiteSpace($projectDesc)) {
    $projectDesc = "Automação interna Fast Sistemas Construtivos"
}

Write-Host ""
Write-Info "Resumo:"
Write-Host "  Nome     : $projectId"
Write-Host "  Stack    : $stack"
Write-Host "  Descrição: $projectDesc"
Write-Host ""
$confirm = Read-Host "Confirma? [s/N]"
if ($confirm -notmatch '^[sSyY]$') {
    Write-Warn "Cancelado."
    exit 0
}

# Copiar starter
Write-Info "Movendo starter $stack pra raiz..."
Copy-Item -Path "_starter/$stack/*" -Destination "." -Recurse -Force

# Renomear pasta src se existir (Python)
if (Test-Path "src/PROJECT_NAME_PLACEHOLDER") {
    Rename-Item -Path "src/PROJECT_NAME_PLACEHOLDER" -NewName $projectId
}

# Substituir placeholders
Write-Info "Substituindo placeholders..."
$extensions = @("*.py", "*.js", "*.ts", "*.toml", "*.json", "*.yaml", "*.yml", "*.md", "Makefile", ".env.example")
$excludeDirs = @("_starter", ".git", "node_modules", ".venv")

Get-ChildItem -Recurse -File -Include $extensions | Where-Object {
    $path = $_.FullName
    -not ($excludeDirs | Where-Object { $path -like "*\$_\*" })
} | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $newContent = $content -replace 'PROJECT_NAME_PLACEHOLDER', $projectId
    $newContent = $newContent -replace 'PROJECT_DESCRIPTION_PLACEHOLDER', $projectDesc
    if ($content -ne $newContent) {
        Set-Content -Path $_.FullName -Value $newContent -NoNewline
    }
}

# Limpar starters e scripts de bootstrap
Write-Info "Removendo _starter/ e scripts de bootstrap..."
Remove-Item -Path "_starter" -Recurse -Force
Remove-Item -Path "init.sh" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "init.ps1" -Force -ErrorAction SilentlyContinue

# Próximos passos
Write-Host ""
Write-Info "Próximos passos:"
if ($stack -eq "python") {
    Write-Host "  1. python -m venv .venv; .\.venv\Scripts\Activate.ps1"
    Write-Host "  2. pip install -e `".[dev]`""
    Write-Host "  3. Copy-Item .env.example .env  (e preencher)"
    Write-Host "  4. pre-commit install"
    Write-Host "  5. make test"
} else {
    Write-Host "  1. npm install"
    Write-Host "  2. Copy-Item .env.example .env  (e preencher)"
    Write-Host "  3. npm test"
}

Write-Host ""
Write-Host "  Depois: abra o VS Code, rode 'claude' e chame /novo-projeto."
Write-Host ""

# Commit inicial
if (Test-Path ".git") {
    $doCommit = Read-Host "Fazer primeiro commit agora? [S/n]"
    if ($doCommit -notmatch '^[nN]$') {
        git add -A
        git commit -m "chore: inicializa projeto $projectId ($stack) a partir do template"
        Write-Info "Commit feito."
    }
}

Write-Info "Pronto. Boa automação."
