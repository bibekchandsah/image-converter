"""
Image Converter - Handles image conversion and resizing logic
"""

import os
import time
from pathlib import Path
from PIL import Image
from PySide6.QtCore import QThread, Signal

class ImageConverter(QThread):
    progress_updated = Signal(int)
    status_updated = Signal(str)
    conversion_finished = Signal(list)
    conversion_error = Signal(str)
    
    def __init__(self, input_path, sizes, output_format, save_location, lock_aspect_ratio=True, resize_mode="stretch", dpi=300, quality=90):
        super().__init__()
        self.input_path = input_path
        self.sizes = sizes
        self.output_format = output_format
        self.save_location = save_location
        self.lock_aspect_ratio = lock_aspect_ratio
        self.resize_mode = resize_mode
        self.dpi = dpi
        self.quality = quality
        self._cancelled = False
    
    def cancel(self):
        """Cancel the conversion process"""
        self._cancelled = True
    
    def run(self):
        try:
            output_files = []
            input_file = Path(self.input_path)
            base_name = input_file.stem
            
            # Open the original image
            with Image.open(self.input_path) as img:
                # Convert to RGB if necessary (for JPEG output)
                if self.output_format.lower() in ['jpeg', 'jpg'] and img.mode in ['RGBA', 'P']:
                    # Create white background for transparency
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                for i, size in enumerate(self.sizes):
                    # Check if cancelled
                    if self._cancelled:
                        self.status_updated.emit("Conversion cancelled")
                        return
                    
                    try:
                        # Emit progress for processing start
                        self.progress_updated.emit(i)
                        
                        # Determine output filename
                        if size == "original":
                            output_name = f"{base_name}.{self.output_format.lower()}"
                            self.status_updated.emit(f"Processing original size...")
                            processed_img = img.copy()
                            
                            # Apply ICO size optimization to original as well
                            if self.output_format.lower() == 'ico':
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
                            if self.output_format.lower() == 'ico':
                                if width > 256 or height > 256:
                                    # ICO has practical limits in PIL - 256x256 works reliably
                                    max_size = 256
                                    if width > height:
                                        height = int(height * max_size / width)
                                        width = max_size
                                    else:
                                        width = int(width * max_size / height)
                                        height = max_size
                            
                            output_name = f"{base_name}_{size_str}.{self.output_format.lower()}"
                            self.status_updated.emit(f"Processing {size_str}...")
                            
                            # Resize image based on mode
                            if not self.lock_aspect_ratio or self.resize_mode == "stretch":
                                # Stretch mode: resize to exact dimensions (may distort)
                                processed_img = img.resize((width, height), Image.Resampling.LANCZOS)
                            
                            elif self.resize_mode == "fit":
                                # Fit mode: fit completely inside target size with background
                                original_width, original_height = img.size
                                aspect_ratio = original_width / original_height
                                target_ratio = width / height
                                
                                # Calculate the size that fits inside the target
                                if aspect_ratio > target_ratio:
                                    # Image is wider, fit by width
                                    new_width = width
                                    new_height = int(width / aspect_ratio)
                                else:
                                    # Image is taller, fit by height
                                    new_height = height
                                    new_width = int(height * aspect_ratio)
                                
                                # Resize the image
                                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                                
                                # Create new image with target size and background color
                                if img.mode == 'RGBA' or 'transparency' in img.info:
                                    processed_img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
                                else:
                                    processed_img = Image.new('RGB', (width, height), (255, 255, 255))
                                
                                # Paste the resized image in the center
                                x_offset = (width - new_width) // 2
                                y_offset = (height - new_height) // 2
                                processed_img.paste(resized_img, (x_offset, y_offset))
                            
                            elif self.resize_mode == "crop":
                                # Crop mode: fill target size completely, crop excess
                                original_width, original_height = img.size
                                aspect_ratio = original_width / original_height
                                target_ratio = width / height
                                
                                # Calculate the size that fills the target
                                if aspect_ratio > target_ratio:
                                    # Image is wider, scale by height and crop width
                                    new_height = height
                                    new_width = int(height * aspect_ratio)
                                else:
                                    # Image is taller, scale by width and crop height
                                    new_width = width
                                    new_height = int(width / aspect_ratio)
                                
                                # Resize the image
                                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                                
                                # Crop from center to target size
                                x_offset = (new_width - width) // 2
                                y_offset = (new_height - height) // 2
                                processed_img = resized_img.crop((x_offset, y_offset, x_offset + width, y_offset + height))
                        
                        # Save the processed image
                        output_path = Path(self.save_location) / output_name
                        
                        # Handle different formats
                        save_kwargs = {}
                        if self.output_format.lower() in ['jpeg', 'jpg']:
                            save_kwargs['quality'] = self.quality
                            save_kwargs['optimize'] = True
                            save_kwargs['dpi'] = (self.dpi, self.dpi)
                        elif self.output_format.lower() == 'webp':
                            # Optimize WebP settings for speed
                            save_kwargs['quality'] = min(self.quality, 85)  # Cap quality for speed
                            save_kwargs['method'] = 1  # Fastest method (0-6, lower is faster)
                            save_kwargs['lossless'] = False  # Ensure lossy compression for speed
                            save_kwargs['exact'] = False  # Allow approximations for speed
                            # WebP doesn't support DPI metadata directly
                        elif self.output_format.lower() == 'png':
                            save_kwargs['optimize'] = True
                            save_kwargs['dpi'] = (self.dpi, self.dpi)
                            # Use quality setting to control PNG compression level
                            # Higher quality = less compression (larger file)
                            # Lower quality = more compression (smaller file)
                            if self.quality >= 90:
                                save_kwargs['compress_level'] = 1  # Less compression, larger file
                            elif self.quality >= 70:
                                save_kwargs['compress_level'] = 6  # Default compression
                            else:
                                save_kwargs['compress_level'] = 9  # Maximum compression, smaller file
                        elif self.output_format.lower() == 'ico':
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
                        if self.output_format.lower() in ['png', 'jpeg', 'jpg']:
                            # Also set the DPI in the image info
                            processed_img.info['dpi'] = (self.dpi, self.dpi)
                        
                        # Handle format name for PIL
                        pil_format = self.output_format.upper()
                        if pil_format == 'JPG':
                            pil_format = 'JPEG'
                        
                        # Update status before saving (this is often the slow part)
                        self.status_updated.emit(f"Saving {output_name}...")
                        
                        # Special handling for ICO format
                        if pil_format == 'ICO':
                            try:
                                # Ensure image is in RGBA mode for ICO
                                if processed_img.mode != 'RGBA':
                                    processed_img = processed_img.convert('RGBA')
                                processed_img.save(str(output_path), format=pil_format, **save_kwargs)
                            except Exception as ico_error:
                                # If ICO save fails, try without any special parameters
                                print(f"ICO save failed with parameters, trying without: {ico_error}")
                                try:
                                    if processed_img.mode != 'RGBA':
                                        processed_img = processed_img.convert('RGBA')
                                    processed_img.save(str(output_path), format=pil_format)
                                except Exception as ico_error2:
                                    print(f"ICO save failed completely: {ico_error2}")
                                    # Skip this size if ICO conversion fails
                                    continue
                        else:
                            processed_img.save(str(output_path), format=pil_format, **save_kwargs)
                        output_files.append(str(output_path))
                        
                        # Update progress
                        self.progress_updated.emit(i + 1)
                        
                        # Small delay to allow UI updates and prevent blocking
                        self.msleep(10)  # 10ms delay
                        
                    except Exception as e:
                        self.conversion_error.emit(f"Error processing size {size}: {str(e)}")
                        return
            
            self.conversion_finished.emit(output_files)
            
        except Exception as e:
            self.conversion_error.emit(f"Conversion failed: {str(e)}")

def convert_image(input_path, output_path, output_format, size=None):
    """
    Utility function for single image conversion
    """
    try:
        with Image.open(input_path) as img:
            # Convert to RGB if necessary
            if output_format.lower() in ['jpeg', 'jpg'] and img.mode in ['RGBA', 'P']:
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize if size is specified
            if size and size != "original":
                if isinstance(size, tuple):
                    img = img.resize(size, Image.Resampling.LANCZOS)
            
            # Save with appropriate settings
            save_kwargs = {}
            if output_format.lower() in ['jpeg', 'jpg']:
                save_kwargs['quality'] = 95
                save_kwargs['optimize'] = True
            elif output_format.lower() == 'webp':
                save_kwargs['quality'] = 95
                save_kwargs['method'] = 4  # Faster method
                save_kwargs['lossless'] = False
            elif output_format.lower() == 'png':
                save_kwargs['optimize'] = True
                # Default to medium compression for utility function
                save_kwargs['compress_level'] = 6
            
            # Handle format name for PIL
            pil_format = output_format.upper()
            if pil_format == 'JPG':
                pil_format = 'JPEG'
            
            img.save(output_path, format=pil_format, **save_kwargs)
            return True
            
    except Exception as e:
        print(f"Conversion error: {e}")
        return False

def get_image_info(image_path):
    """
    Get basic information about an image file
    """
    try:
        with Image.open(image_path) as img:
            return {
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'width': img.width,
                'height': img.height
            }
    except Exception:
        return None