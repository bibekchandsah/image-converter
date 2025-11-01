# 🚀 Installation Guide

## Quick Start (Windows)

1. **Double-click `run_converter.bat`** - This will automatically:
   - Check if Python is installed
   - Install required dependencies
   - Launch the Image Converter GUI

## Manual Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install PySide6 Pillow requests
```

### Step 2: Run the Application
```bash
python main.py
```

## Verification

### Test Core Functionality
```bash
python test_converter.py
```

### Run Demo
```bash
python demo.py
```

## Troubleshooting

### Common Issues

**"Python is not recognized"**
- Install Python from https://python.org
- Make sure to check "Add Python to PATH" during installation

**"No module named 'PySide6'"**
- Run: `pip install PySide6`
- If using conda: `conda install pyside6`

**"Permission denied" when saving files**
- Make sure you have write permissions to the Downloads folder
- Try running as administrator (Windows) or with sudo (Linux/Mac)

**GUI doesn't appear**
- Check if you're using a virtual environment
- Try: `python -m pip install --upgrade PySide6`

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.8 | 3.10+ |
| RAM | 512 MB | 1 GB+ |
| Storage | 100 MB | 500 MB+ |
| OS | Windows 10, macOS 10.14, Ubuntu 18.04 | Latest versions |

### Virtual Environment (Optional)

```bash
# Create virtual environment
python -m venv image_converter_env

# Activate (Windows)
image_converter_env\Scripts\activate

# Activate (Linux/Mac)
source image_converter_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## Features Verification Checklist

- [ ] GUI launches without errors
- [ ] Drag & drop works with image files
- [ ] Browse button opens file dialog
- [ ] URL input can fetch images from web
- [ ] Format conversion works (PNG, JPEG, WebP, ICO)
- [ ] Resize options work correctly
- [ ] Multiple size selection creates multiple files
- [ ] Custom size input works
- [ ] Save location can be changed
- [ ] Progress bar shows during conversion
- [ ] Status messages appear correctly
- [ ] Converted files save to correct location

## Getting Help

If you encounter issues:

1. Check the console output for error messages
2. Verify all dependencies are installed correctly
3. Make sure you have the latest versions of Python and pip
4. Try running the test script to isolate the issue

## Performance Tips

- For large images (>10MB), conversion may take longer
- ICO format works best with sizes up to 256x256 (PIL limitation)
- WebP provides best compression for web use
- JPEG is best for photographs, PNG for graphics with transparency