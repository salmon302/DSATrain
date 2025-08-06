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

echo Stopping backend API server (uvicorn)...
taskkill /f /im "python.exe" /fi "WINDOWTITLE eq DSATrain Backend*" 2>nul
taskkill /f /im "uvicorn.exe" 2>nul

echo Stopping frontend development server (npm)...
taskkill /f /im "node.exe" /fi "WINDOWTITLE eq DSATrain Frontend*" 2>nul

echo Stopping any remaining Node.js processes from React dev server...
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq node.exe" /fo csv ^| find "node.exe"') do (
    for /f "tokens=1" %%j in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do (
        for /f "tokens=5" %%k in ("%%j") do (
            if "%%i" == "%%k" (
                taskkill /f /pid %%k 2>nul
            )
        )
    )
)

echo.
echo All DSATrain processes have been stopped.
echo.
pause
