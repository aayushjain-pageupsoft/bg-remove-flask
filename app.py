"""
Minimal Flask API for Railway deployment - simplified for reliability
"""
import os
import logging
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
import io
from rembg import remove

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # Reduced to 8MB for Railway

# Enable CORS
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'background-removal-api'
    })

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Background Removal API is running',
        'health': '/health',
        'remove': '/remove-background',
        'info': '/api-info'
    })

@app.route('/remove-background', methods=['POST'])
def remove_background():
    """Remove background from uploaded image"""
    try:
        logger.info("Background removal request received")
        
        # Check if image file is provided
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        # Validate file extension
        allowed_extensions = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'error': 'Invalid file type'}), 400
        
        logger.info(f"Processing {file.filename}")
        
        # Load image
        input_image = Image.open(file.stream)
        
        # Optimize image size for faster processing
        max_size = 1024
        if max(input_image.size) > max_size:
            ratio = max_size / max(input_image.size)
            new_size = tuple(int(dim * ratio) for dim in input_image.size)
            input_image = input_image.resize(new_size, Image.Resampling.LANCZOS)
            logger.info(f"Resized to {new_size}")
        
        logger.info("Starting background removal...")
        
        # Remove background (simplified approach)
        output_image = remove(input_image)
        
        logger.info("Background removal completed")
        
        # Handle background color if provided
        background_color = request.form.get('background_color', '')
        if background_color and background_color.startswith('#') and len(background_color) == 7:
            try:
                if output_image.mode != 'RGBA':
                    output_image = output_image.convert('RGBA')
                
                colored_bg = Image.new('RGBA', output_image.size, background_color)
                output_image = Image.alpha_composite(colored_bg, output_image)
                
                # Convert to RGB
                final_img = Image.new('RGB', output_image.size, (255, 255, 255))
                final_img.paste(output_image, mask=output_image.split()[-1])
                output_image = final_img
                
            except Exception as e:
                logger.warning(f"Background color failed: {e}")
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        output_image.save(img_buffer, format='PNG', optimize=True)
        img_buffer.seek(0)
        
        logger.info("Sending response")
        
        return send_file(
            img_buffer,
            mimetype='image/png',
            as_attachment=True,
            download_name=f'bg_removed_{file.filename.split(".")[0]}.png'
        )
        
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        return jsonify({
            'error': 'Processing failed',
            'message': str(e)
        }), 500

@app.route('/api-info', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        'service': 'Background Removal API',
        'version': '1.2.0',
        'endpoints': {
            'GET /': 'Home page',
            'GET /health': 'Health check',
            'POST /remove-background': {
                'description': 'Remove background from uploaded image',
                'parameters': {
                    'image': 'Image file (required)',
                    'background_color': 'Hex color like #FF0000 (optional)'
                }
            }
        },
        'supported_formats': ['png', 'jpg', 'jpeg', 'webp', 'bmp'],
        'note': 'Images are automatically resized to 1024px max for faster processing'
    })

# For gunicorn WSGI
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Starting Background Removal API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)