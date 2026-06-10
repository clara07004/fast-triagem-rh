# Fast Triagem - lancador do app.
# Sobe o servidor Streamlit escondido (se ainda nao estiver no ar) e abre
# o app numa janela propria (modo aplicativo do Edge/Chrome, sem barra de
# navegador). Chamado pelo iniciar_triagem.vbs para nao piscar console.

$ErrorActionPreference = "SilentlyContinue"

$raiz = Split-Path -Parent $PSScriptRoot
$porta = 8501
$url = "http://localhost:$porta"

Set-Location $raiz

# 1. Garante o servidor no ar (escondido).
$noAr = Get-NetTCPConnection -LocalPort $porta -State Listen -ErrorAction SilentlyContinue
if (-not $noAr) {
    Start-Process -FilePath python `
        -ArgumentList "-m", "streamlit", "run", "app.py", "--server.port", "$porta" `
        -WorkingDirectory $raiz -WindowStyle Hidden
    # Espera o servidor responder (ate ~30 s).
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 1
        try {
            $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2
            if ($resp.StatusCode -eq 200) { break }
        } catch {}
    }
}

# 2. Abre como janela de aplicativo (sem abas/barra de endereco).
$navegadores = @(
    "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
)
$navegador = $navegadores | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($navegador) {
    Start-Process -FilePath $navegador -ArgumentList "--app=$url"
} else {
    # Sem Chrome/Edge: abre no navegador padrao mesmo.
    Start-Process $url
}
