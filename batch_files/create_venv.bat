@echo off
cd /d %~dp0..
echo [INFO]Creating virtual environment...
echo.
cmd /C "python -m venv .\dhrh-venv"
echo [INFO]Done.
echo.
pause