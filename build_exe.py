#!/usr/bin/env python3
"""
Build script for Image Converter GUI
Creates a standalone executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed, install if not"""
    try:
        import PyInstaller
        print("✓ PyInstaller is already installed")
        return True
    except ImportError:
        print("⚠ PyInstaller not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller")
            return False

def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Cleaning {dir_name}/")
            shutil.rmtree(dir_name)

def create_spec_file():
    """Create PyInstaller spec file for advanced configuration"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('icon.ico', '.'),
        ('icon.png', '.'),
        ('assets', 'assets'),
        ('utils', 'utils'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'PIL._tkinter_finder',
        'requests.packages.urllib3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'jupyter',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ImageConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
'''
    
    with open('ImageConverter.spec', 'w') as f:
        f.write(spec_content)
    print("✓ Created PyInstaller spec file")

def create_version_info():
    """Create version info file for Windows executable"""
    version_info = '''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(2,0,0,0),
    prodvers=(2,0,0,0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Bibek'),
        StringStruct(u'FileDescription', u'Image Converter GUI - Advanced image conversion tool'),
        StringStruct(u'FileVersion', u'2.0.0.0'),
        StringStruct(u'InternalName', u'ImageConverter'),
        StringStruct(u'LegalCopyright', u'Copyright 2025 Bibek. All rights reserved.'),
        StringStruct(u'OriginalFilename', u'ImageConverter.exe'),
        StringStruct(u'ProductName', u'Image Converter GUI'),
        StringStruct(u'ProductVersion', u'2.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)
    print("✓ Created version info file")

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable...")
    
    try:
        # Use the spec file for building
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "ImageConverter.spec"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Build completed successfully!")
            return True
        else:
            print("❌ Build failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def create_portable_package():
    """Create a portable package with the executable"""
    if not os.path.exists("dist/ImageConverter.exe"):
        print("❌ Executable not found!")
        return False
    
    print("📦 Creating portable package...")
    
    # Create portable directory
    portable_dir = "ImageConverter_Portable"
    if os.path.exists(portable_dir):
        shutil.rmtree(portable_dir)
    
    os.makedirs(portable_dir)
    
    # Copy executable
    shutil.copy2("dist/ImageConverter.exe", portable_dir)
    
    # Copy documentation
    docs_to_copy = ["README.md", "INSTALLATION.md"]
    for doc in docs_to_copy:
        if os.path.exists(doc):
            shutil.copy2(doc, portable_dir)
    
    # Create a simple launcher script
    launcher_content = '''@echo off
echo Starting Image Converter GUI...
ImageConverter.exe
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit.
    pause >nul
)
'''
    
    with open(f"{portable_dir}/Launch_ImageConverter.bat", 'w') as f:
        f.write(launcher_content)
    
    print(f"✓ Portable package created in {portable_dir}/")
    return True

def main():
    """Main build process"""
    print("🚀 Image Converter GUI - Build Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ main.py not found! Please run this script from the project root directory.")
        return False
    
    # Step 1: Check PyInstaller
    if not check_pyinstaller():
        return False
    
    # Step 2: Clean previous builds
    clean_build_dirs()
    
    # Step 3: Create configuration files
    create_spec_file()
    create_version_info()
    
    # Step 4: Build executable
    if not build_executable():
        return False
    
    # Step 5: Create portable package
    if not create_portable_package():
        return False
    
    print("\n🎉 Build completed successfully!")
    print("\nOutput files:")
    print("- dist/ImageConverter.exe (standalone executable)")
    print("- ImageConverter_Portable/ (portable package)")
    print("\nThe executable is ready to distribute!")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)