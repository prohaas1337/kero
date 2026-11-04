@echo off
cd /d "%~dp0"
title LAN Party Lejatszo

net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs -WorkingDirectory '%~dp0'"
    exit /b
)

echo.
echo  LAN Party Lejatszo - inditas...
echo  Mappa: %~dp0
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo  HIBA: Python nem talalhato!
    echo  Telepitsd innen: https://python.org/downloads
    pause
    exit /b 1
)

echo  Csomagok telepitese...
pip install -r requirements.txt --quiet --disable-pip-version-check

echo.
python app.py > log.txt 2>&1
echo.
echo  === HIBA LOG ===
type log.txt
echo  ================
echo.
pause
