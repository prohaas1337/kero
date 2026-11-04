@echo off
title LAN Party Lejatszo

:: Ha nem admin, auto-elevate UAC-on keresztul
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs -WorkingDirectory '%~dp0'"
    exit /b
)

echo.
echo  LAN Party Lejatszo - inditas...
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo  HIBA: Python nem talalhato!
    echo  Telepitsd innen: https://python.org/downloads
    echo  Fontos: Telepitesnel pipald be "Add Python to PATH"!
    echo.
    pause
    exit /b 1
)

echo  Csomagok telepitese / ellenorzese...
pip install -r requirements.txt --quiet --disable-pip-version-check

echo.
python app.py
