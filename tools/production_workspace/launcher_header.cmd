@echo off
setlocal EnableExtensions DisableDelayedExpansion
title Picross - Produktionsansicht
rem Eine Datei: Windowsstarter mit eingebettetem Python-Bootstrap.
set "PW_START_FILE=%~f0"
python -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)" >nul 2>nul
if not errorlevel 1 goto use_python
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)" >nul 2>nul
if not errorlevel 1 goto use_py
echo Python 3.11 oder neuer fehlt oder ist nicht ueber python bzw. py erreichbar.
pause
exit /b 2

:use_python
python -c "import os; p=os.environ['PW_START_FILE']; s=open(p,encoding='utf-8').read(); exec(compile(s.split('\n# === PICROSS_PYTHON_BEGIN ===\n',1)[1],p,'exec'))" %*
set "PW_EXIT=%ERRORLEVEL%"
goto finished

:use_py
py -3 -c "import os; p=os.environ['PW_START_FILE']; s=open(p,encoding='utf-8').read(); exec(compile(s.split('\n# === PICROSS_PYTHON_BEGIN ===\n',1)[1],p,'exec'))" %*
set "PW_EXIT=%ERRORLEVEL%"

:finished
if not "%PW_EXIT%"=="0" pause
exit /b %PW_EXIT%

# === PICROSS_PYTHON_BEGIN ===
