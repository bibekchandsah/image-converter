#!/usr/bin/env python3
"""
Test script for Image Converter functionality
"""

import sys
import tempfile
from pathlib import Path
from PIL import Image
from converter import convert_image, get_image_info
from utils.file_utils import get_downloads_folder, create_output_filename
from utils.resize_options import validate_custom_size, suggest_sizes_for_format

def create_test_image():
    """Create a simple test image"""
    # Create a simple 200x200 red square
    img = Image.new('RGB', (200, 200), color='red')
    
    # Add some text or pattern to make it more interesting
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 150, 150], fill='blue')
    draw.rectangle([75, 75, 125, 125], fill='white')
    
    # Save to temp file
    temp_path = Path(tempfile.gettempdir()) / "test_image.png"
    img.save(temp_path, "PNG")
    return str(temp_path)

def test_image_info():
    """Test image info extraction"""
    print("Testing image info extraction...")
    test_img_path = create_test_image()
    
    info = get_image_info(test_img_path)
    if info:
        print(f"✓ Image info: {info}")
    else:
        print("✗ Failed to get image info")
    
    return test_img_path

def test_conversion(test_img_path):
    """Test image conversion"""
    print("\nTesting image conversion...")
    
    downloads = get_downloads_folder()
    print(f"Downloads folder: {downloads}")
    
    # Test different formats and sizes
    test_cases = [
        ("PNG", (128, 128)),
        ("JPEG", (256, 256)),
        ("WebP", "original"),
        ("ICO", (32, 32))
    ]
    
    for format_name, size in test_cases:
        output_name = create_output_filename(test_img_path, size, format_name)
        output_path = Path(downloads) / output_name
        
        success = convert_image(test_img_path, str(output_path), format_name, size)
        if success and output_path.exists():
            print(f"✓ Converted to {format_name} ({size}): {output_name}")
        else:
            print(f"✗ Failed to convert to {format_name} ({size})")

def test_utilities():
    """Test utility functions"""
    print("\nTesting utility functions...")
    
    # Test size validation
    errors = validate_custom_size(512, 512)
    if not errors:
        print("✓ Size validation works")
    else:
        print(f"✗ Size validation failed: {errors}")
    
    # Test invalid size
    errors = validate_custom_size(-10, 0)
    if errors:
        print("✓ Invalid size detection works")
    else:
        print("✗ Invalid size detection failed")
    
    # Test format suggestions
    suggestions = suggest_sizes_for_format("ICO")
    print(f"✓ ICO format suggestions: {suggestions}")

def main():
    print("🖼️ Image Converter Test Suite")
    print("=" * 40)
    
    try:
        # Test image creation and info
        test_img_path = test_image_info()
        
        # Test conversion
        test_conversion(test_img_path)
        
        # Test utilities
        test_utilities()
        
        print("\n" + "=" * 40)
        print("✅ Test suite completed!")
        print(f"Check your Downloads folder for converted images.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()