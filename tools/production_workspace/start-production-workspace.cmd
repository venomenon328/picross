@echo off
setlocal
cd /d "%~dp0\..\.."
python -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)" >nul 2>nul
if errorlevel 1 goto use_py
python -m tools.production_workspace %*
set "PW_START_RESULT=%ERRORLEVEL%"
goto finished
:use_py
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)" >nul 2>nul
if errorlevel 1 (
  echo Python 3.11 oder neuer fehlt. Bitte gemaess Anleitung einrichten.
  pause
  exit /b 2
)
py -3 -m tools.production_workspace %*
set "PW_START_RESULT=%ERRORLEVEL%"
:finished
if not "%PW_START_RESULT%"=="0" pause
exit /b %PW_START_RESULT%
