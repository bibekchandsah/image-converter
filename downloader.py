"""
Image Downloader - Handles fetching images from URLs
"""

import os
import tempfile
import requests
from pathlib import Path
from urllib.parse import urlparse
from PySide6.QtCore import QThread, Signal

class ImageDownloader(QThread):
    download_finished = Signal(str)
    download_error = Signal(str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
    
    def run(self):
        try:
            # Validate URL
            parsed_url = urlparse(self.url)
            if not parsed_url.scheme or not parsed_url.netloc:
                self.download_error.emit("Invalid URL format")
                return
            
            # Set headers to mimic a browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Download the image
            response = requests.get(self.url, headers=headers, timeout=30, stream=True)
            response.raise_for_status()
            
            # Check if the content is an image
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                self.download_error.emit("URL does not point to an image file")
                return
            
            # Determine file extension from content type or URL
            extension = self.get_extension_from_content_type(content_type)
            if not extension:
                # Try to get extension from URL
                url_path = Path(parsed_url.path)
                extension = url_path.suffix.lower()
                if not extension or extension not in ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp', '.ico', '.tiff']:
                    extension = '.jpg'  # Default extension
            
            # Create temporary file
            temp_dir = tempfile.gettempdir()
            temp_filename = f"downloaded_image_{os.getpid()}{extension}"
            temp_path = Path(temp_dir) / temp_filename
            
            # Save the image
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Verify the file was created and has content
            if temp_path.exists() and temp_path.stat().st_size > 0:
                self.download_finished.emit(str(temp_path))
            else:
                self.download_error.emit("Failed to save downloaded image")
                
        except requests.exceptions.Timeout:
            self.download_error.emit("Download timeout - please try again")
        except requests.exceptions.ConnectionError:
            self.download_error.emit("Connection error - check your internet connection")
        except requests.exceptions.HTTPError as e:
            self.download_error.emit(f"HTTP error: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            self.download_error.emit(f"Download failed: {str(e)}")
        except Exception as e:
            self.download_error.emit(f"Unexpected error: {str(e)}")
    
    def get_extension_from_content_type(self, content_type):
        """
        Map content type to file extension
        """
        content_type_map = {
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/png': '.png',
            'image/webp': '.webp',
            'image/gif': '.gif',
            'image/bmp': '.bmp',
            'image/x-icon': '.ico',
            'image/vnd.microsoft.icon': '.ico',
            'image/tiff': '.tiff',
            'image/x-tiff': '.tiff'
        }
        
        return content_type_map.get(content_type.split(';')[0].strip())

def download_image_sync(url, output_path):
    """
    Synchronous image download function
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        if not content_type.startswith('image/'):
            return False, "URL does not point to an image"
        
        # Save the file
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return True, "Download successful"
        
    except Exception as e:
        return False, str(e)

def is_valid_image_url(url):
    """
    Check if URL appears to be a valid image URL
    """
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # Check if URL ends with image extension
        path = Path(parsed.path)
        valid_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp', '.ico', '.tiff'}
        
        return path.suffix.lower() in valid_extensions
        
    except Exception:
        return False