' Fast Triagem - involucro invisivel do lancador.
' Executa o iniciar_triagem.ps1 sem abrir nenhuma janela de console.
Dim shell, fso, pastaScripts
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
pastaScripts = fso.GetParentFolderName(WScript.ScriptFullName)
shell.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & pastaScripts & "\iniciar_triagem.ps1""", 0, False
