"""
Configuration settings for the background removal API
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # File upload settings
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_FILE_SIZE', 16 * 1024 * 1024))  # 16MB for Railway
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'temp_uploads')
    
    # Image processing settings
    MAX_IMAGE_WIDTH = int(os.environ.get('MAX_IMAGE_WIDTH', 4000))
    MAX_IMAGE_HEIGHT = int(os.environ.get('MAX_IMAGE_HEIGHT', 4000))
    MIN_IMAGE_SIZE = int(os.environ.get('MIN_IMAGE_SIZE', 100))
    
    # API settings
    RATE_LIMIT = os.environ.get('RATE_LIMIT', '1500 per hour')
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff'}

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}