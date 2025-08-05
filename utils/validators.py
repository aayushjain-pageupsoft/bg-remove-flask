"""
Input validation utilities for the background removal API
"""
import os
from typing import Tuple, Optional
from PIL import Image
from werkzeug.datastructures import FileStorage
from config import Config

def allowed_file(filename: str) -> bool:
    """
    Check if the uploaded file has an allowed extension
    
    Args:
        filename (str): Name of the uploaded file
        
    Returns:
        bool: True if file extension is allowed, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def validate_image_file(file: FileStorage) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded image file
    
    Args:
        file (FileStorage): Uploaded file object
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    # Check if file exists
    if not file or not file.filename:
        return False, "No file provided"
    
    # Check file extension
    if not allowed_file(file.filename):
        return False, f"File type not allowed. Supported formats: {', '.join(Config.ALLOWED_EXTENSIONS)}"
    
    # Check file size (Flask handles MAX_CONTENT_LENGTH, but we can add custom validation)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    if file_size == 0:
        return False, "Empty file provided"
    
    if file_size > Config.MAX_CONTENT_LENGTH:
        return False, f"File too large. Maximum size: {Config.MAX_CONTENT_LENGTH // (1024*1024)}MB"
    
    # Validate image format and dimensions
    try:
        with Image.open(file.stream) as img:
            # Reset stream position
            file.stream.seek(0)
            
            width, height = img.size
            
            # Check minimum dimensions
            if width < Config.MIN_IMAGE_SIZE or height < Config.MIN_IMAGE_SIZE:
                return False, f"Image too small. Minimum dimensions: {Config.MIN_IMAGE_SIZE}x{Config.MIN_IMAGE_SIZE}px"
            
            # Check maximum dimensions
            if width > Config.MAX_IMAGE_WIDTH or height > Config.MAX_IMAGE_HEIGHT:
                return False, f"Image too large. Maximum dimensions: {Config.MAX_IMAGE_WIDTH}x{Config.MAX_IMAGE_HEIGHT}px"
            
            # Check if image has valid format
            if img.format not in ['PNG', 'JPEG', 'JPG', 'WEBP', 'BMP', 'TIFF']:
                return False, f"Unsupported image format: {img.format}"
                
        return True, None
        
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"

def validate_background_color(color: str) -> Tuple[bool, Optional[str]]:
    """
    Validate background color format
    
    Args:
        color (str): Color value (hex format expected)
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not color:
        return True, None  # Optional parameter
    
    # Check hex color format
    if not color.startswith('#') or len(color) != 7:
        return False, "Background color must be in hex format (#RRGGBB)"
    
    try:
        int(color[1:], 16)  # Try to convert hex to int
        return True, None
    except ValueError:
        return False, "Invalid hex color format"