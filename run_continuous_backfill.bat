@echo off
REM Continuous Codeforces backfill automation
REM Based on successful recovery strategy: cookie + browser + optimized parameters

cd /d "C:\Users\salmo\Documents\GitHub\DSATrain"

REM Set cookie (replace with current cookie)
set "CF_COOKIE=JSESSIONID=8EAF044E1ADF10153D87F95D9E2A43C2; 39ce7=CF5Id0bR; cf_clearance=iNCbF4GuvOYF7YvBxiLYJlVoCtsvu1HOlfMaaTpgm3M-1755388506-1.2.1.1-OcxVLFArnOoV7aKJvI9xia97.DRxSGQtpxlDf5HloRBTpMLdZIz.FTQOOEWknOUm4aYm6ZoaAs3ZomCor3olOiW1C8W9g.B9C9bk_o47sUNzXyTvbAa7lMZTKr.9j5HEAV7kmNxcfM3pP5bMnCGFXUnroi.DeO8xXQHvg.1lAItFjrm8_vQwWUaYE8.rxc0AOlUWnVfBFXI1mP0MXq_3mP6p0OYX2Lta.ePd3FO3glQ"

REM Optimal parameters based on 100% success rate
set MAX_ITEMS=150
set CONCURRENCY=3
set DELAY=0.75

:BATCH_LOOP
echo [%DATE% %TIME%] Starting batch: max=%MAX_ITEMS%, c=%CONCURRENCY%, d=%DELAY%

REM Run batch
"C:/Users/salmo/Documents/GitHub/DSATrain/.venv/Scripts/python.exe" scripts/cf_bulk_backfill.py --max %MAX_ITEMS% --concurrency %CONCURRENCY% --delay %DELAY% --resume --proxy --browser --cookie "%CF_COOKIE%" >> logs/cf_backfill_run.log 2>&1

REM Check if we should continue (simple approach - run until manually stopped)
echo [%DATE% %TIME%] Batch completed, checking for more candidates...

REM Small delay between batches
timeout /t 10 /nobreak > nul

REM Loop back
goto BATCH_LOOP
