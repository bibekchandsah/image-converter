#!/usr/bin/env python3
"""
Build script for Image Converter GUI
Creates a standalone executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil

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

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable...")
    
    try:
        # Simple PyInstaller command without problematic version info
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name=ImageConverter",
            "--icon=icon.ico",
            "--add-data=icon.ico;.",
            "--add-data=icon.png;.",
            "--add-data=assets;assets",
            "--add-data=utils;utils",
            "--exclude-module=tkinter",
            "--exclude-module=matplotlib",
            "--exclude-module=numpy",
            "--exclude-module=scipy",
            "--exclude-module=pandas",
            "--clean",
            "--noconfirm",
            "main.py"
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
    
    # Step 3: Build executable
    if not build_executable():
        return False
    
    # Check if executable was created
    if os.path.exists("dist/ImageConverter.exe"):
        size_mb = os.path.getsize("dist/ImageConverter.exe") / (1024 * 1024)
        print(f"\n🎉 Build completed successfully!")
        print(f"✓ Executable: dist/ImageConverter.exe ({size_mb:.1f} MB)")
        print("\nThe executable is ready to distribute!")
        return True
    else:
        print("❌ Executable not found after build!")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    
    input("\nPress Enter to exit...")