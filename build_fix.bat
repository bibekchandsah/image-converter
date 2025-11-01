@echo off
echo Image Converter GUI - Quick Fix Build
echo =====================================

echo Cleaning up problematic files...
if exist ImageConverter.spec del ImageConverter.spec
if exist version_info.txt del version_info.txt
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo Running fixed build script...
python build_simple_fixed.py

echo.
echo Build fix completed!
pause