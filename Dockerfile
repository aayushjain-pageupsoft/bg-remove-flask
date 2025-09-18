FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for image processing
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create temp directory for Azure
RUN mkdir -p /tmp/uploads

# Expose port (Azure will provide the actual port via $PORT)
EXPOSE 8000

# Run with gunicorn optimized for Azure App Service
CMD gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 240 --max-requests 1000 --max-requests-jitter 100 --log-level info app:application