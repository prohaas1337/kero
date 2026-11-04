@echo off
title LAN Party Lejatszo

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
if %errorlevel% neq 0 (
    echo  HIBA: Csomagok telepitese sikertelen!
    pause
    exit /b 1
)

echo.
python app.py
pause
