@echo off
cd /d %~dp0..
echo [INFO]Installing packages...
echo.
cmd /C ".\dhrh-venv\Scripts\activate && pip install -r .\requirements.txt"
echo [INFO]Done.
echo.
pause