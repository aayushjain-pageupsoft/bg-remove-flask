# Veena Flask Background Removal API

A powerful and production-ready Flask API for AI-powered background removal from images. Built for Veena Garments to provide seamless background removal capabilities with optional background color replacement.

## 🚀 Features

- **AI-Powered Background Removal**: Uses advanced U2Net model via rembg library
- **Background Color Replacement**: Optional solid color background addition
- **Multiple Format Support**: PNG, JPG, JPEG, WebP, BMP, TIFF
- **Size Optimization**: Automatic image resizing for optimal processing
- **Comprehensive Validation**: File type, size, and format validation
- **Production Ready**: Health checks, logging, error handling
- **CORS Enabled**: Cross-origin resource sharing support
- **Environment Configuration**: Separate dev/prod configurations

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Architecture](#architecture)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)

## 🛠 Installation

### Prerequisites

- Python 3.8+
- pip package manager
- Virtual environment (recommended)

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd veena-flask
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment configuration (optional)**
```bash
cp .env.example .env  # Create environment file
# Edit .env with your settings
```

## 🚀 Quick Start

1. **Start the development server**
```bash
python app.py
```

2. **Test the API**
```bash
curl -X GET http://localhost:8000/health
```

The API will be available at `http://localhost:8000`

## 📡 API Endpoints

### Health Check
- **Endpoint**: `GET /health`
- **Description**: Check API health status
- **Response**:
```json
{
  "status": "healthy",
  "service": "background-removal-api"
}
```

### Background Removal
- **Endpoint**: `POST /remove-background`
- **Description**: Remove background from uploaded image
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `image` (required): Image file
  - `background_color` (optional): Hex color code (e.g., #FF0000)

**Example Request**:
```bash
curl -X POST \
  -F "image=@your-image.jpg" \
  -F "background_color=#FFFFFF" \
  http://localhost:8000/remove-background \
  --output result.png
```

**Response**: Processed image file with background removed

### API Information
- **Endpoint**: `GET /api-info`
- **Description**: Get API documentation and supported formats
- **Response**:
```json
{
  "service": "Background Removal API",
  "version": "1.0.0",
  "endpoints": {
    "POST /remove-background": {
      "description": "Remove background from uploaded image",
      "parameters": {
        "image": "Image file (required)",
        "background_color": "Hex color like #FF0000 (optional)"
      }
    }
  },
  "supported_formats": ["png", "jpg", "jpeg", "webp", "bmp"]
}
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Flask Settings
SECRET_KEY=your-secret-key-here
DEBUG=False

# File Upload Settings
MAX_FILE_SIZE=8388608  # 8MB in bytes
UPLOAD_FOLDER=temp_uploads

# Image Processing Settings
MAX_IMAGE_WIDTH=4000
MAX_IMAGE_HEIGHT=4000
MIN_IMAGE_SIZE=100

# API Settings
RATE_LIMIT=1500 per hour
CORS_ORIGINS=*

# Server Settings
PORT=8000
```

### Configuration Classes

- **DevelopmentConfig**: Debug enabled, verbose logging
- **ProductionConfig**: Optimized for production deployment

## 💡 Usage Examples

### Python Client Example

```python
import requests

# Basic background removal
with open('image.jpg', 'rb') as f:
    files = {'image': f}
    response = requests.post('http://localhost:8000/remove-background', files=files)
    
    with open('result.png', 'wb') as output:
        output.write(response.content)

# With background color
with open('image.jpg', 'rb') as f:
    files = {'image': f}
    data = {'background_color': '#FF0000'}
    response = requests.post('http://localhost:8000/remove-background', files=files, data=data)
    
    with open('result_red_bg.png', 'wb') as output:
        output.write(response.content)
```

### JavaScript Client Example

```javascript
// Using fetch API
const formData = new FormData();
formData.append('image', fileInput.files[0]);
formData.append('background_color', '#FFFFFF');

fetch('http://localhost:8000/remove-background', {
    method: 'POST',
    body: formData
})
.then(response => response.blob())
.then(blob => {
    const url = URL.createObjectURL(blob);
    const img = document.createElement('img');
    img.src = url;
    document.body.appendChild(img);
});
```

### cURL Examples

```bash
# Basic background removal
curl -X POST \
  -F "image=@photo.jpg" \
  http://localhost:8000/remove-background \
  --output transparent.png

# With red background
curl -X POST \
  -F "image=@photo.jpg" \
  -F "background_color=#FF0000" \
  http://localhost:8000/remove-background \
  --output red_background.png

# Check API info
curl -X GET http://localhost:8000/api-info
```

## 🏗 Architecture

### Project Structure

```
veena-flask/
├── app.py                    # Main Flask application
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── ReadME.md                 # This documentation
├── utils/                    # Utility modules
│   ├── __init__.py          # Package initialization
│   ├── image_processor.py   # Advanced image processing
│   └── validators.py        # Input validation utilities
└── venv/                    # Virtual environment
```

### Core Components

1. **Flask Application** (`app.py`)
   - Main server and route definitions
   - Request handling and response generation
   - Error handling and logging

2. **Configuration** (`config.py`)
   - Environment-based configuration
   - Development and production settings
   - Configurable limits and parameters

3. **Image Processor** (`utils/image_processor.py`)
   - AI-powered background removal
   - Image optimization and resizing
   - Format conversion and compositing

4. **Validators** (`utils/validators.py`)
   - File type and size validation
   - Image format verification
   - Input sanitization

### Processing Flow

1. **Request Validation**: File type, size, and format checks
2. **Image Loading**: PIL-based image loading and validation
3. **Background Removal**: U2Net model via rembg library
4. **Optional Processing**: Background color addition
5. **Response Generation**: PNG format output with proper headers

## 🧪 Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

### Code Quality

```bash
# Install development dependencies
pip install black flake8 isort

# Format code
black .
isort .

# Lint code
flake8 .
```

### Adding New Features

1. Create feature branch: `git checkout -b feature/new-feature`
2. Add your changes with tests
3. Update documentation
4. Submit pull request

## 🚀 Deployment

### Development Deployment

```bash
python app.py
```

### Production Deployment with Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 4 app:app
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:app"]
```

```bash
# Build and run
docker build -t veena-flask-api .
docker run -p 8000:8000 veena-flask-api
```

### Environment Variables for Production

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
MAX_FILE_SIZE=16777216
CORS_ORIGINS=https://yourdomain.com
```

## 📊 Performance Considerations

- **File Size Limits**: Default 16MB, configurable
- **Image Optimization**: Automatic resizing for large images
- **Model Caching**: rembg session reuse for better performance
- **Memory Management**: Efficient image processing pipeline

## 🔒 Security Features

- **File Type Validation**: Whitelist-based file extension checking
- **Size Limits**: Configurable upload size restrictions
- **Input Sanitization**: Comprehensive validation pipeline
- **Error Handling**: No sensitive information in error responses
- **CORS Configuration**: Controlled cross-origin access

## 🐛 Troubleshooting

### Common Issues

1. **"No module named 'rembg'"**
   ```bash
   pip install rembg
   ```

2. **Memory errors with large images**
   - Reduce MAX_IMAGE_WIDTH/HEIGHT in config
   - Increase system memory allocation

3. **CORS errors**
   - Check CORS_ORIGINS configuration
   - Ensure proper headers in requests

4. **File upload errors**
   - Verify file size limits
   - Check file format support

## 📝 API Response Codes

- `200`: Success
- `400`: Bad Request (validation errors)
- `413`: Payload Too Large (file size exceeded)
- `500`: Internal Server Error (processing failed)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [rembg](https://github.com/danielgatis/rembg) - AI background removal library
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Pillow](https://pillow.readthedocs.io/) - Image processing library

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact: [your-email@example.com]

---

Built with ❤️ for Veena Garments