@echo off
REM Default port
if "%PORT%"=="" set PORT=8000

REM Parse command line arguments
:parse_args
if "%1"=="--port" (
    set PORT=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--reload" (
    set RELOAD_FLAG=--reload
    shift
    goto parse_args
)
if not "%1"=="" (
    echo Unknown option: %1
    echo Usage: run_web.bat [--port PORT] [--reload]
    pause
    exit /b 1
)

echo ======================================================================
echo Starting Label Generator Web Application...
echo ======================================================================
echo.
echo Open your browser and go to:
echo   * Local:   http://localhost:%PORT%
echo   * Network: http://YOUR-IP:%PORT%
echo.
echo Usage examples:
echo   run_web.bat --port 5000
echo   set PORT=3000 ^&^& run_web.bat
echo   run_web.bat --port 9000 --reload
echo.
echo Press Ctrl+C to stop the server
echo ======================================================================
echo.

python run_web.py --port %PORT% %RELOAD_FLAG%
pause