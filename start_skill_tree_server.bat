@echo off
title DSA Skill Tree Server (FastAPI)
echo Starting DSA Skill Tree Server (FastAPI)...
echo Port: 8002
echo Health: http://localhost:8002/health
echo Skill Tree: http://localhost:8002/skill-tree/overview
echo.

:restart
if exist ".venv\Scripts\activate.bat" (
	call .venv\Scripts\activate.bat
)
python -m uvicorn src.api.skill_tree_server:app --reload --host 0.0.0.0 --port 8002
if %ERRORLEVEL% EQU 0 goto end
echo Server crashed, restarting in 5 seconds...
timeout /t 5 /nobreak >nul
goto restart

:end
echo Server stopped normally.
pause
