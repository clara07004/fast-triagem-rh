# Atualiza o Fast Triagem no VPS da SaveinCloud.
#
# Empacota o código local, envia via pscp e reconstrói os containers.
# Os dados (data/ e vagas/) ficam intactos — são volumes fora da imagem.
#
# Uso:  .\scripts\deploy_vps.ps1
#       (pede a senha root do VPS; requer PuTTY instalado)

$ErrorActionPreference = "Stop"

$VpsIp = "200.150.196.205"
$HostKey = "SHA256:0tV7kSsPjM5gZmYFwALBjZ7wfpA/jFBFfGSg3UGgq2A"
$Plink = "C:\Program Files\PuTTY\plink.exe"
$Pscp = "C:\Program Files\PuTTY\pscp.exe"

$senha = Read-Host "Senha root do VPS" -AsSecureString
$senhaTexto = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($senha))

$raiz = Split-Path $PSScriptRoot -Parent
Set-Location $raiz

Write-Host "Empacotando código..."
$pacote = "$env:TEMP\fast-triagem-deploy.tar.gz"
tar -czf $pacote app.py src assets .streamlit pyproject.toml README.md `
    Dockerfile docker-compose.yml Caddyfile .dockerignore

Write-Host "Enviando pro VPS..."
& $Pscp -batch -pw $senhaTexto -hostkey $HostKey $pacote "root@${VpsIp}:/root/"

Write-Host "Reconstruindo containers (3-5 min)..."
& $Plink -batch -ssh "root@$VpsIp" -pw $senhaTexto -hostkey $HostKey `
    "tar -xzf /root/fast-triagem-deploy.tar.gz -C /root/fast-triagem-rh && cd /root/fast-triagem-rh && docker compose up -d --build > /tmp/build.log 2>&1; docker compose ps"

Write-Host "`nPronto. Teste: https://node268825-env-0048116.sp1.br.saveincloud.net.br"
