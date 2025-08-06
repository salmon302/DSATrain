@echo off
REM ========================================
REM DSA Training Platform Environment Setup
REM ========================================
REM This batch file sets up the complete development environment:
REM - Creates Python virtual environment
REM - Installs Python dependencies
REM - Installs Node.js dependencies
REM - Runs database migrations

echo.
echo ========================================
echo   DSATrain Environment Setup
echo ========================================
echo.

REM Set the working directory to the script location
cd /d "%~dp0"

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.9+ from https://python.org/
    echo.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python version: %PYTHON_VERSION%

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed or not in PATH!
    echo Please install Node.js 16+ from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

REM Check Node.js version
for /f "tokens=1" %%i in ('node --version') do set NODE_VERSION=%%i
echo Found Node.js version: %NODE_VERSION%

echo.
echo [1/6] Creating Python virtual environment...
if exist ".venv" (
    echo Virtual environment already exists. Skipping creation.
) else (
    python -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
)

echo [2/6] Activating virtual environment...
call .venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to activate virtual environment!
    pause
    exit /b 1
)

echo [3/6] Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install Python dependencies!
    pause
    exit /b 1
)

echo [4/6] Installing frontend dependencies...
cd frontend
npm install
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install Node.js dependencies!
    cd ..
    pause
    exit /b 1
)
cd ..

echo [5/6] Setting up database...
REM Check if database exists, if not run migrations
if not exist "dsatrain_phase4.db" (
    echo Creating database and running migrations...
    alembic upgrade head
    if %ERRORLEVEL% NEQ 0 (
        echo WARNING: Database migration failed. You may need to set it up manually.
    ) else (
        echo Database setup completed.
    )
) else (
    echo Database already exists. Skipping initial setup.
    echo To update database schema, run: alembic upgrade head
)

echo [6/6] Running quick validation...
python -c "from src.api.main import app; print('✓ Backend imports successful')" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Backend validation failed. There may be missing dependencies.
) else (
    echo ✓ Backend validation passed
)

cd frontend
npm list react >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Frontend validation failed. React may not be properly installed.
) else (
    echo ✓ Frontend validation passed
)
cd ..

echo.
echo ========================================
echo     Environment Setup Complete!
echo ========================================
echo.
echo You can now run launch_dsatrain.bat to start the platform.
echo.
echo Quick reference:
echo - Backend API will run on:     http://localhost:8000
echo - API Documentation:          http://localhost:8000/docs
echo - Frontend will run on:       http://localhost:3000
echo.
echo To start manually:
echo   Backend:  call .venv\Scripts\activate.bat ^&^& python -m uvicorn src.api.main:app --reload
echo   Frontend: cd frontend ^&^& npm start
echo.
pause
