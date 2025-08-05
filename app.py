"""
Minimal Flask API for Railway deployment with model preloading
"""
import os
import logging
import threading
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
import io
from rembg import remove, new_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for model management
rembg_session = None
model_loaded = False
model_lock = threading.Lock()

# Create Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Enable CORS
CORS(app)

def initialize_model():
    """Initialize the rembg model in a thread-safe way"""
    global rembg_session, model_loaded
    
    with model_lock:
        if not model_loaded:
            try:
                logger.info("🚀 Initializing background removal model...")
                rembg_session = new_session('u2net')
                
                # Warm up the model with a dummy image
                dummy_image = Image.new('RGB', (100, 100), color='white')
                remove(dummy_image, session=rembg_session)
                
                model_loaded = True
                logger.info("✅ Model initialized and warmed up successfully!")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to initialize model: {e}")
                return False
    
    return model_loaded

def get_rembg_session():
    """Get the rembg session, initializing if necessary"""
    global rembg_session, model_loaded
    
    if not model_loaded:
        if not initialize_model():
            return None
    
    return rembg_session

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    logger.info("Health check called")
    return jsonify({
        'status': 'healthy',
        'service': 'background-removal-api',
        'port': os.environ.get('PORT', '8000'),
        'model_loaded': model_loaded
    })

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Background Removal API is running',
        'health': '/health',
        'warmup': '/warmup',
        'remove': '/remove-background',
        'model_loaded': model_loaded
    })

@app.route('/warmup', methods=['POST', 'GET'])
def warmup_model():
    """Warmup endpoint to preload the model"""
    try:
        logger.info("Model warmup requested")
        if initialize_model():
            return jsonify({
                'status': 'success',
                'message': 'Model loaded and warmed up successfully',
                'model_loaded': True
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to load model',
                'model_loaded': False
            }), 503
    except Exception as e:
        logger.error(f"Warmup failed: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Warmup failed: {str(e)}',
            'model_loaded': False
        }), 500

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
        
        # Validate file extension
        allowed_extensions = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({
                'error': 'Invalid file type',
                'message': f'Supported formats: {", ".join(allowed_extensions)}'
            }), 400
        
        # Process image
        logger.info(f"Processing image: {file.filename}")
        
        # Load and process image
        input_image = Image.open(file.stream)
        logger.info(f"Image loaded: {input_image.size}")
        
        # Remove background using session for better performance
        session = get_rembg_session()
        if session is None:
            logger.error("Model not available")
            return jsonify({
                'error': 'Model loading failed',
                'message': 'Background removal model is not available. Please try again.'
            }), 503
        
        logger.info("Removing background with initialized model...")
        output_image = remove(input_image, session=session)
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
            'debug': str(e)
        }), 500

@app.route('/api-info', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        'service': 'Background Removal API',
        'version': '1.1.0',
        'model_loaded': model_loaded,
        'endpoints': {
            'GET /': 'Home page with API status',
            'GET /health': 'Health check with model status',
            'GET|POST /warmup': 'Preload the background removal model',
            'POST /remove-background': {
                'description': 'Remove background from uploaded image',
                'parameters': {
                    'image': 'Image file (required)',
                    'background_color': 'Hex color like #FF0000 (optional)'
                },
                'note': 'First request may take longer if model is not preloaded'
            }
        },
        'supported_formats': ['png', 'jpg', 'jpeg', 'webp', 'bmp'],
        'tips': [
            'Call /warmup first to preload the model for faster processing',
            'Model loads automatically in background on app startup',
            'Check /health to see if model is ready'
        ]
    })

# For gunicorn WSGI
application = app

# Initialize model in background thread on startup
def startup_model_init():
    """Initialize model in background on app startup"""
    logger.info("Starting background model initialization...")
    initialize_model()

# Start model initialization in background
startup_thread = threading.Thread(target=startup_model_init, daemon=True)
startup_thread.start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Starting Background Removal API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)