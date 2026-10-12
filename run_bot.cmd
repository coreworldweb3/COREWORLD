@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
rem Avoid inherited SSL key-log paths that are inaccessible in this environment.
set "SSLKEYLOGFILE="
if not exist ".venv\Scripts\python.exe" (
    echo Python environment missing. See docs/notion-course.md.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" "src\main.py"
pause
