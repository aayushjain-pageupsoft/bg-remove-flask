# Railway Deployment Guide

## Quick Deploy Steps

1. **Connect to Railway:**
   - Go to [railway.app](https://railway.app)
   - Sign up/Login with GitHub
   - Click "Deploy from GitHub repo"
   - Select this repository

2. **Environment Variables:**
   - Railway automatically sets PORT (no configuration needed)
   - All other settings use sensible defaults

3. **Deployment:**
   - Railway will automatically detect the Dockerfile
   - Uses minimal Flask app (app.py) for faster startup
   - Health check available at `/health`
   - Home page available at `/` with API info

## Configuration Files

- `app.py`: Minimal Flask application (main entry point)
- `Dockerfile`: Container build configuration with system dependencies  
- `Procfile`: Gunicorn configuration for Railway (backup)
- `railway.json`: Railway-specific deployment settings

## API Endpoints

After deployment, your API will be available at:
- `GET /` - Home page with API information and model status
- `GET /health` - Health check (includes model loading status)
- `GET|POST /warmup` - Preload the background removal model for faster processing
- `POST /remove-background` - Background removal (uses preloaded model)
- `GET /api-info` - API documentation with usage tips

## Testing

Test your deployment:
```bash
# Check health and model status
curl https://your-app.railway.app/health

# Warm up the model (recommended on first use)
curl -X POST https://your-app.railway.app/warmup

# Test background removal
curl -X POST -F "image=@your-image.jpg" https://your-app.railway.app/remove-background --output result.png
```

## Performance Tips

- **First Request**: Call `/warmup` first to preload the model
- **Model Status**: Check `/health` to see if the model is ready
- **Background Loading**: The model loads automatically on app startup
- **Session Reuse**: Subsequent requests will be much faster

## Memory Optimization

- Single worker configuration for Railway's memory limits
- Model pre-loading to avoid cold starts
- Request timeout set to 300 seconds for large images