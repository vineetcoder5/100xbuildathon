@echo off
REM %~dp0 expands to the directory that contains this batch file, including a trailing slash
set APPDIR=%~dp0

start "" /D "%APPDIR%" "%APPDIR%python_embed\python.exe" "%APPDIR%active_window_monitor.py"
start "" /D "%APPDIR%" "%APPDIR%python_embed\python.exe" "%APPDIR%file_launcher_monitor.py"
start "" /D "%APPDIR%" "%APPDIR%python_embed\python.exe" "%APPDIR%floating_button.py"
start "" /D "%APPDIR%" "%APPDIR%python_embed\python.exe" "%APPDIR%Active_window_path.py"
start "" /D "%APPDIR%" "%APPDIR%python_embed\python.exe" "%APPDIR%screenshot_sender.py"
start "" /D "%APPDIR%" "%APPDIR%python_embed\python.exe" "%APPDIR%main_server.py"
pause
