@echo off
setlocal

set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%
set PYTHONSAFEPATH=1
set PYTHONPATH=%SCRIPT_DIR%

uv run --project "%SCRIPT_DIR%" -m app.main %*
