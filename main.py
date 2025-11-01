#!/usr/bin/env python3
"""
Image Converter GUI - Main Entry Point
A modern PySide6 application for converting and resizing images
"""

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from ui_mainwindow import ImageConverterWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Image Converter")
    app.setApplicationVersion("1.0")
    
    # Set application icon for taskbar and window
    def get_resource_path(relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    icon_paths = ["icon.ico", "icon.png"]
    for icon_name in icon_paths:
        icon_path = get_resource_path(icon_name)
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            if not icon.isNull():
                app.setWindowIcon(icon)
                break
    
    # Create and show main window
    window = ImageConverterWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()