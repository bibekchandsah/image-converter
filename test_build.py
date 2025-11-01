#!/usr/bin/env python3
"""
Test script to verify the built executable works correctly
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def test_executable_exists():
    """Test if the executable was created"""
    exe_path = "dist/ImageConverter.exe"
    if os.path.exists(exe_path):
        print("✓ Executable found:", exe_path)
        
        # Get file size
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"✓ File size: {size_mb:.1f} MB")
        
        return True
    else:
        print("❌ Executable not found:", exe_path)
        return False

def test_executable_runs():
    """Test if the executable starts without errors"""
    exe_path = "dist/ImageConverter.exe"
    
    try:
        print("🧪 Testing executable startup...")
        
        # Start the executable
        process = subprocess.Popen([exe_path], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait a moment for it to start
        time.sleep(3)
        
        # Check if it's still running (good sign)
        if process.poll() is None:
            print("✓ Executable started successfully")
            
            # Terminate the process
            process.terminate()
            process.wait(timeout=5)
            print("✓ Executable terminated cleanly")
            return True
        else:
            # Process exited, check for errors
            stdout, stderr = process.communicate()
            print("❌ Executable exited immediately")
            if stderr:
                print("Error output:", stderr.decode())
            return False
            
    except Exception as e:
        print(f"❌ Error testing executable: {e}")
        return False

def test_dependencies():
    """Test if all required modules are available"""
    required_modules = [
        'PySide6',
        'PIL',
        'requests'
    ]
    
    print("🔍 Checking dependencies...")
    all_good = True
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module} available")
        except ImportError:
            print(f"❌ {module} missing")
            all_good = False
    
    return all_good

def main():
    """Run all tests"""
    print("🧪 Image Converter GUI - Build Test")
    print("=" * 40)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Executable Exists", test_executable_exists),
        ("Executable Runs", test_executable_runs),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n📊 Test Results:")
    print("-" * 30)
    
    all_passed = True
    for test_name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if not result:
            all_passed = False
    
    print("-" * 30)
    
    if all_passed:
        print("🎉 All tests passed! The executable is ready for distribution.")
    else:
        print("⚠️  Some tests failed. Please check the build process.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)