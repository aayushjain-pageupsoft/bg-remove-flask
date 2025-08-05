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
- `GET /` - Home page with API information
- `GET /health` - Health check (returns status and port info)
- `POST /remove-background` - Background removal
- `GET /api-info` - API documentation

## Testing

Test your deployment:
```bash
curl https://your-app.railway.app/health
```

## Memory Optimization

- Single worker configuration for Railway's memory limits
- Model pre-loading to avoid cold starts
- Request timeout set to 300 seconds for large images