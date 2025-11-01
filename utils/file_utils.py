"""
File utilities for Image Converter
"""

import os
from pathlib import Path

def get_downloads_folder():
    """
    Get the user's Downloads folder path
    """
    home = Path.home()
    downloads = home / "Downloads"
    
    # Create Downloads folder if it doesn't exist
    downloads.mkdir(exist_ok=True)
    
    return str(downloads)

def get_safe_filename(filename):
    """
    Remove or replace invalid characters from filename
    """
    # Characters not allowed in Windows filenames
    invalid_chars = '<>:"/\\|?*'
    
    safe_filename = filename
    for char in invalid_chars:
        safe_filename = safe_filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    safe_filename = safe_filename.strip(' .')
    
    # Ensure filename is not empty
    if not safe_filename:
        safe_filename = "image"
    
    return safe_filename

def ensure_unique_filename(file_path):
    """
    Ensure filename is unique by adding number suffix if needed
    """
    path = Path(file_path)
    
    if not path.exists():
        return str(path)
    
    # File exists, find unique name
    counter = 1
    while True:
        new_name = f"{path.stem}_{counter}{path.suffix}"
        new_path = path.parent / new_name
        
        if not new_path.exists():
            return str(new_path)
        
        counter += 1

def get_file_size_mb(file_path):
    """
    Get file size in megabytes
    """
    try:
        size_bytes = Path(file_path).stat().st_size
        return size_bytes / (1024 * 1024)
    except Exception:
        return 0

def is_valid_image_extension(file_path):
    """
    Check if file has a valid image extension
    """
    valid_extensions = {
        '.png', '.jpg', '.jpeg', '.bmp', '.webp', 
        '.gif', '.ico', '.tiff', '.heic'
    }
    
    extension = Path(file_path).suffix.lower()
    return extension in valid_extensions

def create_output_filename(input_path, size, output_format):
    """
    Create output filename based on input file, size, and format
    """
    input_file = Path(input_path)
    base_name = get_safe_filename(input_file.stem)
    
    if size == "original":
        return f"{base_name}.{output_format.lower()}"
    elif isinstance(size, tuple):
        width, height = size
        return f"{base_name}_{width}x{height}.{output_format.lower()}"
    else:
        return f"{base_name}_{size[0]}x{size[1]}.{output_format.lower()}"

def get_temp_image_path(extension=".jpg"):
    """
    Get a temporary file path for image operations
    """
    import tempfile
    temp_dir = tempfile.gettempdir()
    temp_name = f"temp_image_{os.getpid()}{extension}"
    return str(Path(temp_dir) / temp_name)

def cleanup_temp_files(file_paths):
    """
    Clean up temporary files
    """
    for file_path in file_paths:
        try:
            if Path(file_path).exists():
                os.remove(file_path)
        except Exception:
            pass  # Ignore cleanup errors