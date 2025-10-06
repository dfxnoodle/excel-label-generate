@echo off
REM CUHK Label Generator - Automated Setup Script for Windows
REM
REM This script automates the complete setup process for the Label Generator
REM application on a new Windows machine.
REM
REM Usage:
REM   setup.bat              - Run the setup

setlocal enabledelayedexpansion

REM Configuration
set PYTHON_MIN_VERSION=3.11
set VENV_DIR=.venv

echo ===============================================================================
echo   CUHK Label Generator - Automated Setup (Windows)
echo ===============================================================================
echo.

REM Check if Python is installed
echo [Step 1/7] Checking Python installation...
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python %PYTHON_MIN_VERSION% or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Found Python %PYTHON_VERSION%
echo.

REM Check minimum version (simplified check)
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)

if %MAJOR% LSS 3 (
    echo [ERROR] Python version %PYTHON_VERSION% is too old!
    echo Minimum required version: %PYTHON_MIN_VERSION%
    pause
    exit /b 1
)

if %MAJOR% EQU 3 if %MINOR% LSS 11 (
    echo [ERROR] Python version %PYTHON_VERSION% is too old!
    echo Minimum required version: %PYTHON_MIN_VERSION%
    pause
    exit /b 1
)

REM Check pip
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip is not installed!
    echo Please reinstall Python with pip included.
    pause
    exit /b 1
)
echo [OK] pip is available
echo.

REM Create virtual environment
echo [Step 2/7] Setting up Python virtual environment...
echo.

if exist "%VENV_DIR%" (
    echo [WARNING] Virtual environment already exists at %VENV_DIR%
    echo.
    choice /C YN /M "Do you want to remove and recreate it"
    if !errorlevel! equ 1 (
        echo Removing existing virtual environment...
        rmdir /s /q "%VENV_DIR%"
    ) else (
        echo Using existing virtual environment
        goto :skip_venv_creation
    )
)

echo Creating virtual environment at %VENV_DIR%...
python -m venv "%VENV_DIR%"

if not exist "%VENV_DIR%" (
    echo [ERROR] Failed to create virtual environment!
    pause
    exit /b 1
)

echo [OK] Virtual environment created successfully
echo.

:skip_venv_creation

REM Install dependencies
echo [Step 3/7] Installing Python dependencies...
echo.

if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found!
    pause
    exit /b 1
)

echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)

echo [OK] Dependencies installed successfully
echo.

REM Verify project structure
echo [Step 4/7] Verifying project structure...
echo.

set ALL_DIRS_EXIST=1

if not exist "src" (
    echo [WARNING] Missing directory: src
    set ALL_DIRS_EXIST=0
)
if not exist "templates" (
    echo [WARNING] Missing directory: templates
    set ALL_DIRS_EXIST=0
)
if not exist "static" (
    echo [WARNING] Missing directory: static
    set ALL_DIRS_EXIST=0
)
if not exist "config" (
    echo [WARNING] Missing directory: config
    set ALL_DIRS_EXIST=0
)
if not exist "data" (
    echo [WARNING] Missing directory: data
    mkdir data
    echo [OK] Created data directory
    set ALL_DIRS_EXIST=1
)

if %ALL_DIRS_EXIST% equ 1 (
    echo [OK] All required directories exist
)
echo.

REM Check important files
echo [Step 5/7] Checking important files...
echo.

set ALL_FILES_EXIST=1

if exist "src\web_app.py" (echo   [OK] src\web_app.py) else (echo   [X] src\web_app.py ^(missing^) & set ALL_FILES_EXIST=0)
if exist "src\simple_labels.py" (echo   [OK] src\simple_labels.py) else (echo   [X] src\simple_labels.py ^(missing^) & set ALL_FILES_EXIST=0)
if exist "templates\index.html" (echo   [OK] templates\index.html) else (echo   [X] templates\index.html ^(missing^) & set ALL_FILES_EXIST=0)
if exist "templates\config.html" (echo   [OK] templates\config.html) else (echo   [X] templates\config.html ^(missing^) & set ALL_FILES_EXIST=0)
if exist "run_web.py" (echo   [OK] run_web.py) else (echo   [X] run_web.py ^(missing^) & set ALL_FILES_EXIST=0)
if exist "config\label_config.json" (echo   [OK] config\label_config.json) else (echo   [X] config\label_config.json ^(missing^) & set ALL_FILES_EXIST=0)

if %ALL_FILES_EXIST% equ 1 (
    echo [OK] All important files found
) else (
    echo [WARNING] Some files are missing - this may cause issues
)
echo.

REM Check data files
echo [Step 6/7] Checking data files...
echo.

set FOUND_EXCEL=0
for %%f in (data\*.xlsx data\*.xls) do (
    if exist "%%f" (
        echo [OK] Found Excel file: %%f
        set FOUND_EXCEL=1
    )
)

if %FOUND_EXCEL% equ 0 (
    echo [WARNING] No Excel files found in data\ directory
    echo You'll need to upload Excel files through the web interface
)

if exist "config\SimSun.ttf" (
    echo [OK] Font file found: config\SimSun.ttf
) else (
    echo [WARNING] Font file config\SimSun.ttf not found
    echo Chinese characters may not display correctly
    echo Please place SimSun.ttf in the config\ directory
)
echo.

REM Check configuration
echo [Step 7/7] Checking configuration...
echo.

if exist "config\label_config.json" (
    echo [OK] Configuration file exists: config\label_config.json
) else (
    echo [WARNING] Configuration file not found!
    echo Please ensure config\label_config.json exists before running the application
)
echo.

REM Show final instructions
echo ===============================================================================
echo   Setup Complete!
echo ===============================================================================
echo.
echo [OK] Python virtual environment created
echo [OK] Dependencies installed
echo [OK] Project structure verified
echo.
echo ===============================================================================
echo   Next Steps
echo ===============================================================================
echo.
echo 1. Activate the virtual environment:
echo    .venv\Scripts\activate.bat
echo.
echo 2. Run the web application:
echo    # Quick start (default port 8000)
echo    run_web.bat
echo.
echo    # Custom port
echo    run_web.bat --port 8002
echo.
echo    # Or directly with Python
echo    python run_web.py --port 8002
echo.
echo 3. Access the application:
echo    Local:   http://localhost:8000
echo.
echo 4. Documentation:
echo    - README.md                  - Main documentation
echo    - WEB_README.md             - Web application guide
echo    - QUICK_START.md            - Quick start guide
echo.
echo ===============================================================================
echo   Troubleshooting
echo ===============================================================================
echo.
echo If you encounter issues:
echo   1. Make sure you activate the virtual environment first
echo   2. Check that all dependencies installed: pip list
echo   3. Verify config\label_config.json exists
echo   4. Check that port 8000 (or your chosen port) is not in use
echo   5. Review logs for error messages
echo.
echo ===============================================================================
echo   Setup completed successfully! Happy label generating!
echo ===============================================================================
echo.

pause
