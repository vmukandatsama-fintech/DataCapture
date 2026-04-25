# Run as Administrator in PowerShell
$APP    = "C:\DataCapture"
$PYTHON = "$APP\venv\Scripts\python.exe"
$TASK   = "DataCapture"

Write-Host "[1/3] Registering scheduled task..."

Unregister-ScheduledTask -TaskName $TASK -Confirm:$false -ErrorAction SilentlyContinue

$action = New-ScheduledTaskAction `
    -Execute $PYTHON `
    -Argument "$APP\serve.py" `
    -WorkingDirectory $APP

$trigger = New-ScheduledTaskTrigger -AtStartup

$settings = New-ScheduledTaskSettingsSet `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -MultipleInstances IgnoreNew

$principal = New-ScheduledTaskPrincipal `
    -UserId "SYSTEM" `
    -LogonType ServiceAccount `
    -RunLevel Highest

Register-ScheduledTask `
    -TaskName $TASK `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "DataCapture CY26 Web App - Waitress on port 8000" `
    -Force | Out-Null

Write-Host "[2/3] Opening firewall port 8000..."
netsh advfirewall firewall delete rule name="DataCapture" | Out-Null
netsh advfirewall firewall add rule name="DataCapture" dir=in action=allow protocol=TCP localport=8000 | Out-Null

Write-Host "[3/3] Starting now..."
Start-ScheduledTask -TaskName $TASK

Write-Host ""
Write-Host "Done. DataCapture is running at http://192.168.10.28:8000"
Write-Host "Auto-starts on every server reboot."
Write-Host "Restarts automatically on failure (3x, 1 minute apart)."
