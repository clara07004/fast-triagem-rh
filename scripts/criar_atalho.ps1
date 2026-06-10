# Fast Triagem - cria o atalho "Fast Triagem" na area de trabalho.
# Rode uma vez em cada computador que vai usar o app:
#   powershell -ExecutionPolicy Bypass -File scripts\criar_atalho.ps1

$raiz = Split-Path -Parent $PSScriptRoot
$desktop = [Environment]::GetFolderPath("Desktop")
$atalho = Join-Path $desktop "Fast Triagem.lnk"

$ws = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut($atalho)
$lnk.TargetPath = "$env:SystemRoot\System32\wscript.exe"
$lnk.Arguments = """$raiz\scripts\iniciar_triagem.vbs"""
$lnk.WorkingDirectory = $raiz
$lnk.IconLocation = "$raiz\assets\fast_triagem.ico"
$lnk.Description = "Fast Triagem - triagem de candidatos com IA (RS)"
$lnk.Save()

Write-Host "Atalho criado: $atalho"
