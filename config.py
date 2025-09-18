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
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_FILE_SIZE', 8 * 1024 * 1024))  # 8MB for Azure App Service
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/tmp/uploads')  # Use /tmp for Azure
    
    # Image processing settings
    MAX_IMAGE_WIDTH = int(os.environ.get('MAX_IMAGE_WIDTH', 2048))  # Reduced for Azure
    MAX_IMAGE_HEIGHT = int(os.environ.get('MAX_IMAGE_HEIGHT', 2048))  # Reduced for Azure
    MIN_IMAGE_SIZE = int(os.environ.get('MIN_IMAGE_SIZE', 100))
    
    # API settings
    RATE_LIMIT = os.environ.get('RATE_LIMIT', '1000 per hour')  # Reduced for Azure
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    
    # Azure-specific settings
    WEBSITE_SITE_NAME = os.environ.get('WEBSITE_SITE_NAME', 'local')
    WEBSITE_INSTANCE_ID = os.environ.get('WEBSITE_INSTANCE_ID', 'local')
    
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