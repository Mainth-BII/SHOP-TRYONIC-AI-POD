@echo off
REM run_daily_smoke.bat
REM Chay daily smoke tests tren TEST env (mac dinh)
REM De chay PROD: run_daily_smoke.bat prod

set ENV=%1
if "%ENV%"=="" set ENV=test

echo === Daily Smoke Test - ENV=%ENV% ===
python -m pytest tests/production/daily/ -v --tb=short --env=%ENV% 2>&1
