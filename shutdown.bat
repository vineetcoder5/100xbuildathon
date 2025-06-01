@echo off
echo Stopping all running scripts...

REM Kill all instances of pythonw.exe (silent/background) and python.exe (if visible)
taskkill /F /IM pythonw.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1

echo All Python scripts terminated.

