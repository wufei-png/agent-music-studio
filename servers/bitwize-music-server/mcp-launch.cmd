@echo off
setlocal EnableExtensions EnableDelayedExpansion
for %%I in ("%~dp0..\..") do set "ROOT=%%~fI"
if exist "%ROOT%\.codex-plugin\plugin.json" (
  if defined AGENT_MUSIC_STUDIO_CODEX_VENV (
    set "CODEX_VENV=%AGENT_MUSIC_STUDIO_CODEX_VENV%"
  ) else (
    set "CODEX_VENV=%USERPROFILE%\.agent-music-studio\codex-venv"
  )
  set "CODEX_PYTHON=!CODEX_VENV!\Scripts\python.exe"
  set "BOOTSTRAP=!ROOT!\tools\bootstrap_codex_runtime.py"
  if not exist "!CODEX_PYTHON!" goto :codex_runtime_missing
  python "!BOOTSTRAP!" --venv "!CODEX_VENV!" --check --quiet
  if errorlevel 1 goto :codex_runtime_missing
  if not defined PLUGIN_ROOT set "PLUGIN_ROOT=!ROOT!"
  "!CODEX_PYTHON!" "%~dp0run.py" %*
  exit /b !errorlevel!
)

set "VENV=%USERPROFILE%\.bitwize-music\venv\Scripts\python.exe"
if exist "%VENV%" (
  "%VENV%" "%~dp0run.py" %*
) else (
  python "%~dp0run.py" %*
)
exit /b %errorlevel%

:codex_runtime_missing
echo Agent Music Studio Codex runtime is missing or stale. 1>&2
echo Run: python "!BOOTSTRAP!" --venv "!CODEX_VENV!" 1>&2
exit /b 1
