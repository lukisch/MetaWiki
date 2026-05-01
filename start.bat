@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
set PYTHON=python
%PYTHON% --version >nul 2>&1
if errorlevel 1 (
    set PYTHON=py -3
    %PYTHON% --version >nul 2>&1
    if errorlevel 1 (
        echo [FEHLER] Python nicht gefunden!
        pause
        exit /b 1
    )
)
%PYTHON% metawiki_cli.py %*
if errorlevel 1 pause
