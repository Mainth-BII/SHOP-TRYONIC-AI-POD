@echo off
cd /d d:\TEST_STUDIO\shop_tryonic_ai

echo.
echo ============================================================
echo   CHAY CRITICAL_001 -- Full Journey to Checkout (PROD)
echo ============================================================
echo.

pytest tests/production/test_critical_flows.py::TestProductionCriticalFlows::test_CRITICAL_001_full_journey_to_checkout --env=test -v -s --headed

echo.
echo ============================================================
echo   XONG. Nhan phim bat ky de dong...
echo ============================================================
pause
