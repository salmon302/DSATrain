@echo off
REM ========================================
REM DSA Training Platform Stop Script
REM ========================================
REM This batch file stops all DSATrain related processes

echo.
echo ========================================
echo    Stopping DSATrain Platform
echo ========================================
echo.

echo Stopping backend API server (port 8000)...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing process on port 8000 with PID %%p
    taskkill /f /pid %%p 2>nul
)

echo Stopping skill tree server (port 8002)...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr :8002 ^| findstr LISTENING') do (
    echo Killing process on port 8002 with PID %%p
    taskkill /f /pid %%p 2>nul
)

echo Stopping frontend development server (port 3000)...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do (
    echo Killing process on port 3000 with PID %%p
    taskkill /f /pid %%p 2>nul
)

echo.
echo All DSATrain processes have been stopped.
echo.
pause
