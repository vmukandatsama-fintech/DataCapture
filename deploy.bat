@echo off
:: Run this on the server after every git pull to apply updates.
setlocal

set APP=C:\Apps\datacapture
set PYTHON=%APP%\venv\Scripts\python.exe
set PIP=%APP%\venv\Scripts\pip.exe

echo [1/5] Pulling latest code...
cd /d %APP%
git pull

echo [2/5] Installing dependencies...
%PIP% install -r requirements.txt --quiet

echo [3/5] Running migrations...
%PYTHON% manage.py migrate --no-input

echo [4/5] Collecting static files...
%PYTHON% manage.py collectstatic --no-input --clear

echo [5/5] Restarting service...
net stop DataCapture
net start DataCapture

echo.
echo Deploy complete.
endlocal
