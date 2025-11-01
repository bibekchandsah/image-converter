#!/usr/bin/env python3
"""
Demo script showing Image Converter usage examples
"""

import sys
from pathlib import Path
from PIL import Image
import tempfile

# Add current directory to path to import our modules
sys.path.insert(0, '.')

from converter import convert_image
from downloader import download_image_sync
from utils.file_utils import get_downloads_folder, create_output_filename

def create_sample_image():
    """Create a sample image for demonstration"""
    print("Creating sample image...")
    
    # Create a colorful gradient image
    img = Image.new('RGB', (400, 300), color='white')
    
    # Create a simple gradient effect
    pixels = img.load()
    for x in range(400):
        for y in range(300):
            r = int(255 * x / 400)
            g = int(255 * y / 300)
            b = int(255 * (x + y) / 700)
            pixels[x, y] = (r, g, b)
    
    # Save sample image
    sample_path = Path(tempfile.gettempdir()) / "sample_gradient.png"
    img.save(sample_path, "PNG")
    print(f"✓ Sample image created: {sample_path}")
    return str(sample_path)

def demo_conversions():
    """Demonstrate various conversion scenarios"""
    print("\n🔄 Demonstrating Image Conversions")
    print("-" * 40)
    
    # Create sample image
    sample_path = create_sample_image()
    downloads = get_downloads_folder()
    
    # Demo 1: Convert to different formats
    formats = ["PNG", "JPEG", "WebP", "ICO"]
    for fmt in formats:
        output_name = f"demo_sample.{fmt.lower()}"
        output_path = Path(downloads) / output_name
        
        success = convert_image(sample_path, str(output_path), fmt)
        if success:
            print(f"✓ Converted to {fmt}: {output_name}")
        else:
            print(f"✗ Failed to convert to {fmt}")
    
    # Demo 2: Convert to different sizes
    sizes = [(64, 64), (128, 128), (256, 256), (512, 512)]
    for size in sizes:
        output_name = create_output_filename(sample_path, size, "PNG")
        output_path = Path(downloads) / output_name
        
        success = convert_image(sample_path, str(output_path), "PNG", size)
        if success:
            print(f"✓ Resized to {size[0]}x{size[1]}: {output_name}")

def main():
    print("🖼️ Image Converter Demo")
    print("=" * 50)
    
    try:
        demo_conversions()
        
        print("\n" + "=" * 50)
        print("✅ Demo completed successfully!")
        print(f"Check your Downloads folder: {get_downloads_folder()}")
        print("\nTo run the GUI application:")
        print("python main.py")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()