@echo off
title Editor AFP - Servidor local
cd /d "%~dp0"
powershell -NoProfile -STA -ExecutionPolicy Bypass -File "%~dp0EditorAFP-Servidor.ps1"
echo.
echo El servidor se detuvo. Pulsa una tecla para cerrar.
pause >nul
