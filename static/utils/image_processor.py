"""
Image processing utilities for background removal
"""
import io
import logging
from typing import Optional, Tuple
from PIL import Image, ImageDraw
import numpy as np
from rembg import remove, new_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageProcessor:
    """Handle image processing operations"""
    
    def __init__(self):
        """Initialize the image processor with rembg session"""
        try:
            # Initialize rembg session for better performance
            self.session = new_session('u2net')  # You can use different models
            logger.info("ImageProcessor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ImageProcessor: {str(e)}")
            self.session = None
    
    def remove_background(self, input_image: Image.Image) -> Image.Image:
        """
        Remove background from image using rembg
        
        Args:
            input_image (PIL.Image.Image): Input image
            
        Returns:
            PIL.Image.Image: Image with background removed (transparent)
            
        Raises:
            Exception: If background removal fails
        """
        try:
            logger.info(f"Processing image: {input_image.size}, mode: {input_image.mode}")
            
            # Convert image to RGB if necessary
            if input_image.mode not in ['RGB', 'RGBA']:
                input_image = input_image.convert('RGB')
                logger.info("Converted image to RGB mode")
            
            # Remove background
            if self.session:
                output_image = remove(input_image, session=self.session)
            else:
                output_image = remove(input_image)
            
            logger.info("Background removal completed successfully")
            return output_image
            
        except Exception as e:
            logger.error(f"Background removal failed: {str(e)}")
            raise Exception(f"Failed to remove background: {str(e)}")
    
    def add_background_color(self, transparent_image: Image.Image, 
                           bg_color: str = '#FFFFFF') -> Image.Image:
        """
        Add solid color background to transparent image
        
        Args:
            transparent_image (PIL.Image.Image): Image with transparent background
            bg_color (str): Background color in hex format
            
        Returns:
            PIL.Image.Image: Image with colored background
        """
        try:
            # Create background image
            if transparent_image.mode != 'RGBA':
                transparent_image = transparent_image.convert('RGBA')
            
            # Create background
            background = Image.new('RGBA', transparent_image.size, bg_color + '00')
            
            # Create colored background
            colored_bg = Image.new('RGBA', transparent_image.size, bg_color)
            
            # Composite images
            result = Image.alpha_composite(colored_bg, transparent_image)
            
            # Convert to RGB for final output
            final_image = Image.new('RGB', result.size, (255, 255, 255))
            final_image.paste(result, mask=result.split()[-1])
            
            logger.info(f"Added background color: {bg_color}")
            return final_image
            
        except Exception as e:
            logger.error(f"Failed to add background color: {str(e)}")
            raise Exception(f"Failed to add background color: {str(e)}")
    
    def optimize_image_size(self, image: Image.Image, max_size: int = 2048) -> Image.Image:
        """
        Optimize image size for processing while maintaining aspect ratio
        
        Args:
            image (PIL.Image.Image): Input image
            max_size (int): Maximum dimension size
            
        Returns:
            PIL.Image.Image: Resized image
        """
        width, height = image.size
        
        if max(width, height) <= max_size:
            return image
        
        # Calculate new dimensions
        if width > height:
            new_width = max_size
            new_height = int((height * max_size) / width)
        else:
            new_height = max_size
            new_width = int((width * max_size) / height)
        
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        logger.info(f"Resized image from {width}x{height} to {new_width}x{new_height}")
        
        return resized_image
    
    def image_to_bytes(self, image: Image.Image, format: str = 'PNG', 
                      quality: int = 95) -> io.BytesIO:
        """
        Convert PIL Image to bytes
        
        Args:
            image (PIL.Image.Image): Input image
            format (str): Output format
            quality (int): Image quality for JPEG
            
        Returns:
            io.BytesIO: Image as bytes buffer
        """
        img_buffer = io.BytesIO()
        
        if format.upper() == 'JPEG' and image.mode in ['RGBA', 'P']:
            # Convert to RGB for JPEG
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'RGBA':
                rgb_image.paste(image, mask=image.split()[-1])
            else:
                rgb_image.paste(image)
            image = rgb_image
        
        save_kwargs = {'format': format}
        if format.upper() == 'JPEG':
            save_kwargs['quality'] = quality
            save_kwargs['optimize'] = True
        
        image.save(img_buffer, **save_kwargs)
        img_buffer.seek(0)
        
        return img_buffer
