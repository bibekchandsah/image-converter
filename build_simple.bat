@echo off
echo Image Converter GUI - Simple Build Script
echo ==========================================

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the executable
echo Building executable...
pyinstaller --onefile --windowed --icon=icon.ico --name=ImageConverter --add-data="icon.ico;." --add-data="icon.png;." --add-data="assets;assets" --add-data="utils;utils" --exclude-module=tkinter --exclude-module=matplotlib --exclude-module=numpy --clean --noconfirm main.py

if exist dist\ImageConverter.exe (
    echo.
    echo ✓ Build completed successfully!
    echo ✓ Executable created: dist\ImageConverter.exe
    echo.
    echo You can now distribute the ImageConverter.exe file.
    pause
) else (
    echo.
    echo ❌ Build failed! Check the output above for errors.
    pause
)