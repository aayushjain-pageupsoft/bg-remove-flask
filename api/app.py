"""
Railway-optimized Flask API for background removal
"""
import os
import sys
import logging
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
import io
from rembg import remove

# Add the parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ✅ PRE-LOAD MODEL AT STARTUP (Skip if memory constrained)
preload_model = os.environ.get('PRELOAD_MODEL', 'false').lower() == 'true'
if preload_model:
    logger.info("🚀 Pre-loading background removal model...")
    try:
        # Force model loading with a dummy image
        dummy_image = Image.new('RGB', (100, 100), color='white')
        remove(dummy_image)
        logger.info("✅ Model loaded successfully! API ready for requests.")
    except Exception as e:
        logger.error(f"❌ Failed to preload model: {e}")
        logger.info("Continuing without preload - model will load on first request")
else:
    logger.info("Model preloading disabled - will load on first request")

    
# Create Flask app with Railway configuration
app = Flask(__name__)

# Load configuration based on environment
env = os.environ.get('FLASK_ENV', 'production')
if env == 'development':
    app.config.from_object(Config)
else:
    app.config.from_object(Config)

# Set file upload limit
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

# Enable CORS with configuration
CORS(app, origins=Config.CORS_ORIGINS.split(',') if Config.CORS_ORIGINS != '*' else '*')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'background-removal-api'
    })

@app.route('/remove-background', methods=['POST'])
def remove_background():
    """Remove background from uploaded image"""
    try:
        # Check if image file is provided
        if 'image' not in request.files:
            return jsonify({
                'error': 'No image provided',
                'message': 'Please upload an image file'
            }), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({
                'error': 'No image selected',
                'message': 'Please select an image file'
            }), 400
        
        # Validate file extension using config
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS):
            return jsonify({
                'error': 'Invalid file type',
                'message': f'Supported formats: {", ".join(Config.ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Process image
        logger.info(f"Processing image: {file.filename}")
        
        # Load and process image
        input_image = Image.open(file.stream)
        logger.info(f"Image loaded: {input_image.size}")
        
        # Remove background
        output_image = remove(input_image)
        logger.info("Background removal completed")
        
        # Get background color if provided
        background_color = request.form.get('background_color', '')
        
        # Add background color if specified
        if background_color and background_color.startswith('#') and len(background_color) == 7:
            try:
                # Create background with color
                if output_image.mode != 'RGBA':
                    output_image = output_image.convert('RGBA')
                
                # Create colored background
                colored_bg = Image.new('RGBA', output_image.size, background_color)
                
                # Composite images
                final_image = Image.alpha_composite(colored_bg, output_image)
                
                # Convert to RGB
                output_image = Image.new('RGB', final_image.size, (255, 255, 255))
                output_image.paste(final_image, mask=final_image.split()[-1] if len(final_image.split()) == 4 else None)
                
                logger.info(f"Added background color: {background_color}")
            except Exception as e:
                logger.warning(f"Failed to add background color: {str(e)}")
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        output_format = 'PNG'
        output_image.save(img_buffer, format=output_format)
        img_buffer.seek(0)
        
        logger.info("Image processing completed successfully")
        
        # Return processed image
        response = send_file(
            img_buffer,
            mimetype='image/png',
            as_attachment=True,
            download_name=f'removed_bg_{file.filename}'
        )
        
        # Add cache control headers
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
        
    except Exception as e:
        import traceback
        logger.error(f"Error processing image: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({
            'error': 'Processing failed',
            'message': 'Failed to process image. Please try again with a different image.',
            'debug': str(e) if app.debug else None
        }), 500

@app.route('/api-info', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        'service': 'Background Removal API',
        'version': '1.0.0',
        'endpoints': {
            'POST /remove-background': {
                'description': 'Remove background from uploaded image',
                'parameters': {
                    'image': 'Image file (required)',
                    'background_color': 'Hex color like #FF0000 (optional)'
                }
            }
        },
        'supported_formats': list(Config.ALLOWED_EXTENSIONS)
    })

# For gunicorn WSGI
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Starting Background Removal API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
