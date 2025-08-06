@echo off
title DSA Skill Tree Server
echo Starting DSA Skill Tree Server...
echo Port: 8003
echo Health: http://localhost:8003/health
echo Skill Tree: http://localhost:8003/skill-tree/overview
echo.

:restart
"C:\Users\salmo\Documents\GitHub\DSATrain\.venv\Scripts\python.exe" "C:\Users\salmo\Documents\GitHub\DSATrain\robust_flask_server.py"
if %ERRORLEVEL% EQU 0 goto end
echo Server crashed, restarting in 5 seconds...
timeout /t 5 /nobreak >nul
goto restart

:end
echo Server stopped normally.
pause
