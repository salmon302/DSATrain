@echo off
REM ========================================
REM DSA Training Platform Launcher
REM ========================================
REM This batch file launches the complete DSATrain platform:
REM - Backend API server (FastAPI on port 8000)
REM - Skill Tree API server (Flask on port 8003)
REM - Frontend React app (on port 3000)
REM - Opens browser to the application

echo.
echo ========================================
echo    DSA Training Platform Launcher
echo ========================================
echo.

REM Set the working directory to the script location
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup_environment.bat first to create the virtual environment.
    echo.
    pause
    exit /b 1
)

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed or not in PATH!
    echo Please install Node.js from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

REM Check if npm is installed
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: npm is not installed or not in PATH!
    echo Please install Node.js from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo [1/5] Activating Python virtual environment...
call .venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to activate virtual environment!
    pause
    exit /b 1
)

echo [2/5] Checking Python dependencies...
python -c "import fastapi, uvicorn, sqlalchemy" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Some Python dependencies are missing.
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install Python dependencies!
        pause
        exit /b 1
    )
)

echo [3/5] Checking frontend dependencies...
cd frontend
if not exist "node_modules" (
    echo Installing Node.js dependencies...
    npm install
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install Node.js dependencies!
        pause
        exit /b 1
    )
)
cd ..

echo [4/6] Starting backend API server...
start "DSATrain Backend" cmd /k "call .venv\Scripts\activate.bat && echo Starting FastAPI backend on http://localhost:8000 && echo API Documentation available at http://localhost:8000/docs && python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

echo [5/6] Starting skill tree API server...
start "DSATrain Skill Tree" cmd /k "call .venv\Scripts\activate.bat && echo Starting Skill Tree API on http://localhost:8003 && echo Skill Tree endpoint: http://localhost:8003/skill-tree/overview && python robust_flask_server.py"

REM Wait a moment for skill tree server to start
timeout /t 3 /nobreak >nul

echo [6/6] Starting frontend React application...
start "DSATrain Frontend" cmd /k "cd frontend && echo Starting React frontend on http://localhost:3000 && npm start"

REM Wait a moment for frontend to start
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo    DSATrain Platform is starting up!
echo ========================================
echo.
echo Backend API:      http://localhost:8000
echo API Docs:         http://localhost:8000/docs
echo Skill Tree API:   http://localhost:8003
echo Skill Tree Data:  http://localhost:8003/skill-tree/overview
echo Frontend App:     http://localhost:3000
echo.
echo All servers are running in separate windows.
echo Close those windows to stop the servers.
echo.

REM Open the frontend application in default browser
echo Opening application in browser...
start "" "http://localhost:3000"

echo.
echo Platform launched successfully!
echo Press any key to close this launcher window...
pause >nul
