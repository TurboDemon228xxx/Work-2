@echo off
setlocal
if not defined WORK2_PYTHON set "WORK2_PYTHON=python"
pushd "%~dp0"
"%WORK2_PYTHON%" -m src %*
set "WORK2_STATUS=%ERRORLEVEL%"
popd
exit /b %WORK2_STATUS%
