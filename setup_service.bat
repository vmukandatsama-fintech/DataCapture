@echo off
:: Run once on the server as Administrator to register the Windows Service.
:: No external tools required — uses pywin32 (installed via pip).
setlocal

set APP=C:\DataCapture
set PYTHON=%APP%\venv\Scripts\python.exe
set PIP=%APP%\venv\Scripts\pip.exe
set SVC=DataCapture

cd /d %APP%

echo [1/4] Installing pywin32...
%PIP% install pywin32 --quiet
%PYTHON% venv\Scripts\pywin32_postinstall.py -install 2>nul

echo [2/4] Registering Windows Service...
net stop %SVC% 2>nul
%PYTHON% windows_service.py remove 2>nul
%PYTHON% windows_service.py install

echo [3/4] Configuring auto-restart on crash and auto-start on boot...
sc config %SVC% start= auto
sc failure %SVC% reset= 86400 actions= restart/5000/restart/5000/restart/5000

echo [4/4] Opening firewall port 8000...
netsh advfirewall firewall delete rule name="DataCapture" >nul 2>&1
netsh advfirewall firewall add rule name="DataCapture" dir=in action=allow protocol=TCP localport=8000

net start %SVC%

echo.
echo Service "%SVC%" installed and started.
echo Auto-restarts on crash, auto-starts on server reboot.
echo App: http://192.168.10.28:8000
echo.
pause
endlocal
