#!/bin/bash

echo "Image Converter GUI - Simple Build Script"
echo "=========================================="

# Check if PyInstaller is installed
python3 -c "import PyInstaller" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing PyInstaller..."
    pip3 install pyinstaller
fi

# Clean previous builds
rm -rf build dist

# Build the executable
echo "Building executable..."
pyinstaller --onefile --windowed --icon=icon.ico --name=ImageConverter \
    --add-data="icon.ico:." \
    --add-data="icon.png:." \
    --add-data="assets:assets" \
    --add-data="utils:utils" \
    main.py

if [ -f "dist/ImageConverter" ]; then
    echo ""
    echo "✓ Build completed successfully!"
    echo "✓ Executable created: dist/ImageConverter"
    echo ""
    echo "You can now distribute the ImageConverter executable."
else
    echo ""
    echo "❌ Build failed! Check the output above for errors."
fi