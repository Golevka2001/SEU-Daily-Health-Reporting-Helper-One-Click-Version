@echo off
cd /d %~dp0..
echo [INFO]Installing chrome driver...
echo.
cmd /C ".\dhrh-venv\Scripts\activate && python .\chrome_driver_installer.py"
echo [INFO]Done.
echo.
pause