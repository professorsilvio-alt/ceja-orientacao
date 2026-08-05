# agendar_sync.ps1
# Cria uma Tarefa Agendada para executar sync_horarios.ps1 diariamente as 06:00.
# Usa schtasks.exe - NAO precisa de privilegios de Administrador.

$scriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$scriptSync = Join-Path $scriptDir "sync_horarios.ps1"
$logFile    = Join-Path $scriptDir "sync_horarios.log"
$taskName   = "CEJA - Sync Horarios"
$psExe      = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
$args       = "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$scriptSync`""

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " CEJA - Configuracao da Tarefa Agendada" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Script : $scriptSync"
Write-Host "Log    : $logFile"
Write-Host "Horario: Todos os dias as 06:00"
Write-Host ""

# Remove tarefa anterior (ignora erro se nao existir)
schtasks /Delete /TN "$taskName" /F 2>$null | Out-Null

# Cria a tarefa com schtasks.exe (funciona sem admin para usuario atual)
$resultado = schtasks /Create `
    /TN "$taskName" `
    /TR "`"$psExe`" $args" `
    /SC DAILY `
    /ST 06:00 `
    /RL HIGHEST `
    /F 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "Tarefa '$taskName' criada com sucesso!" -ForegroundColor Green
    Write-Host "Proxima execucao automatica: amanha as 06:00."
} else {
    Write-Host ""
    Write-Host "Nao foi possivel criar via schtasks. Tentando metodo alternativo..." -ForegroundColor Yellow

    # Metodo alternativo: cria o XML e importa via COM (tambem sem admin)
    $xml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Sincroniza horarios dos professores do CEJA a partir do Google Sheets.</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-08-04T06:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Enabled>true</Enabled>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>$psExe</Command>
      <Arguments>-ExecutionPolicy Bypass -WindowStyle Hidden -File "$scriptSync"</Arguments>
      <WorkingDirectory>$scriptDir</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"@
    $xmlPath = Join-Path $env:TEMP "ceja_sync_task.xml"
    [System.IO.File]::WriteAllText($xmlPath, $xml, [System.Text.Encoding]::Unicode)

    $res2 = schtasks /Create /TN "$taskName" /XML "$xmlPath" /F 2>&1
    Remove-Item $xmlPath -ErrorAction SilentlyContinue

    if ($LASTEXITCODE -eq 0) {
        Write-Host "Tarefa '$taskName' criada com sucesso (via XML)!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "Nao foi possivel registrar a tarefa automaticamente." -ForegroundColor Red
        Write-Host ""
        Write-Host "SOLUCAO MANUAL (2 opcoes):" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Opcao 1 - Execute UMA VEZ como Administrador:" -ForegroundColor White
        Write-Host "  Clique com botao direito no PowerShell > 'Executar como Administrador'"
        Write-Host "  Depois rode: powershell -ExecutionPolicy Bypass -File `"$($MyInvocation.MyCommand.Path)`""
        Write-Host ""
        Write-Host "Opcao 2 - Use o Agendador de Tarefas do Windows manualmente:" -ForegroundColor White
        Write-Host "  1. Abra 'Agendador de Tarefas' (taskschd.msc)"
        Write-Host "  2. Clique em 'Criar Tarefa Basica'"
        Write-Host "  3. Nome: $taskName"
        Write-Host "  4. Disparador: Diariamente as 06:00"
        Write-Host "  5. Acao: Iniciar programa"
        Write-Host "     Programa: $psExe"
        Write-Host "     Argumentos: -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$scriptSync`""
        Write-Host "     Iniciar em: $scriptDir"
        Write-Host ""
        Write-Host "Opcao 3 - Execucao via STARTUP (sem precisar de admin):" -ForegroundColor White
        Write-Host "  Sera criado um atalho na pasta Inicializacao do Windows."
        $resp3 = Read-Host "  Criar atalho na pasta Startup? (S/N)"
        if ($resp3 -match '^[Ss]') {
            $startupDir = [System.IO.Path]::Combine($env:APPDATA, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
            $batPath    = Join-Path $startupDir "CEJA_sync.bat"
            $batContent = "@echo off`r`npowershell -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$scriptSync`"`r`n"
            [System.IO.File]::WriteAllText($batPath, $batContent, [System.Text.Encoding]::ASCII)
            Write-Host "  Atalho criado: $batPath" -ForegroundColor Green
            Write-Host "  O sync sera executado toda vez que o Windows iniciar." -ForegroundColor Green
        }
        Write-Host ""
    }
}

Write-Host ""

# Pergunta se quer executar agora
$resp = Read-Host "Executar o sync agora para testar? (S/N)"
if ($resp -match '^[Ss]') {
    Write-Host ""
    Write-Host "Executando sync..." -ForegroundColor Cyan
    Write-Host ""
    & "$psExe" -ExecutionPolicy Bypass -File "$scriptSync"
}

Write-Host ""
Write-Host "Concluido!" -ForegroundColor Green
Write-Host ""
