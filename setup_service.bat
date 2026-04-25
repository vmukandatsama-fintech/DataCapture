@echo off
:: Run once on the server as Administrator to register the Windows Service.
:: Requires nssm.exe in C:\Tools\ — download from https://nssm.cc/download
setlocal

set APP=C:\DataCapture
set NSSM=C:\Tools\nssm.exe
set SVC=DataCapture
set PYTHON=%APP%\venv\Scripts\python.exe
set SCRIPT=%APP%\serve.py
set LOG=%APP%\logs

if not exist "%NSSM%" (
    echo ERROR: nssm.exe not found at %NSSM%
    echo Download from https://nssm.cc/download and place nssm.exe in C:\Tools\
    pause
    exit /b 1
)

:: Create log directory
if not exist "%LOG%" mkdir "%LOG%"

:: Remove existing service if present
%NSSM% stop %SVC% 2>nul
%NSSM% remove %SVC% confirm 2>nul

:: Install service
%NSSM% install %SVC% "%PYTHON%" "%SCRIPT%"

:: Working directory
%NSSM% set %SVC% AppDirectory "%APP%"

:: Display name and description
%NSSM% set %SVC% DisplayName "DataCapture Web App"
%NSSM% set %SVC% Description "CY26 Data Capture — Waitress on port 8000"

:: Auto-start on boot
%NSSM% set %SVC% Start SERVICE_AUTO_START

:: Restart automatically if it crashes (wait 5 seconds before restart)
%NSSM% set %SVC% AppRestartDelay 5000
%NSSM% set %SVC% AppExit Default Restart

:: Log stdout and stderr to files
%NSSM% set %SVC% AppStdout "%LOG%\app.log"
%NSSM% set %SVC% AppStderr "%LOG%\error.log"
%NSSM% set %SVC% AppRotateFiles 1
%NSSM% set %SVC% AppRotateSeconds 86400

:: Open firewall port 8000
netsh advfirewall firewall delete rule name="DataCapture" >nul 2>&1
netsh advfirewall firewall add rule name="DataCapture" dir=in action=allow protocol=TCP localport=8000

:: Start the service now
%NSSM% start %SVC%

echo.
echo Service "%SVC%" installed and started.
echo Auto-restarts on crash and on server reboot.
echo Logs: %LOG%\app.log / error.log
echo App:  http://192.168.10.28:8000
echo.
pause
endlocal
