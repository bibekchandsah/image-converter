# 🖼️ Image Converter GUI

A modern Python GUI application built with PySide6 for converting and resizing images with advanced features including drag & drop support, clipboard paste, URL fetching, unit conversion, comprehensive preview system, and optimized multi-threading.

## ✨ Features

### 🎯 Input Methods
- **Drag & Drop**: Direct image dropping with visual feedback
- **File Browser**: Traditional file selection dialog
- **URL Fetching**: Download images directly from web URLs
- **Clipboard Support**: Paste images with Ctrl+V

### 📐 Advanced Unit System
- **Multiple Units**: Pixels, Centimeters, Inches
- **Real-time Conversion**: Dynamic unit switching with DPI calculation
- **Smart Labels**: Size options update based on selected unit
- **DPI Integration**: Proper physical size calculations
- **Quality Integration**:  DPI and quality settings synchronized

### 🔄 Format Support
- **Input**: PNG, JPG, JPEG, BMP, WebP, GIF, ICO, TIFF, HEIC
- **Output**: PNG, JPEG, JPG, WebP, ICO
- **Format-Specific Optimization**:
  - **WebP**: Fast compression with quality capping
  - **PNG**: Compression levels based on quality settings
  - **ICO**: Automatic size optimization (max 256x256)
  - **JPEG**: Full quality and DPI support

### 🎨 Intelligent Resizing
- **Original Size**: Keep source dimensions
- **Predefined Sizes**: 16x16, 32x32, 48x48, 128x128, 150x150, 192x192, 512x512
- **Custom Dimensions**: User-defined sizes with unit support
- **Batch Processing**: Multiple sizes simultaneously
- **Aspect Ratio Control**: Lock/unlock with resize modes (Stretch, Crop, Fit)

### 👁️ Comprehensive Preview System
- **Real-time Preview**: See exactly what you'll get before saving
- **Batch Preview**: Preview multiple sizes at once
- **Detailed Information**: File size, dimensions, format, DPI, quality
- **Format-Specific Details**: Compression info, limitations, recommendations
- **Actual Conversion**: Preview uses real conversion settings for accurate results

### ⚡ Performance & Threading
- **Non-blocking UI**: Multi-threaded conversion prevents freezing
- **Cancellable Operations**: Stop conversions mid-process
- **Progress Tracking**: Real-time status updates
- **Optimized WebP**: Fast compression settings for responsive UI

### 🎛️ Advanced Settings
- **Quality Control**: 1-100% quality settings with format-specific handling
- **DPI Settings**: 72-600 DPI with metadata support
- **Compression Modes**: Format-specific optimization
- **Resize Modes**: Stretch, Crop, Fit with aspect ratio control

## 🚀 Installation

1. **Install Python 3.8+**

2. **Install required dependencies**:
```bash
pip install PySide6 Pillow requests
```

3. **Run the application**:
```bash
python main.py
```

## 📁 Project Structure

```
ImageConverter/
├── main.py                    # Application entry point
├── ui_mainwindow.py          # Main GUI window and logic
├── converter.py              # Image conversion functionality
├── downloader.py             # URL image fetching
├── utils/
│   ├── file_utils.py         # File handling utilities
│   └── resize_options.py     # Size validation and presets
├── assets/
│   └── style.qss            # Modern UI stylesheet
└── README.md
```

## 🎯 Usage

### Basic Workflow
1. **Load an Image**:
   - Drag & drop an image file into the drop area
   - Click the drop area to browse files
   - Enter an image URL and click "Fetch"
   - Paste from clipboard with Ctrl+V

2. **Configure Settings**:
   - **Format**: Choose PNG, JPEG, JPG, WebP, or ICO
   - **Quality**: Set 1-100% (affects lossy formats)
   - **DPI**: Set 72-600 DPI (for print quality)
   - **Aspect Ratio**: Lock/unlock with resize mode selection

3. **Select Units & Sizes**:
   - **Unit**: Choose Pixels, Centimeters, or Inches
   - **Sizes**: Check one or more size options
   - **Custom**: Enter specific dimensions in chosen unit

4. **Preview Before Saving**:
   - Click "Preview" to see exact results
   - Review file sizes, dimensions, and format details
   - Cancel to adjust settings or proceed to save

5. **Convert & Save**:
   - Click "Convert Image(s)" after preview confirmation
   - Monitor progress with real-time status updates
   - Cancel conversion if needed

### Advanced Features

#### Unit Conversion
- Switch between Pixels, Centimeters, and Inches
- Size labels automatically update based on DPI settings
- Custom size dialog supports decimal values for precise measurements

#### Preview System
- **Comprehensive Details**: See file size, dimensions, DPI, quality, and format-specific info
- **Actual Conversion**: Preview performs real conversion for accurate file sizes
- **Format Guidance**: Get recommendations and limitations for each format

#### Quality & DPI Control
- **Format-Specific**: Quality affects JPEG/WebP, compression level for PNG
- **DPI Metadata**: Properly set for PNG/JPEG, noted as unsupported for WebP/ICO
- **Smart Defaults**: 300 DPI for print quality, 90% quality for good balance

## 🔧 Technical Details

- **Framework**: PySide6 (Qt for Python)
- **Image Processing**: Pillow (PIL)
- **HTTP Requests**: requests library
- **Threading**: QThread for non-blocking operations
- **File Handling**: pathlib for cross-platform compatibility

## 📝 Output File Naming

Converted files follow this pattern:
```
original_filename_WIDTHxHEIGHT.format
```

Examples:
- `sunset_128x128.webp`
- `photo_512x512.png`
- `icon_32x32.ico`

## 🎯 Unit Conversion Examples

### Pixel Mode (Default)
- Direct pixel dimensions: 512x512, 256x256, etc.

### Centimeter Mode (300 DPI)
- 1.0 cm = 118 pixels
- 2.5 cm = 295 pixels  
- 5.0 cm = 590 pixels

### Inch Mode (300 DPI)
- 0.5 inches = 150 pixels
- 1.0 inch = 300 pixels
- 2.0 inches = 600 pixels

*Note: Conversions depend on DPI setting. Higher DPI = more pixels per physical unit.*

## 🔍 Preview System Details

### What You See in Preview
- **File Name**: Exact output filename
- **Dimensions**: Final pixel dimensions (with unit conversion if applicable)
- **Format**: Output format with specific notes
- **DPI**: Resolution setting (where supported)
- **Quality**: Compression quality with format-specific details
- **File Size**: Actual file size after conversion
- **Format Notes**: Optimization details and limitations

### Preview Accuracy
- Uses real conversion process for accurate file sizes
- Shows actual compression results
- Displays format-specific optimizations
- Provides cancellation option before saving

## 🛠️ Advanced Features

### 📐 Unit System
- **Pixel Mode**: Direct pixel dimensions (default)
- **Centimeter Mode**: Physical measurements with DPI calculation
- **Inch Mode**: Imperial measurements with DPI conversion
- **Dynamic Updates**: Size labels change based on selected unit and DPI

### 👁️ Preview System
- **Real Conversion**: Uses actual conversion settings for accurate previews
- **Detailed Info**: Shows file size, dimensions, DPI, quality, compression type
- **Format-Specific Guidance**:
  - **PNG**: Shows compression level (Low/Medium/High)
  - **JPEG**: Shows quality percentage and DPI
  - **WebP**: Shows optimized quality and fast compression note
  - **ICO**: Shows size limitations and compatibility notes

### ⚡ Performance Optimizations
- **Multi-threading**: Non-blocking UI during conversions
- **WebP Optimization**: Fast compression (method 1, quality capped at 85%)
- **PNG Compression**: Quality-based compression levels (1-9)
- **Memory Management**: Size limits prevent memory issues
- **Cancellation**: Stop long-running conversions

### 🎨 Resize Modes
- **Stretch**: Resize to exact dimensions (may distort)
- **Crop**: Fill target size completely, crop excess
- **Fit**: Fit completely inside target size with background

### 🔧 Format-Specific Features
- **ICO Optimization**: Automatic size reduction to 256x256 for compatibility
- **WebP Fast Mode**: Optimized for speed with quality capping
- **PNG Compression**: Quality setting controls compression level
- **JPEG Quality**: Full 1-100% quality range with DPI support

### 🖱️ User Interface
- **Drag & Drop**: Visual feedback and validation
- **Clipboard Support**: Paste images and URLs
- **Progress Tracking**: Real-time conversion status
- **Error Handling**: Graceful error recovery and user feedback
- **Responsive Design**: Adapts to window resizing

## 🎨 UI Features

- Modern, clean design
- Responsive layout
- Real-time image preview
- Progress indicators
- Status messages
- Intuitive controls

## 🔍 Format Support & Optimization

### Input Formats
- **PNG** (Portable Network Graphics) - Lossless with transparency
- **JPEG/JPG** (Joint Photographic Experts Group) - Compressed photos
- **BMP** (Bitmap) - Uncompressed raster format
- **WebP** (Web Picture format) - Modern web format
- **GIF** (Graphics Interchange Format) - Animated/simple graphics
- **ICO** (Icon format) - Windows icons
- **TIFF** (Tagged Image File Format) - High-quality archival
- **HEIC** (High Efficiency Image Container) - Apple's modern format

### Output Formats with Smart Optimization

#### PNG - Lossless Compression
- **Quality Setting**: Controls compression level (1-9)
- **DPI Support**: Full metadata support
- **Transparency**: Preserved from source
- **Best For**: Graphics, logos, images with transparency

#### JPEG/JPG - Lossy Compression
- **Quality Range**: 1-100% with visual quality control
- **DPI Support**: Full metadata and print quality support
- **Optimization**: Automatic optimization enabled
- **Best For**: Photographs, complex images

#### WebP - Modern Web Format
- **Fast Compression**: Optimized method 1 for speed
- **Quality Capping**: Automatically capped at 85% for performance
- **No DPI**: Format doesn't support DPI metadata
- **Best For**: Web images, modern browsers

#### ICO - Windows Icons
- **Size Limitation**: Automatically optimized to 256x256 max (PIL limitation)
- **Multiple Sizes**: Can contain multiple icon sizes
- **No Quality/DPI**: Lossless format without metadata support
- **Best For**: Windows application icons, favicons

### Format-Specific Intelligence
- **Automatic Optimization**: Each format uses optimal settings
- **Size Warnings**: Clear indication of format limitations
- **Quality Guidance**: Format-appropriate quality recommendations
- **Compatibility Notes**: Information about format support and limitations

## 🚨 Requirements & Performance

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows 10/11, macOS, or Linux
- **Memory**: 4GB RAM recommended for large image processing
- **Storage**: Minimal disk space (temporary files cleaned automatically)

### Dependencies
```bash
pip install PySide6 Pillow requests
```

### Performance Notes
- **Large Images**: >10MB images may take longer to process
- **ICO Format**: Limited to 256x256 pixels (PIL limitation)
- **WebP**: Optimized for speed with quality capping at 85%
- **Multi-threading**: UI remains responsive during conversion
- **Memory Management**: Automatic size limits prevent memory issues

## 📄 License

This project is open source and available under the MIT License.

## � Recentt Improvements

### Version 2.0 Features
- ✅ **Unit System**: Pixels, Centimeters, Inches with real-time conversion
- ✅ **Advanced Preview**: Real conversion preview with detailed information
- ✅ **Multi-threading**: Non-blocking UI with cancellation support
- ✅ **Format Optimization**: WebP fast mode, PNG compression levels, ICO size limits
- ✅ **Clipboard Support**: Paste images and URLs with Ctrl+V
- ✅ **Quality Control**: Format-specific quality and DPI settings
- ✅ **Resize Modes**: Stretch, Crop, Fit with aspect ratio control
- ✅ **Smart UI**: Dynamic labels, progress tracking, error handling

### Performance Enhancements
- 🚀 **WebP Speed**: 3x faster conversion with optimized settings
- 🚀 **UI Responsiveness**: Multi-threaded processing prevents freezing
- 🚀 **Memory Management**: Automatic size limits and cleanup
- 🚀 **Preview Speed**: Efficient temporary file handling

## 👨‍💻 Author

**Bibek**  
Date: 30 Oct 2025 (Updated: 1 Nov 2025)  
Project: Image Converter GUI v2.0  
Language: Python 3 (PySide6)  
Features: Advanced unit conversion, preview system, multi-threading

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve this application.

### Development Focus Areas
- Additional output formats (AVIF, JPEG XL)
- Batch file processing
- Image editing features (rotate, flip, filters)
- Plugin system for custom formats
- Command-line interface