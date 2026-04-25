@echo off
:: Run on the server as Administrator to deploy latest code from GitHub.
setlocal

set APP=C:\DataCapture
set PYTHON=%APP%\venv\Scripts\python.exe
set PIP=%APP%\venv\Scripts\pip.exe
set TASK=DataCapture

cd /d %APP%

echo [1/5] Pulling latest code from GitHub...
git pull origin main
if %errorlevel% neq 0 (
    echo ERROR: git pull failed. Aborting.
    pause
    exit /b 1
)

echo [2/5] Installing dependencies...
%PIP% install -r requirements.txt --quiet

echo [3/5] Running migrations...
%PYTHON% manage.py migrate --no-input

echo [4/5] Collecting static files...
%PYTHON% manage.py collectstatic --no-input --clear

echo [5/5] Restarting server...
schtasks /end /tn %TASK% 2>nul
timeout /t 3 /nobreak >nul
schtasks /run /tn %TASK%

echo.
echo Deploy complete. App running at http://192.168.10.28:8000
endlocal
