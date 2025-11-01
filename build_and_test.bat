@echo off
echo Image Converter GUI - Build and Test Script
echo =============================================

echo.
echo Step 1: Installing dependencies...
pip install -r requirements.txt

echo.
echo Step 2: Building executable...
python build_exe.py

echo.
echo Step 3: Testing build...
python test_build.py

echo.
echo Build and test process completed!
echo Check the output above for any errors.
echo.
pause