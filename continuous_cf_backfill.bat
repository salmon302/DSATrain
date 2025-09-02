@echo off
REM Optimized Continuous Codeforces Backfill
REM Based on successful recovery and optimization testing
REM 
REM SUCCESS PARAMETERS IDENTIFIED:
REM - Cookie authentication: ESSENTIAL
REM - Browser fallback: ESSENTIAL 
REM - Concurrency: 3 (optimal)
REM - Delay: 0.75s (optimal)
REM - Batch size: 100 (efficient)
REM - Proxy: Enabled for reliability

setlocal enabledelayedexpansion

cd /d "C:\Users\salmo\Documents\GitHub\DSATrain"

REM Current working cookie (update as needed)
set "CF_COOKIE=JSESSIONID=8EAF044E1ADF10153D87F95D9E2A43C2; 39ce7=CF5Id0bR; cf_clearance=iNCbF4GuvOYF7YvBxiLYJlVoCtsvu1HOlfMaaTpgm3M-1755388506-1.2.1.1-OcxVLFArnOoV7aKJvI9xia97.DRxSGQtpxlDf5HloRBTpMLdZIz.FTQOOEWknOUm4aYm6ZoaAs3ZomCor3olOiW1C8W9g.B9C9bk_o47sUNzXyTvbAa7lMZTKr.9j5HEAV7kmNxcfM3pP5bMnCGFXUnroi.DeO8xXQHvg.1lAItFjrm8_vQwWUaYE8.rxc0AOlUWnVfBFXI1mP0MXq_3mP6p0OYX2Lta.ePd3FO3glQ"

REM Optimal parameters from testing
set MAX_ITEMS=100
set CONCURRENCY=3
set DELAY=0.75
set BATCH_COUNT=0

echo ================================================================
echo CODEFORCES CONTINUOUS BACKFILL AUTOMATION
echo ================================================================
echo Start Time: %DATE% %TIME%
echo Parameters: max=%MAX_ITEMS%, concurrency=%CONCURRENCY%, delay=%DELAY%s
echo Cookie: MASKED (length ~500 chars)
echo ================================================================

:BATCH_LOOP
set /a BATCH_COUNT+=1
echo.
echo [BATCH %BATCH_COUNT%] %DATE% %TIME% - Starting batch...

REM Run batch with proven parameters
"C:/Users/salmo/Documents/GitHub/DSATrain/.venv/Scripts/python.exe" scripts/cf_bulk_backfill.py --max %MAX_ITEMS% --concurrency %CONCURRENCY% --delay %DELAY% --resume --proxy --browser --cookie "%CF_COOKIE%"

REM Log completion
echo [BATCH %BATCH_COUNT%] %DATE% %TIME% - Batch completed

REM Small pause between batches for politeness
echo Waiting 15 seconds before next batch...
timeout /t 15 /nobreak > nul

REM Continue loop
goto BATCH_LOOP

REM This script will run indefinitely until manually stopped
REM Stop with Ctrl+C when candidates reach 0 or when needed
