"""
Main Window UI for Image Converter
"""

import os
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QComboBox, QLineEdit, QProgressBar,
    QFileDialog, QMessageBox, QScrollArea, QCheckBox, QGroupBox,
    QSpinBox, QDoubleSpinBox, QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt, QThread, Signal, QMimeData
from PySide6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QFont, QClipboard, QKeySequence, QShortcut, QIcon
from converter import ImageConverter
from downloader import ImageDownloader

def get_app_icon():
    """Get application icon for dialogs"""
    def get_resource_path(relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        import sys
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    icon_names = ["icon.ico", "icon.png"]
    
    for icon_name in icon_names:
        icon_path = get_resource_path(icon_name)
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            if not icon.isNull():
                return icon
    return QIcon()  # Return empty icon if none found

class PreviewDialog(QDialog):
    def __init__(self, preview_data, dpi=300, quality=90, parent=None):
        super().__init__(parent)
        self.preview_data = preview_data  # List of (image_path, size, format, output_name) tuples
        self.dpi = dpi
        self.quality = quality
        self.setWindowTitle("Preview Before Saving")
        self.setModal(True)
        self.resize(800, 600)
        self.setup_dialog_icon()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Preview of images to be saved:")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #0078d4; margin-bottom: 5px;")
        layout.addWidget(title_label)
        
        # Conversion settings summary - always show user's selected settings
        if len(self.preview_data) > 0:
            format_name = self.preview_data[0][2]  # Get format from first item
            if format_name.lower() == 'webp':
                actual_quality = min(self.quality, 85)
                if actual_quality != self.quality:
                    settings_text = f"Settings: Quality {self.quality}% → {actual_quality}% (WebP) | DPI not supported | {len(self.preview_data)} files"
                else:
                    settings_text = f"Settings: Quality {self.quality}% (WebP) | DPI not supported | {len(self.preview_data)} files"
            elif format_name.lower() == 'ico':
                settings_text = f"Settings: Quality {self.quality}% (not used) | DPI not supported | {len(self.preview_data)} ICO files"
            elif format_name.lower() == 'png':
                settings_text = f"Settings: DPI {self.dpi} (metadata) | Quality {self.quality}% (compression) | {len(self.preview_data)} files"
            else:  # JPEG/JPG
                settings_text = f"Settings: DPI {self.dpi} | Quality {self.quality}% | {len(self.preview_data)} files"
        else:
            settings_text = f"Settings: DPI {self.dpi} | Quality {self.quality}% | 0 files"
        
        settings_label = QLabel(settings_text)
        settings_label.setStyleSheet("font-size: 11px; color: #888; margin-bottom: 10px;")
        layout.addWidget(settings_label)
        
        # Scroll area for previews
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        for i, (image_path, size, format_name, output_name, original_path) in enumerate(self.preview_data):
            # Create preview item
            item_frame = QGroupBox(f"Preview {i+1}")
            item_layout = QHBoxLayout(item_frame)
            
            # Image preview
            preview_size = 150  # Define preview size at the top
            try:
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    # Scale preview to reasonable size
                    scaled_pixmap = pixmap.scaled(preview_size, preview_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    
                    image_label = QLabel()
                    image_label.setPixmap(scaled_pixmap)
                    image_label.setAlignment(Qt.AlignCenter)
                    image_label.setStyleSheet("""
                        QLabel {
                            border: 1px solid #666;
                            background-color: #2b2b2b;
                            border-radius: 5px;
                            padding: 5px;
                        }
                    """)
                    item_layout.addWidget(image_label)
                else:
                    # Fallback if image can't be loaded
                    image_label = QLabel("Preview\nNot Available")
                    image_label.setAlignment(Qt.AlignCenter)
                    image_label.setMinimumSize(preview_size, preview_size)
                    image_label.setStyleSheet("""
                        QLabel {
                            border: 1px solid #666;
                            background-color: #2b2b2b;
                            color: #888;
                            border-radius: 5px;
                            padding: 5px;
                        }
                    """)
                    item_layout.addWidget(image_label)
            except Exception:
                # Error loading image
                image_label = QLabel("Error\nLoading\nPreview")
                image_label.setAlignment(Qt.AlignCenter)
                image_label.setMinimumSize(preview_size, preview_size)
                image_label.setStyleSheet("""
                    QLabel {
                        border: 1px solid #666;
                        background-color: #2b2b2b;
                        color: #888;
                        border-radius: 5px;
                        padding: 5px;
                    }
                """)
                item_layout.addWidget(image_label)
            
            # Info panel
            info_layout = QVBoxLayout()
            
            # File name
            name_label = QLabel(f"📄 File: {output_name}")
            name_label.setStyleSheet("font-weight: bold; color: #ffffff; margin-bottom: 5px;")
            info_layout.addWidget(name_label)
            
            # Dimensions
            if size == "original":
                try:
                    from PIL import Image
                    # Use original image path to get true original dimensions
                    with Image.open(original_path) as img:
                        orig_width, orig_height = img.size
                    
                    # Check if ICO format needs size optimization for original
                    if format_name.lower() == 'ico' and (orig_width > 256 or orig_height > 256):
                        # Show the optimized size for ICO
                        max_size = 256
                        if orig_width > orig_height:
                            opt_height = int(orig_height * max_size / orig_width)
                            opt_width = max_size
                        else:
                            opt_width = int(orig_width * max_size / orig_height)
                            opt_height = max_size
                        size_text = f"📐 Size: {orig_width} x {orig_height} → {opt_width} x {opt_height} pixels (Original)"
                    else:
                        size_text = f"📐 Size: {orig_width} x {orig_height} pixels (Original)"
                except:
                    size_text = "📐 Size: Original"
            else:
                if isinstance(size, tuple):
                    width, height = size
                    # Check if ICO size was optimized
                    if format_name.lower() == 'ico' and (width > 256 or height > 256):
                        # Show the optimized size
                        max_size = 256
                        if width > height:
                            opt_height = int(height * max_size / width)
                            opt_width = max_size
                        else:
                            opt_width = int(width * max_size / height)
                            opt_height = max_size
                        size_text = f"📐 Size: {width} x {height} → {opt_width} x {opt_height} pixels"
                    else:
                        size_text = f"📐 Size: {width} x {height} pixels"
                else:
                    size_text = f"📐 Size: {size}"
            
            size_label = QLabel(size_text)
            size_label.setStyleSheet("color: #cccccc; margin-bottom: 3px;")
            info_layout.addWidget(size_label)
            
            # Format
            format_label = QLabel(f"🎨 Format: {format_name.upper()}")
            format_label.setStyleSheet("color: #cccccc; margin-bottom: 3px;")
            info_layout.addWidget(format_label)
            
            # DPI information (show for all formats with appropriate notes)
            if format_name.lower() in ['png', 'jpeg', 'jpg']:
                if format_name.lower() == 'png':
                    dpi_text = f"🔍 DPI: {self.dpi} (metadata only)"
                else:
                    dpi_text = f"🔍 DPI: {self.dpi}"
                dpi_label = QLabel(dpi_text)
                dpi_label.setStyleSheet("color: #cccccc; margin-bottom: 3px;")
                info_layout.addWidget(dpi_label)
            elif format_name.lower() == 'webp':
                # WebP doesn't support DPI metadata
                dpi_label = QLabel(f"🔍 DPI: {self.dpi} (not supported in WebP)")
                dpi_label.setStyleSheet("color: #888; margin-bottom: 3px; font-style: italic;")
                info_layout.addWidget(dpi_label)
            elif format_name.lower() == 'ico':
                # ICO doesn't support DPI metadata
                dpi_label = QLabel(f"🔍 DPI: {self.dpi} (not supported in ICO)")
                dpi_label.setStyleSheet("color: #888; margin-bottom: 3px; font-style: italic;")
                info_layout.addWidget(dpi_label)
            
            # Quality information - always show user's selected quality
            if format_name.lower() in ['jpeg', 'jpg']:
                quality_text = f"⚡ Quality: {self.quality}%"
                quality_label = QLabel(quality_text)
                quality_label.setStyleSheet("color: #cccccc; margin-bottom: 3px;")
                info_layout.addWidget(quality_label)
            elif format_name.lower() == 'webp':
                # For WebP, show both user setting and actual used quality
                actual_quality = min(self.quality, 85)
                if actual_quality == self.quality:
                    quality_text = f"⚡ Quality: {self.quality}% (Fast compression)"
                else:
                    quality_text = f"⚡ Quality: {self.quality}% → {actual_quality}% (WebP optimized)"
                quality_label = QLabel(quality_text)
                quality_label.setStyleSheet("color: #cccccc; margin-bottom: 3px;")
                info_layout.addWidget(quality_label)
                
                # Add note about WebP compression
                webp_note = QLabel("📝 WebP: Modern format with superior compression")
                webp_note.setStyleSheet("color: #666; font-size: 10px; margin-bottom: 3px;")
                info_layout.addWidget(webp_note)
            elif format_name.lower() == 'png':
                # PNG: Show user's quality setting and compression level
                if self.quality >= 90:
                    compression_info = "Low compression"
                elif self.quality >= 70:
                    compression_info = "Medium compression"
                else:
                    compression_info = "High compression"
                
                quality_text = f"⚡ Quality: {self.quality}% ({compression_info})"
                quality_label = QLabel(quality_text)
                quality_label.setStyleSheet("color: #cccccc; margin-bottom: 3px;")
                info_layout.addWidget(quality_label)
            elif format_name.lower() == 'ico':
                # ICO: Show user's quality setting but note it doesn't apply
                quality_text = f"⚡ Quality: {self.quality}% (lossless icon format)"
                quality_label = QLabel(quality_text)
                quality_label.setStyleSheet("color: #888; margin-bottom: 3px; font-style: italic;")
                info_layout.addWidget(quality_label)
                
                # Add note about ICO format
                if isinstance(size, tuple):
                    width, height = size
                    if width <= 48 and height <= 48:
                        ico_note = QLabel("📝 ICO: Optimal size for Windows icons")
                    elif width <= 128 and height <= 128:
                        ico_note = QLabel("📝 ICO: Good for high-DPI displays")
                    elif width <= 256 and height <= 256:
                        ico_note = QLabel("📝 ICO: Maximum reliable size")
                    elif width > 256 or height > 256:
                        ico_note = QLabel("📝 ICO: Size reduced to 256x256 (PIL limitation)")
                    else:
                        ico_note = QLabel("📝 ICO: Good size for compatibility")
                elif size == "original":
                    # Check original image size for ICO format note using original path
                    try:
                        from PIL import Image
                        with Image.open(original_path) as img:
                            orig_width, orig_height = img.size
                        if orig_width > 256 or orig_height > 256:
                            ico_note = QLabel("📝 ICO: Original size reduced to 256x256 (PIL limitation)")
                        else:
                            ico_note = QLabel("📝 ICO: Original size, good compatibility")
                    except:
                        ico_note = QLabel("📝 ICO: Windows icon format, max 256x256 reliable")
                else:
                    ico_note = QLabel("📝 ICO: Windows icon format, max 256x256 reliable")
                ico_note.setStyleSheet("color: #666; font-size: 10px; margin-bottom: 3px;")
                info_layout.addWidget(ico_note)
            
            # File size estimate (if possible)
            try:
                import os
                if os.path.exists(image_path):
                    file_size = os.path.getsize(image_path)
                    if file_size < 1024:
                        size_str = f"{file_size} B"
                    elif file_size < 1024 * 1024:
                        size_str = f"{file_size / 1024:.1f} KB"
                    else:
                        size_str = f"{file_size / (1024 * 1024):.1f} MB"
                    
                    file_size_text = f"💾 File size: {size_str}"
                    if format_name.lower() == 'ico':
                        file_size_text += " (varies by icon size)"
                    file_size_label = QLabel(file_size_text)
                    file_size_label.setStyleSheet("color: #888; font-size: 11px;")
                    info_layout.addWidget(file_size_label)
            except:
                pass
            
            info_layout.addStretch()
            item_layout.addLayout(info_layout)
            
            scroll_layout.addWidget(item_frame)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(400)
        layout.addWidget(scroll_area)
        
        # Summary
        summary_label = QLabel(f"Total files to be saved: {len(self.preview_data)}")
        summary_label.setStyleSheet("font-weight: bold; color: #0078d4; margin-top: 10px;")
        layout.addWidget(summary_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #666;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #777;
            }
        """)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
        save_btn = QPushButton("💾 Save All Images")
        save_btn.clicked.connect(self.accept)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def closeEvent(self, event):
        """Clean up temporary preview files when dialog is closed"""
        self.cleanup_temp_files()
        super().closeEvent(event)
    
    def reject(self):
        """Clean up temporary files when dialog is cancelled"""
        self.cleanup_temp_files()
        super().reject()
    
    def accept(self):
        """Clean up temporary files when dialog is accepted"""
        self.cleanup_temp_files()
        super().accept()
    
    def cleanup_temp_files(self):
        """Remove temporary preview files"""
        import os
        for temp_path, _, _, _, _ in self.preview_data:
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception:
                pass  # Ignore cleanup errors
    
    def setup_dialog_icon(self):
        """Setup dialog icon to match main window"""
        def get_resource_path(relative_path):
            """Get absolute path to resource, works for dev and for PyInstaller"""
            import sys
            try:
                # PyInstaller creates a temp folder and stores path in _MEIPASS
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)
        
        icon_names = ["icon.ico", "icon.png"]
        
        for icon_name in icon_names:
            icon_path = get_resource_path(icon_name)
            if os.path.exists(icon_path):
                icon = QIcon(icon_path)
                if not icon.isNull():
                    self.setWindowIcon(icon)
                    break

class CustomSizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Custom Size")
        self.setModal(True)
        self.resize(350, 200)
        self.setup_dialog_icon()
        
        layout = QVBoxLayout()
        
        # Unit selection
        unit_layout = QHBoxLayout()
        unit_layout.addWidget(QLabel("Unit:"))
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["Pixels", "Centimeters", "Inches"])
        self.unit_combo.setCurrentText("Pixels")
        self.unit_combo.currentTextChanged.connect(self.on_unit_changed)
        unit_layout.addWidget(self.unit_combo)
        layout.addLayout(unit_layout)
        
        # Width input
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Width:"))
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(0.1, 10000)
        self.width_spin.setValue(512)
        self.width_spin.setDecimals(1)
        self.width_spin.valueChanged.connect(self.update_pixel_preview)
        width_layout.addWidget(self.width_spin)
        self.width_unit_label = QLabel("px")
        width_layout.addWidget(self.width_unit_label)
        layout.addLayout(width_layout)
        
        # Height input
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Height:"))
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(0.1, 10000)
        self.height_spin.setValue(512)
        self.height_spin.setDecimals(1)
        self.height_spin.valueChanged.connect(self.update_pixel_preview)
        height_layout.addWidget(self.height_spin)
        self.height_unit_label = QLabel("px")
        height_layout.addWidget(self.height_unit_label)
        layout.addLayout(height_layout)
        
        # DPI input (for cm/inch conversions)
        dpi_layout = QHBoxLayout()
        dpi_layout.addWidget(QLabel("DPI:"))
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(72, 600)
        self.dpi_spin.setValue(300)
        self.dpi_spin.valueChanged.connect(self.update_pixel_preview)
        dpi_layout.addWidget(self.dpi_spin)
        self.dpi_label = QLabel("(for cm/inch conversion)")
        self.dpi_label.setStyleSheet("color: #888; font-size: 10px;")
        dpi_layout.addWidget(self.dpi_label)
        layout.addLayout(dpi_layout)
        
        # Preview label
        self.preview_label = QLabel("Size in pixels: 512 x 512")
        self.preview_label.setStyleSheet("color: #0078d4; font-weight: bold; padding: 5px;")
        layout.addWidget(self.preview_label)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
        # Initialize unit display
        self.on_unit_changed("Pixels")
    
    def on_unit_changed(self, unit):
        """Handle unit change and update UI accordingly"""
        # Store current pixel values for conversion
        current_width_px = self.get_current_width_pixels()
        current_height_px = self.get_current_height_pixels()
        
        if unit == "Pixels":
            self.width_unit_label.setText("px")
            self.height_unit_label.setText("px")
            self.dpi_spin.setEnabled(False)
            self.dpi_label.setVisible(False)
            self.width_spin.setRange(1, 10000)
            self.height_spin.setRange(1, 10000)
            self.width_spin.setDecimals(0)
            self.height_spin.setDecimals(0)
            self.width_spin.setSuffix("")
            self.height_spin.setSuffix("")
            self.width_spin.setValue(current_width_px)
            self.height_spin.setValue(current_height_px)
        elif unit == "Centimeters":
            self.width_unit_label.setText("cm")
            self.height_unit_label.setText("cm")
            self.dpi_spin.setEnabled(True)
            self.dpi_label.setVisible(True)
            self.width_spin.setRange(0.1, 100)
            self.height_spin.setRange(0.1, 100)
            self.width_spin.setDecimals(1)
            self.height_spin.setDecimals(1)
            self.width_spin.setSuffix(" cm")
            self.height_spin.setSuffix(" cm")
            # Convert pixels to cm
            dpi = self.dpi_spin.value()
            width_cm = round(current_width_px / dpi * 2.54, 1)
            height_cm = round(current_height_px / dpi * 2.54, 1)
            self.width_spin.setValue(width_cm)
            self.height_spin.setValue(height_cm)
        elif unit == "Inches":
            self.width_unit_label.setText("in")
            self.height_unit_label.setText("in")
            self.dpi_spin.setEnabled(True)
            self.dpi_label.setVisible(True)
            self.width_spin.setRange(0.1, 40)
            self.height_spin.setRange(0.1, 40)
            self.width_spin.setDecimals(2)
            self.height_spin.setDecimals(2)
            self.width_spin.setSuffix(" in")
            self.height_spin.setSuffix(" in")
            # Convert pixels to inches
            dpi = self.dpi_spin.value()
            width_in = round(current_width_px / dpi, 2)
            height_in = round(current_height_px / dpi, 2)
            self.width_spin.setValue(width_in)
            self.height_spin.setValue(height_in)
        
        self.update_pixel_preview()
    
    def get_current_width_pixels(self):
        """Get current width in pixels regardless of unit"""
        unit = self.unit_combo.currentText()
        width_val = self.width_spin.value()
        
        if unit == "Pixels":
            return int(width_val)
        elif unit == "Centimeters":
            dpi = self.dpi_spin.value()
            return int(width_val * dpi / 2.54)
        elif unit == "Inches":
            dpi = self.dpi_spin.value()
            return int(width_val * dpi)
        return 512  # fallback
    
    def get_current_height_pixels(self):
        """Get current height in pixels regardless of unit"""
        unit = self.unit_combo.currentText()
        height_val = self.height_spin.value()
        
        if unit == "Pixels":
            return int(height_val)
        elif unit == "Centimeters":
            dpi = self.dpi_spin.value()
            return int(height_val * dpi / 2.54)
        elif unit == "Inches":
            dpi = self.dpi_spin.value()
            return int(height_val * dpi)
        return 512  # fallback
    
    def update_pixel_preview(self):
        """Update the pixel preview based on current unit and values"""
        unit = self.unit_combo.currentText()
        width_val = self.width_spin.value()
        height_val = self.height_spin.value()
        
        if unit == "Pixels":
            width_px = width_val
            height_px = height_val
        elif unit == "Centimeters":
            dpi = self.dpi_spin.value()
            width_px = int(width_val * dpi / 2.54)
            height_px = int(height_val * dpi / 2.54)
        elif unit == "Inches":
            dpi = self.dpi_spin.value()
            width_px = int(width_val * dpi)
            height_px = int(height_val * dpi)
        
        self.preview_label.setText(f"Size in pixels: {width_px} x {height_px}")
    
    def get_size(self):
        """Return size in pixels regardless of input unit"""
        unit = self.unit_combo.currentText()
        width_val = self.width_spin.value()
        height_val = self.height_spin.value()
        
        if unit == "Pixels":
            return (width_val, height_val)
        elif unit == "Centimeters":
            dpi = self.dpi_spin.value()
            width_px = int(width_val * dpi / 2.54)
            height_px = int(height_val * dpi / 2.54)
            return (width_px, height_px)
        elif unit == "Inches":
            dpi = self.dpi_spin.value()
            width_px = int(width_val * dpi)
            height_px = int(height_val * dpi)
            return (width_px, height_px)
    
    def setup_dialog_icon(self):
        """Setup dialog icon to match main window"""
        def get_resource_path(relative_path):
            """Get absolute path to resource, works for dev and for PyInstaller"""
            import sys
            try:
                # PyInstaller creates a temp folder and stores path in _MEIPASS
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)
        
        icon_names = ["icon.ico", "icon.png"]
        
        for icon_name in icon_names:
            icon_path = get_resource_path(icon_name)
            if os.path.exists(icon_path):
                icon = QIcon(icon_path)
                if not icon.isNull():
                    self.setWindowIcon(icon)
                    break

class DropArea(QLabel):
    file_dropped = Signal(str)
    click_to_browse = Signal()
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setText("Drag & Drop Image Here\nor\nClick to Select File\nor\nPress Ctrl+V to Paste")
        self.setCursor(Qt.PointingHandCursor)  # Show pointer cursor
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #666;
                border-radius: 10px;
                background-color: #2b2b2b;
                color: #cccccc;
                font-size: 14px;
                padding: 40px;
                min-height: 150px;
            }
            QLabel:hover {
                border-color: #0078d4;
                background-color: #3a3a3a;
                color: #ffffff;
            }
        """)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            url = urls[0]
            
            # Check if it's a local file
            if url.isLocalFile():
                file_path = url.toLocalFile()
                if self.is_image_file(file_path):
                    event.acceptProposedAction()
                    self.setStyleSheet(self.styleSheet().replace("#2b2b2b", "#3a3a3a"))
            # Check if it's a web URL with image extension
            elif url.scheme() in ['http', 'https']:
                url_string = url.toString()
                if self.is_image_url(url_string):
                    event.acceptProposedAction()
                    self.setStyleSheet(self.styleSheet().replace("#2b2b2b", "#3a3a3a"))
        # Also check for image data directly
        elif event.mimeData().hasImage():
            event.acceptProposedAction()
            self.setStyleSheet(self.styleSheet().replace("#2b2b2b", "#3a3a3a"))
    
    def dragLeaveEvent(self, event):
        self.setStyleSheet(self.styleSheet().replace("#3a3a3a", "#2b2b2b"))
    
    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            url = urls[0]
            
            # Handle local files
            if url.isLocalFile():
                file_path = url.toLocalFile()
                if self.is_image_file(file_path):
                    self.file_dropped.emit(file_path)
                    event.acceptProposedAction()
            # Handle web URLs
            elif url.scheme() in ['http', 'https']:
                url_string = url.toString()
                if self.is_image_url(url_string):
                    # Emit the URL for download
                    self.file_dropped.emit(url_string)
                    event.acceptProposedAction()
        # Handle direct image data
        elif event.mimeData().hasImage():
            # Save the image data to a temporary file
            image = event.mimeData().imageData()
            if image:
                import tempfile
                import uuid
                temp_file = tempfile.gettempdir() + f"/dropped_image_{uuid.uuid4().hex[:8]}.png"
                if image.save(temp_file):
                    self.file_dropped.emit(temp_file)
                    event.acceptProposedAction()
        
        self.setStyleSheet(self.styleSheet().replace("#3a3a3a", "#2b2b2b"))
    
    def mousePressEvent(self, event):
        """Handle mouse click to open file browser"""
        if event.button() == Qt.LeftButton:
            self.click_to_browse.emit()
        super().mousePressEvent(event)
    
    def is_image_file(self, file_path):
        valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.webp', '.gif', '.ico', '.tiff', '.heic'}
        return Path(file_path).suffix.lower() in valid_extensions
    
    def is_image_url(self, url_string):
        """Check if URL points to an image file"""
        valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.webp', '.gif', '.ico', '.tiff', '.heic'}
        # Remove query parameters and fragments
        url_path = url_string.split('?')[0].split('#')[0]
        return any(url_path.lower().endswith(ext) for ext in valid_extensions)

class ImageConverterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.save_location = str(Path.home() / "Downloads")
        self.custom_size = (512, 512)
        
        self.setWindowTitle("Image Converter")
        self.setGeometry(100, 100, 800, 700)
        self.setup_window_icon()
        
        self.setup_ui()
        self.setup_connections()
        self.setup_clipboard()
    
    def resizeEvent(self, event):
        """Handle window resize to update image preview"""
        super().resizeEvent(event)
        # Reload image if one is currently loaded to fit new size
        if hasattr(self, 'current_image_path') and self.current_image_path:
            self.load_image(self.current_image_path)
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Input Section
        input_group = QGroupBox("Image Input")
        input_layout = QVBoxLayout(input_group)
        
        # Drop area (now clickable)
        self.drop_area = DropArea()
        input_layout.addWidget(self.drop_area)
        
        # URL input
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Image URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com/image.jpg")
        url_layout.addWidget(self.url_input)
        self.fetch_btn = QPushButton("🌐 Fetch")
        url_layout.addWidget(self.fetch_btn)
        input_layout.addLayout(url_layout)
        
        main_layout.addWidget(input_group)
        
        # Main content area - Two column layout
        content_layout = QHBoxLayout()
        
        # Left column - Preview Section
        left_column = QVBoxLayout()
        preview_group = QGroupBox("Image Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        # Direct label without scroll area for responsive display
        self.preview_label = QLabel("No image selected")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(400, 300)
        self.preview_label.setScaledContents(False)  # Maintain aspect ratio
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 1px solid #555;
                background-color: #2b2b2b;
                color: #ffffff;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        preview_layout.addWidget(self.preview_label)
        
        left_column.addWidget(preview_group)
        content_layout.addLayout(left_column, 1)  # Give left column more space
        
        # Right column - Options Section
        right_column = QVBoxLayout()
        
        # Format selection
        format_group = QGroupBox("Output Format")
        format_layout = QVBoxLayout(format_group)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPEG", "JPG", "WebP", "ICO"])
        self.format_combo.setMinimumHeight(35)
        format_layout.addWidget(self.format_combo)
        
        # Resize mode controls
        resize_mode_layout = QHBoxLayout()
        
        # Lock aspect ratio checkbox (now controls resize mode dropdown)
        self.lock_aspect_ratio = QCheckBox("🔒 Lock Aspect Ratio")
        self.lock_aspect_ratio.setChecked(False)  # Default to unchecked (stretch mode)
        resize_mode_layout.addWidget(self.lock_aspect_ratio)
        
        # Resize mode dropdown
        self.resize_mode_combo = QComboBox()
        self.resize_mode_combo.addItems(["Stretch", "Crop", "Fit"])
        self.resize_mode_combo.setCurrentText("Stretch")  # Default mode
        self.resize_mode_combo.setEnabled(False)  # Disabled when aspect ratio is unlocked
        self.resize_mode_combo.setMinimumHeight(25)
        self.resize_mode_combo.setStyleSheet("""
            QComboBox {
                background-color: #2b2b2b;
                color: #cccccc;
                border: 1px solid #666;
                border-radius: 3px;
                padding: 3px;
                font-size: 11px;
            }
            QComboBox:disabled {
                background-color: #1a1a1a;
                color: #666;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)
        
        # Set tooltips
        self.resize_mode_combo.setItemData(0, "Image will stretch to match the new size", Qt.ToolTipRole)
        self.resize_mode_combo.setItemData(1, "Image will match the new size and leftovers will be cropped", Qt.ToolTipRole)
        self.resize_mode_combo.setItemData(2, "Image will fit completely inside the new size and the rest will be painted with background color", Qt.ToolTipRole)
        
        resize_mode_layout.addWidget(self.resize_mode_combo)
        format_layout.addLayout(resize_mode_layout)
        
        # DPI (Resolution) input
        dpi_layout = QHBoxLayout()
        dpi_label = QLabel("Resolution (DPI):")
        dpi_label.setStyleSheet("color: #cccccc; font-size: 12px;")
        dpi_layout.addWidget(dpi_label)
        
        self.dpi_spinbox = QSpinBox()
        self.dpi_spinbox.setRange(72, 600)  # Common DPI range
        self.dpi_spinbox.setValue(300)  # Default to 300 DPI (professional printing)
        self.dpi_spinbox.setSuffix(" dpi")
        self.dpi_spinbox.setMinimumHeight(25)
        self.dpi_spinbox.valueChanged.connect(self.on_dpi_changed)
        # Use default system styling for better arrow visibility
        self.dpi_spinbox.setToolTip("Indicates how many dots will be drawn on each inch\nwhen printing this image.\n300dpi is the quality used for most professional printing.\nDoesn't affect how an image is seen on screens.")
        
        dpi_layout.addWidget(self.dpi_spinbox)
        format_layout.addLayout(dpi_layout)
        
        # Quality input
        quality_layout = QHBoxLayout()
        quality_label = QLabel("Quality (%):")
        quality_label.setStyleSheet("color: #cccccc; font-size: 12px;")
        quality_layout.addWidget(quality_label)
        
        self.quality_spinbox = QSpinBox()
        self.quality_spinbox.setRange(1, 100)  # Quality range 1-100%
        self.quality_spinbox.setValue(90)  # Default to 90% (good trade-off)
        self.quality_spinbox.setSuffix("%")
        self.quality_spinbox.setMinimumHeight(25)
        # Use default system styling for better arrow visibility
        self.quality_spinbox.setToolTip("0% quality will result in the smallest file, but the ugliest image.\n100% quality will result in a bigger file, but a great image.\nQualities around 70% or 90% are usually a great trade-off.")
        
        quality_layout.addWidget(self.quality_spinbox)
        format_layout.addLayout(quality_layout)
        right_column.addWidget(format_group)
        
        # Size selection
        size_group = QGroupBox("Resize Options")
        size_main_layout = QVBoxLayout(size_group)
        
        # Unit selection for resize options
        unit_layout = QHBoxLayout()
        unit_label = QLabel("Unit:")
        unit_label.setStyleSheet("color: #cccccc; font-weight: bold; font-size: 12px;")
        unit_layout.addWidget(unit_label)
        self.resize_unit_combo = QComboBox()
        self.resize_unit_combo.addItems(["Pixels", "Centimeters", "Inches"])
        self.resize_unit_combo.setCurrentText("Pixels")
        self.resize_unit_combo.currentTextChanged.connect(self.on_resize_unit_changed)
        self.resize_unit_combo.setMinimumHeight(25)
        self.resize_unit_combo.setStyleSheet("""
            QComboBox {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #666;
                border-radius: 3px;
                padding: 3px 8px;
                font-size: 12px;
            }
            QComboBox:hover {
                border-color: #0078d4;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)
        unit_layout.addWidget(self.resize_unit_combo)
        unit_layout.addStretch()
        size_main_layout.addLayout(unit_layout)
        
        # Size checkboxes
        size_layout = QGridLayout()
        
        self.size_checkboxes = {}
        self.original_sizes = [
            ("Original", "original"),
            ("16x16", (16, 16)),
            ("32x32", (32, 32)),
            ("48x48", (48, 48)),
            ("128x128", (128, 128)),
            ("150x150", (150, 150)),
            ("192x192", (192, 192)),
            ("512x512", (512, 512)),
            ("Custom", "custom")
        ]
        
        # Create 3x3 grid layout
        for i, (label, value) in enumerate(self.original_sizes):
            row = i // 3
            col = i % 3
            checkbox = QCheckBox(label)
            if label == "Original":
                checkbox.setChecked(True)
            self.size_checkboxes[value] = checkbox
            size_layout.addWidget(checkbox, row, col)
        
        size_main_layout.addLayout(size_layout)
        right_column.addWidget(size_group)
        
        # Save location group
        save_group = QGroupBox("Save to:")
        save_layout = QVBoxLayout(save_group)
        
        # Path display
        self.save_location_label = QLabel(self.save_location)
        self.save_location_label.setStyleSheet("""
            QLabel {
                border: 1px solid #555; 
                padding: 3px;
                background-color: #2b2b2b;
                color: #ffffff;
                border-radius: 5px;
                min-height: 15px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)
        save_layout.addWidget(self.save_location_label)
        
        # Choose folder button
        self.choose_location_btn = QPushButton("📂 Choose Folder")
        self.choose_location_btn.setMinimumHeight(25)
        self.choose_location_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 1px solid #666;
                border-radius: 5px;
                padding: 3px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
                border-color: #777;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
        """)
        save_layout.addWidget(self.choose_location_btn)
        
        right_column.addWidget(save_group)
        right_column.addStretch()  # Add stretch to push content to top
        
        content_layout.addLayout(right_column, 0)  # Right column takes less space
        main_layout.addLayout(content_layout)
        
        # Convert button and progress
        convert_layout = QHBoxLayout()
        convert_layout.addStretch()  # Add stretch before buttons to center them
        
        self.convert_btn = QPushButton("🔄 Convert Image(s)")
        self.convert_btn.setMinimumHeight(35)  # Reduced from 50 to 35
        self.convert_btn.setMaximumWidth(200)  # Limit button width
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        convert_layout.addWidget(self.convert_btn)
        
        # Cancel button (initially hidden)
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.setMinimumHeight(35)
        self.cancel_btn.setMaximumWidth(120)
        self.cancel_btn.setVisible(False)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #d13438;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 16px;
                margin-left: 10px;
            }
            QPushButton:hover {
                background-color: #b52d32;
            }
        """)
        convert_layout.addWidget(self.cancel_btn)
        convert_layout.addStretch()  # Add stretch after buttons to center them
        
        main_layout.addLayout(convert_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        main_layout.addWidget(self.status_label)
    
    def setup_connections(self):
        self.drop_area.file_dropped.connect(self.load_image)
        self.drop_area.click_to_browse.connect(self.browse_file)
        self.fetch_btn.clicked.connect(self.fetch_from_url)
        self.url_input.returnPressed.connect(self.fetch_from_url)  # Enter key triggers fetch
        self.choose_location_btn.clicked.connect(self.choose_save_location)
        self.convert_btn.clicked.connect(self.convert_images)
        self.cancel_btn.clicked.connect(self.cancel_conversion)
        self.size_checkboxes["custom"].toggled.connect(self.handle_custom_size)
        self.lock_aspect_ratio.toggled.connect(self.toggle_resize_mode)
    
    def setup_clipboard(self):
        """Setup clipboard functionality for pasting images"""
        # Create keyboard shortcut for Ctrl+V
        self.paste_shortcut = QShortcut(QKeySequence.Paste, self)
        self.paste_shortcut.activated.connect(self.paste_from_clipboard)
    
    def paste_from_clipboard(self):
        """Handle pasting image from clipboard"""
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        
        # Check if clipboard has image data
        if clipboard.mimeData().hasImage():
            image = clipboard.image()
            if not image.isNull():
                # Save clipboard image to temporary file
                import tempfile
                import uuid
                temp_file = tempfile.gettempdir() + f"/clipboard_image_{uuid.uuid4().hex[:8]}.png"
                
                if image.save(temp_file):
                    self.load_image(temp_file)
                    self.status_label.setText("Image pasted from clipboard")
                else:
                    QMessageBox.warning(self, "Error", "Failed to save clipboard image")
            else:
                QMessageBox.information(self, "No Image", "No valid image found in clipboard")
        
        # Check if clipboard has URLs (for web images)
        elif clipboard.mimeData().hasUrls():
            urls = clipboard.mimeData().urls()
            if urls:
                url = urls[0]
                if url.scheme() in ['http', 'https']:
                    url_string = url.toString()
                    if self.drop_area.is_image_url(url_string):
                        self.load_image(url_string)
                        return
                
        # Check if clipboard has text that might be a URL
        elif clipboard.mimeData().hasText():
            text = clipboard.text().strip()
            if text.startswith(('http://', 'https://')) and self.drop_area.is_image_url(text):
                self.load_image(text)
                return
            else:
                QMessageBox.information(self, "No Image", "Clipboard contains text but not a valid image URL")
        else:
            QMessageBox.information(self, "No Image", "No image data found in clipboard")
    
    def setup_window_icon(self):
        """Setup window and taskbar icon"""
        def get_resource_path(relative_path):
            """Get absolute path to resource, works for dev and for PyInstaller"""
            import sys
            try:
                # PyInstaller creates a temp folder and stores path in _MEIPASS
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)
        
        # Try to load icon.ico first, then icon.png as fallback
        icon_names = ["icon.ico", "icon.png"]
        
        for icon_name in icon_names:
            icon_path = get_resource_path(icon_name)
            if os.path.exists(icon_path):
                icon = QIcon(icon_path)
                if not icon.isNull():
                    self.setWindowIcon(icon)
                    # Set application icon for taskbar
                    from PySide6.QtWidgets import QApplication
                    QApplication.instance().setWindowIcon(icon)
                    break
    
    def show_message(self, msg_type, title, message):
        """Show message box with application icon"""
        msg_box = QMessageBox(self)
        msg_box.setWindowIcon(get_app_icon())
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if msg_type == "warning":
            msg_box.setIcon(QMessageBox.Warning)
        elif msg_type == "information":
            msg_box.setIcon(QMessageBox.Information)
        elif msg_type == "critical":
            msg_box.setIcon(QMessageBox.Critical)
        
        msg_box.exec()
    
    def load_image(self, file_path_or_url):
        # Check if input is a URL
        if file_path_or_url.startswith(('http://', 'https://')):
            # Handle URL by downloading it
            self.status_label.setText("Downloading image from URL...")
            self.downloader = ImageDownloader(file_path_or_url)
            self.downloader.download_finished.connect(self.on_download_finished)
            self.downloader.download_error.connect(self.on_download_error)
            self.downloader.start()
            return
        
        # Handle local file
        try:
            self.current_image_path = file_path_or_url
            
            # Load and display preview
            pixmap = QPixmap(file_path_or_url)
            if not pixmap.isNull():
                # Get available space in preview label (minus padding)
                available_width = self.preview_label.width() - 20  # Account for padding
                available_height = self.preview_label.height() - 20
                
                # Scale pixmap to fit available space while maintaining aspect ratio
                if available_width > 0 and available_height > 0:
                    scaled_pixmap = pixmap.scaled(
                        available_width, available_height, 
                        Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                else:
                    # Fallback to default size if widget not yet sized
                    scaled_pixmap = pixmap.scaled(380, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                self.preview_label.setPixmap(scaled_pixmap)
                
                file_name = Path(file_path_or_url).name
                self.status_label.setText(f"Loaded: {file_name}")
                self.convert_btn.setEnabled(True)
            else:
                raise Exception("Invalid image file")
                
        except Exception as e:
            self.show_message("warning", "Error", f"Failed to load image: {str(e)}")
            self.status_label.setText("Error loading image")
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image File",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.webp *.gif *.ico *.tiff *.heic)"
        )
        if file_path:
            self.load_image(file_path)
    
    def fetch_from_url(self):
        url = self.url_input.text().strip()
        if not url:
            self.show_message("warning", "Warning", "Please enter a valid URL")
            return
        
        self.status_label.setText("Downloading image...")
        self.fetch_btn.setEnabled(False)
        
        # Create downloader thread
        self.downloader = ImageDownloader(url)
        self.downloader.download_finished.connect(self.on_download_finished)
        self.downloader.download_error.connect(self.on_download_error)
        self.downloader.start()
    
    def on_download_finished(self, file_path):
        self.fetch_btn.setEnabled(True)
        self.load_image(file_path)
    
    def on_download_error(self, error_msg):
        self.fetch_btn.setEnabled(True)
        self.show_message("warning", "Download Error", error_msg)
        self.status_label.setText("Download failed")
    
    def choose_save_location(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose Save Location", self.save_location)
        if folder:
            self.save_location = folder
            self.save_location_label.setText(folder)
    
    def handle_custom_size(self, checked):
        if checked:
            dialog = CustomSizeDialog(self)
            if dialog.exec() == QDialog.Accepted:
                self.custom_size = dialog.get_size()
            else:
                self.size_checkboxes["custom"].setChecked(False)
    
    def toggle_resize_mode(self, checked):
        """Enable/disable resize mode dropdown based on aspect ratio checkbox"""
        self.resize_mode_combo.setEnabled(checked)
    
    def on_resize_unit_changed(self, unit):
        """Handle unit change in resize options and update checkbox labels"""
        dpi = self.dpi_spinbox.value()
        
        # Update checkbox labels based on selected unit
        for i, (original_label, value) in enumerate(self.original_sizes):
            if value == "original" or value == "custom":
                continue  # Skip original and custom options
            
            checkbox = self.size_checkboxes[value]
            width_px, height_px = value
            
            if unit == "Pixels":
                new_label = f"{width_px}x{height_px}"
            elif unit == "Centimeters":
                width_cm = round(width_px / dpi * 2.54, 1)
                height_cm = round(height_px / dpi * 2.54, 1)
                # Format to remove unnecessary decimals
                width_str = f"{width_cm:g}"
                height_str = f"{height_cm:g}"
                new_label = f"{width_str}x{height_str} cm"
            elif unit == "Inches":
                width_in = round(width_px / dpi, 2)
                height_in = round(height_px / dpi, 2)
                # Format to remove unnecessary decimals
                width_str = f"{width_in:g}"
                height_str = f"{height_in:g}"
                new_label = f"{width_str}x{height_str} in"
            
            checkbox.setText(new_label)
    
    def on_dpi_changed(self):
        """Handle DPI change and update unit labels if needed"""
        current_unit = self.resize_unit_combo.currentText()
        if current_unit in ["Centimeters", "Inches"]:
            self.on_resize_unit_changed(current_unit)
    
    def generate_preview_data(self, selected_sizes, output_format, lock_aspect_ratio, resize_mode, dpi, quality):
        """Generate preview data for the preview dialog"""
        try:
            import os
            import time
            from PIL import Image
            import tempfile
            import uuid
            
            preview_data = []
            input_file = Path(self.current_image_path)
            base_name = input_file.stem
            
            # Open the original image
            with Image.open(self.current_image_path) as img:
                # Convert to RGB if necessary (for JPEG output)
                if output_format.lower() in ['jpeg', 'jpg'] and img.mode in ['RGBA', 'P']:
                    # Create white background for transparency
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                for size in selected_sizes:
                    try:
                        # Determine output filename
                        if size == "original":
                            output_name = f"{base_name}.{output_format.lower()}"
                            processed_img = img.copy()
                            
                            # Apply ICO size optimization to original as well
                            if output_format.lower() == 'ico':
                                orig_width, orig_height = processed_img.size
                                if orig_width > 256 or orig_height > 256:
                                    # ICO has practical limits in PIL - 256x256 works reliably
                                    max_size = 256
                                    if orig_width > orig_height:
                                        new_height = int(orig_height * max_size / orig_width)
                                        new_width = max_size
                                    else:
                                        new_width = int(orig_width * max_size / orig_height)
                                        new_height = max_size
                                    processed_img = processed_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        else:
                            if isinstance(size, tuple):
                                width, height = size
                                # Convert to integers if they're floats (from custom size dialog)
                                width, height = int(width), int(height)
                                size_str = f"{width}x{height}"
                            else:
                                width, height = size
                                # Convert to integers if they're floats
                                width, height = int(width), int(height)
                                size_str = f"{width}x{height}"
                            
                            # Skip extremely large sizes to prevent memory issues
                            if width > 8000 or height > 8000:
                                continue
                            
                            # Optimize size for ICO format limitations
                            if output_format.lower() == 'ico':
                                if width > 256 or height > 256:
                                    # ICO has practical limits in PIL - 256x256 works reliably
                                    max_size = 256
                                    if width > height:
                                        height = int(height * max_size / width)
                                        width = max_size
                                    else:
                                        width = int(width * max_size / height)
                                        height = max_size
                            
                            output_name = f"{base_name}_{size_str}.{output_format.lower()}"
                            
                            # Resize image based on mode (same logic as converter)
                            if not lock_aspect_ratio or resize_mode == "stretch":
                                processed_img = img.resize((width, height), Image.Resampling.LANCZOS)
                            elif resize_mode == "fit":
                                original_width, original_height = img.size
                                aspect_ratio = original_width / original_height
                                target_ratio = width / height
                                
                                if aspect_ratio > target_ratio:
                                    new_width = width
                                    new_height = int(width / aspect_ratio)
                                else:
                                    new_height = height
                                    new_width = int(height * aspect_ratio)
                                
                                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                                
                                if img.mode == 'RGBA' or 'transparency' in img.info:
                                    processed_img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
                                else:
                                    processed_img = Image.new('RGB', (width, height), (255, 255, 255))
                                
                                x_offset = (width - new_width) // 2
                                y_offset = (height - new_height) // 2
                                processed_img.paste(resized_img, (x_offset, y_offset))
                            elif resize_mode == "crop":
                                original_width, original_height = img.size
                                aspect_ratio = original_width / original_height
                                target_ratio = width / height
                                
                                if aspect_ratio > target_ratio:
                                    new_height = height
                                    new_width = int(height * aspect_ratio)
                                else:
                                    new_width = width
                                    new_height = int(width / aspect_ratio)
                                
                                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                                
                                x_offset = (new_width - width) // 2
                                y_offset = (new_height - height) // 2
                                processed_img = resized_img.crop((x_offset, y_offset, x_offset + width, y_offset + height))
                        
                        # Save preview to temporary file
                        temp_dir = tempfile.gettempdir()
                        temp_filename = f"preview_{uuid.uuid4().hex[:8]}_{output_name}"
                        temp_path = os.path.join(temp_dir, temp_filename)
                        
                        # Handle different formats - match exactly with main converter
                        save_kwargs = {}
                        if output_format.lower() in ['jpeg', 'jpg']:
                            save_kwargs['quality'] = quality
                            save_kwargs['optimize'] = True
                            save_kwargs['dpi'] = (dpi, dpi)
                        elif output_format.lower() == 'webp':
                            # Use same WebP settings as main converter
                            save_kwargs['quality'] = min(quality, 85)  # Cap quality for speed
                            save_kwargs['method'] = 1  # Fastest method (0-6, lower is faster)
                            save_kwargs['lossless'] = False  # Ensure lossy compression for speed
                            save_kwargs['exact'] = False  # Allow approximations for speed
                        elif output_format.lower() == 'png':
                            save_kwargs['optimize'] = True
                            save_kwargs['dpi'] = (dpi, dpi)
                            # Use quality setting to control PNG compression level
                            # Higher quality = less compression (larger file)
                            # Lower quality = more compression (smaller file)
                            if quality >= 90:
                                save_kwargs['compress_level'] = 1  # Less compression, larger file
                            elif quality >= 70:
                                save_kwargs['compress_level'] = 6  # Default compression
                            else:
                                save_kwargs['compress_level'] = 9  # Maximum compression, smaller file
                        elif output_format.lower() == 'ico':
                            # ICO doesn't support DPI metadata or quality
                            # For large ICO files, we need to be more careful
                            img_width, img_height = processed_img.width, processed_img.height
                            if img_width <= 256 and img_height <= 256:
                                # Standard ICO with sizes parameter
                                save_kwargs['sizes'] = [(img_width, img_height)]
                            else:
                                # For larger ICO files, don't use sizes parameter
                                # PIL might have issues with large sizes in the sizes parameter
                                pass
                        
                        # Set DPI for formats that support it
                        if output_format.lower() in ['png', 'jpeg', 'jpg']:
                            # Also set the DPI in the image info
                            processed_img.info['dpi'] = (dpi, dpi)
                        
                        # Handle format name for PIL
                        pil_format = output_format.upper()
                        if pil_format == 'JPG':
                            pil_format = 'JPEG'
                        
                        # Special handling for ICO format
                        if pil_format == 'ICO':
                            try:
                                # Ensure image is in RGBA mode for ICO
                                if processed_img.mode != 'RGBA':
                                    processed_img = processed_img.convert('RGBA')
                                processed_img.save(temp_path, format=pil_format, **save_kwargs)
                            except Exception as ico_error:
                                # If ICO save fails, try without any special parameters
                                print(f"ICO save failed with parameters, trying without: {ico_error}")
                                try:
                                    if processed_img.mode != 'RGBA':
                                        processed_img = processed_img.convert('RGBA')
                                    processed_img.save(temp_path, format=pil_format)
                                except Exception as ico_error2:
                                    print(f"ICO save failed completely: {ico_error2}")
                                    # Skip this size if ICO conversion fails
                                    continue
                        else:
                            processed_img.save(temp_path, format=pil_format, **save_kwargs)
                        
                        # Ensure file is completely written and flushed
                        time.sleep(0.02)  # Slightly longer delay
                        
                        # Force file system sync (if possible)
                        try:
                            if hasattr(os, 'sync'):
                                os.sync()
                        except:
                            pass
                        
                        # Add to preview data (temp_path, size, output_format, output_name, original_path)
                        preview_data.append((temp_path, size, output_format, output_name, self.current_image_path))
                        
                    except Exception as e:
                        # Skip this size if there's an error
                        continue
            
            return preview_data
            
        except Exception as e:
            print(f"Error generating preview data: {str(e)}")
            return []
    

    
    def cancel_conversion(self):
        """Cancel the ongoing conversion"""
        if hasattr(self, 'converter') and self.converter.isRunning():
            self.converter.cancel()
            self.converter.wait(3000)  # Wait up to 3 seconds for thread to finish
            self.progress_bar.setVisible(False)
            self.convert_btn.setEnabled(True)
            self.cancel_btn.setVisible(False)
            self.status_label.setText("Conversion cancelled")
    
    def convert_images(self):
        if not self.current_image_path:
            self.show_message("warning", "Warning", "Please select an image first")
            return
        
        # Get selected sizes
        selected_sizes = []
        for size_key, checkbox in self.size_checkboxes.items():
            if checkbox.isChecked():
                if size_key == "custom":
                    selected_sizes.append(self.custom_size)
                elif size_key != "original":
                    selected_sizes.append(size_key)
                else:
                    selected_sizes.append("original")
        
        if not selected_sizes:
            self.show_message("warning", "Warning", "Please select at least one size option")
            return
        
        # Get output format and resize settings
        output_format = self.format_combo.currentText().lower()
        lock_aspect_ratio = self.lock_aspect_ratio.isChecked()
        resize_mode = self.resize_mode_combo.currentText().lower() if lock_aspect_ratio else "stretch"
        dpi = self.dpi_spinbox.value()
        quality = self.quality_spinbox.value()
        
        # Generate preview data
        self.status_label.setText("Generating preview...")
        preview_data = self.generate_preview_data(selected_sizes, output_format, lock_aspect_ratio, resize_mode, dpi, quality)
        
        if not preview_data:
            self.show_message("warning", "Error", "Failed to generate preview data")
            return
        
        # Show preview dialog
        preview_dialog = PreviewDialog(preview_data, dpi, quality, self)
        if preview_dialog.exec() != QDialog.Accepted:
            self.status_label.setText("Conversion cancelled")
            return
        
        # User confirmed, proceed with actual conversion
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(selected_sizes))
        self.progress_bar.setValue(0)
        self.convert_btn.setEnabled(False)
        self.cancel_btn.setVisible(True)
        self.status_label.setText("Starting conversion...")
        
        # Create converter thread
        self.converter = ImageConverter(
            self.current_image_path,
            selected_sizes,
            output_format,
            self.save_location,
            lock_aspect_ratio,
            resize_mode,
            dpi,
            quality
        )
        self.converter.progress_updated.connect(self.progress_bar.setValue)
        self.converter.status_updated.connect(self.status_label.setText)
        self.converter.conversion_finished.connect(self.on_conversion_finished)
        self.converter.conversion_error.connect(self.on_conversion_error)
        self.converter.start()
    
    def on_conversion_finished(self, output_files):
        self.progress_bar.setVisible(False)
        self.convert_btn.setEnabled(True)
        self.cancel_btn.setVisible(False)
        
        file_list = "\n".join([Path(f).name for f in output_files])
        self.show_message("information", "Conversion Complete", f"Successfully converted {len(output_files)} image(s):\n\n{file_list}")
        self.status_label.setText(f"Converted {len(output_files)} image(s)")
    
    def on_conversion_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.convert_btn.setEnabled(True)
        self.cancel_btn.setVisible(False)
        self.show_message("critical", "Conversion Error", error_msg)
        self.status_label.setText("Conversion failed")