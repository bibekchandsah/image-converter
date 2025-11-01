"""
Resize options and validation utilities
"""

# Predefined resize options
RESIZE_PRESETS = {
    "original": "original",
    "16x16": (16, 16),
    "32x32": (32, 32),
    "48x48": (48, 48),
    "128x128": (128, 128),
    "150x150": (150, 150),
    "192x192": (192, 192),
    "512x512": (512, 512),
    "custom": "custom"
}

# Common icon sizes
ICON_SIZES = [16, 32, 48, 64, 128, 256]

# Common web image sizes
WEB_SIZES = [
    (150, 150),   # Thumbnail
    (300, 300),   # Small
    (600, 600),   # Medium
    (1200, 1200), # Large
    (1920, 1080), # HD
    (2560, 1440), # QHD
]

def validate_custom_size(width, height):
    """
    Validate custom width and height values
    """
    errors = []
    
    if not isinstance(width, int) or width <= 0:
        errors.append("Width must be a positive integer")
    elif width > 10000:
        errors.append("Width cannot exceed 10,000 pixels")
    
    if not isinstance(height, int) or height <= 0:
        errors.append("Height must be a positive integer")
    elif height > 10000:
        errors.append("Height cannot exceed 10,000 pixels")
    
    return errors

def get_aspect_ratio(width, height):
    """
    Calculate aspect ratio
    """
    if height == 0:
        return 0
    return width / height

def calculate_proportional_size(original_width, original_height, target_width=None, target_height=None):
    """
    Calculate proportional size maintaining aspect ratio
    """
    if target_width and target_height:
        return target_width, target_height
    
    aspect_ratio = original_width / original_height
    
    if target_width:
        return target_width, int(target_width / aspect_ratio)
    elif target_height:
        return int(target_height * aspect_ratio), target_height
    else:
        return original_width, original_height

def suggest_sizes_for_format(output_format):
    """
    Suggest appropriate sizes based on output format
    """
    format_lower = output_format.lower()
    
    if format_lower == 'ico':
        # ICO files typically need multiple sizes
        return [(16, 16), (32, 32), (48, 48), (128, 128), (256, 256)]
    elif format_lower in ['webp', 'png']:
        # Web formats - suggest web-friendly sizes
        return [(150, 150), (300, 300), (600, 600), (1200, 1200)]
    elif format_lower in ['jpeg', 'jpg']:
        # JPEG - suggest photo sizes
        return [(800, 600), (1920, 1080), (2560, 1440)]
    else:
        # Default suggestions
        return [(128, 128), (512, 512), (1024, 1024)]

def get_size_category(width, height):
    """
    Categorize image size
    """
    total_pixels = width * height
    
    if total_pixels < 10000:  # < 100x100
        return "Icon"
    elif total_pixels < 250000:  # < 500x500
        return "Small"
    elif total_pixels < 1000000:  # < 1000x1000
        return "Medium"
    elif total_pixels < 4000000:  # < 2000x2000
        return "Large"
    else:
        return "Very Large"

def optimize_size_for_format(width, height, output_format):
    """
    Optimize size based on output format limitations
    """
    format_lower = output_format.lower()
    
    # ICO format limitations
    if format_lower == 'ico':
        # ICO has practical limits in PIL - 256x256 works reliably
        max_size = 256
        if width > max_size or height > max_size:
            if width > height:
                height = int(height * max_size / width)
                width = max_size
            else:
                width = int(width * max_size / height)
                height = max_size
    
    return width, height

def get_recommended_quality(output_format, image_size):
    """
    Get recommended quality settings based on format and size
    """
    format_lower = output_format.lower()
    width, height = image_size
    total_pixels = width * height
    
    if format_lower in ['jpeg', 'jpg']:
        if total_pixels > 2000000:  # Large images
            return 85  # Lower quality for large images
        else:
            return 95  # High quality for smaller images
    elif format_lower == 'webp':
        if total_pixels > 2000000:
            return 80
        else:
            return 90
    else:
        return None  # No quality setting needed