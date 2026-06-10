# Fast Triagem - instalador para um novo computador.
#
# Pre-requisito: Python 3.11+ instalado (python.org, marcando "Add to PATH").
# Uso (na pasta do projeto):
#   powershell -ExecutionPolicy Bypass -File scripts\instalar.ps1
#
# O que faz: confere o Python, instala as dependencias, configura a chave
# da Claude API (.env) e cria o atalho "Fast Triagem" na area de trabalho.

$ErrorActionPreference = "Stop"
$raiz = Split-Path -Parent $PSScriptRoot
Set-Location $raiz

Write-Host ""
Write-Host "=== Fast Triagem - instalacao ===" -ForegroundColor Red
Write-Host ""

# --- 1/4: Python ----------------------------------------------------------
Write-Host "[1/4] Conferindo o Python..."
try {
    $versao = (& python --version 2>&1) -replace "Python ", ""
} catch {
    Write-Host "ERRO: Python nao encontrado." -ForegroundColor Red
    Write-Host "Instale o Python 3.11+ em https://python.org (marque 'Add Python to PATH')."
    exit 1
}
$partes = $versao.Split(".")
if ([int]$partes[0] -lt 3 -or ([int]$partes[0] -eq 3 -and [int]$partes[1] -lt 11)) {
    Write-Host "ERRO: Python $versao encontrado, mas o projeto exige 3.11+." -ForegroundColor Red
    exit 1
}
Write-Host "      Python $versao - ok."

# --- 2/4: Dependencias ----------------------------------------------------
Write-Host "[2/4] Instalando dependencias (pode levar alguns minutos)..."
& python -m pip install -e . --quiet --disable-pip-version-check
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: a instalacao das dependencias falhou. Veja as mensagens acima." -ForegroundColor Red
    exit 1
}
Write-Host "      Dependencias instaladas."

# --- 3/4: Chave da Claude API (.env) --------------------------------------
if (Test-Path ".env") {
    Write-Host "[3/4] Arquivo .env ja existe - mantido como esta."
} else {
    Write-Host "[3/4] Configurando a chave da Claude API."
    Write-Host "      (peca a chave para a Clara Barbosa; ela comeca com 'sk-ant-')"
    $chave = Read-Host "      Cole a ANTHROPIC_API_KEY e tecle Enter"
    if (-not $chave.Trim()) {
        Write-Host "ERRO: nenhuma chave informada. Rode o instalador de novo." -ForegroundColor Red
        exit 1
    }
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Add-Content ".env" "" -Encoding ascii
    }
    Add-Content ".env" "ANTHROPIC_API_KEY=$($chave.Trim())" -Encoding ascii
    Write-Host "      Chave salva no .env (fora do controle de versao)."
}

# --- 4/4: Atalho ----------------------------------------------------------
Write-Host "[4/4] Criando o atalho na area de trabalho..."
& powershell -NoProfile -ExecutionPolicy Bypass -File "$raiz\scripts\criar_atalho.ps1"

Write-Host ""
Write-Host "Pronto! Use o atalho 'Fast Triagem' na area de trabalho para abrir o app." -ForegroundColor Green
Write-Host ""
