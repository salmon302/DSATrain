@echo off
REM ========================================
REM DSA Training Platform Development Utils
REM ========================================
REM Common development tasks for DSATrain

:MENU
echo.
echo ========================================
echo    DSATrain Development Utilities
echo ========================================
echo.
echo 1. Launch Full Platform
echo 2. Start Backend Only
echo 3. Start Frontend Only
echo 4. Run Database Migrations
echo 5. Reset Database
echo 6. Install/Update Dependencies
echo 7. Run Tests
echo 8. View Logs
echo 9. Open API Documentation
echo 0. Exit
echo.
set /p choice="Enter your choice (0-9): "

if "%choice%"=="1" goto LAUNCH_FULL
if "%choice%"=="2" goto START_BACKEND
if "%choice%"=="3" goto START_FRONTEND
if "%choice%"=="4" goto RUN_MIGRATIONS
if "%choice%"=="5" goto RESET_DATABASE
if "%choice%"=="6" goto UPDATE_DEPS
if "%choice%"=="7" goto RUN_TESTS
if "%choice%"=="8" goto VIEW_LOGS
if "%choice%"=="9" goto OPEN_DOCS
if "%choice%"=="0" goto EXIT

echo Invalid choice! Please try again.
goto MENU

:LAUNCH_FULL
echo Launching full platform...
call launch_dsatrain.bat
goto MENU

:START_BACKEND
echo Starting backend only...
call .venv\Scripts\activate.bat
echo Backend API starting on http://localhost:8000
echo API Documentation: http://localhost:8000/docs
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
goto MENU

:START_FRONTEND
echo Starting frontend only...
cd frontend
echo Frontend starting on http://localhost:3000
npm start
cd ..
goto MENU

:RUN_MIGRATIONS
echo Running database migrations...
call .venv\Scripts\activate.bat
alembic upgrade head
echo Migrations completed.
pause
goto MENU

:RESET_DATABASE
echo WARNING: This will delete all data in the database!
set /p confirm="Are you sure? (y/N): "
if /i "%confirm%"=="y" (
    if exist "dsatrain_phase4.db" del "dsatrain_phase4.db"
    call .venv\Scripts\activate.bat
    alembic upgrade head
    echo Database reset completed.
) else (
    echo Database reset cancelled.
)
pause
goto MENU

:UPDATE_DEPS
echo Updating dependencies...
call .venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt --upgrade
cd frontend
npm update
cd ..
echo Dependencies updated.
pause
goto MENU

:RUN_TESTS
echo Running tests...
call .venv\Scripts\activate.bat
python -m pytest tests/ -v
pause
goto MENU

:VIEW_LOGS
echo Opening logs directory...
if exist "logs" (
    start "" "logs"
) else (
    echo No logs directory found.
)
pause
goto MENU

:OPEN_DOCS
echo Opening API documentation...
start "" "http://localhost:8000/docs"
pause
goto MENU

:EXIT
echo Goodbye!
exit /b 0
