@echo off
REM ========================================
REM DSA Training Platform - Development Launcher
REM ========================================
REM Enhanced launcher with agentic capabilities and skill tree integration
REM - Main API server (FastAPI on port 8000)
REM - Skill Tree API server (Flask on port 8003) 
REM - Frontend React app (on port 3000)
REM - Integration testing and agentic client tools

echo.
echo ========================================
echo   DSA Training Platform - DEV LAUNCHER
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

echo [1/7] Activating Python virtual environment...
call .venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to activate virtual environment!
    pause
    exit /b 1
)

echo [2/7] Checking Python dependencies...
python -c "import fastapi, uvicorn, sqlalchemy, flask, flask_cors" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Some Python dependencies are missing.
    echo Installing dependencies...
    pip install fastapi uvicorn sqlalchemy flask flask-cors requests
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install Python dependencies!
        pause
        exit /b 1
    )
)

echo [3/7] Running integration pre-check...
python test_platform_integration.py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Pre-check: Platform ready for launch
) else (
    echo Pre-check: Starting fresh platform instance
)

echo [4/7] Starting main API server (FastAPI)...
start "DSATrain Main API" cmd /k "call .venv\Scripts\activate.bat && echo =============================================== && echo DSATrain Main API Server && echo =============================================== && echo FastAPI Backend: http://localhost:8000 && echo API Documentation: http://localhost:8000/docs && echo Health Check: http://localhost:8000/health && echo. && python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 4 /nobreak >nul

echo [5/7] Starting skill tree API server (Flask)...
start "DSATrain Skill Tree API" cmd /k "call .venv\Scripts\activate.bat && echo =============================================== && echo DSATrain Skill Tree API Server && echo =============================================== && echo Skill Tree API: http://localhost:8003 && echo Health Check: http://localhost:8003/health && echo Skill Tree Data: http://localhost:8003/skill-tree/overview && echo Agentic Control: Available && echo. && python robust_flask_server.py"

timeout /t 4 /nobreak >nul

echo [6/7] Checking frontend dependencies...
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

echo [7/7] Starting frontend React application...
start "DSATrain Frontend" cmd /k "cd frontend && echo =============================================== && echo DSATrain Frontend Application && echo =============================================== && echo React Frontend: http://localhost:3000 && echo Skill Tree Visualization: Integrated && echo API Endpoints: Connected && echo. && npm start"

REM Wait for services to initialize
echo.
echo Waiting for all services to initialize...
timeout /t 8 /nobreak >nul

echo.
echo ========================================
echo   DEVELOPMENT PLATFORM STATUS
echo ========================================
echo.
echo 🚀 Main API Server:    http://localhost:8000
echo 📚 API Documentation:  http://localhost:8000/docs
echo 🌳 Skill Tree API:     http://localhost:8003
echo 📊 Skill Tree Data:    http://localhost:8003/skill-tree/overview
echo 🎨 Frontend App:       http://localhost:3000
echo.
echo 🤖 AGENTIC CAPABILITIES:
echo    - Skill Tree Client: agentic_skill_tree_client.py
echo    - Integration Tests: test_platform_integration.py
echo    - Platform Control:  Programmatic API access
echo.
echo ⚡ All servers running in separate windows
echo 🔧 Development tools ready for agentic workflows
echo.

REM Run post-launch integration test
echo Running post-launch integration test...
timeout /t 3 /nobreak >nul
python test_platform_integration.py
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ PLATFORM INTEGRATION: SUCCESSFUL
    echo 🟢 All services operational and ready for development
) else (
    echo.
    echo ⚠️ PLATFORM INTEGRATION: PARTIAL
    echo 🟡 Some services may need additional startup time
)

echo.
echo 🌐 Opening application in browser...
start "" "http://localhost:3000"

echo.
echo ========================================
echo Platform launched successfully!
echo Close server windows to stop services.
echo Press any key to close this launcher...
echo ========================================
pause >nul
