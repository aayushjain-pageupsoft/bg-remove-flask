# Railway Deployment Guide

## Quick Deploy Steps

1. **Connect to Railway:**
   - Go to [railway.app](https://railway.app)
   - Sign up/Login with GitHub
   - Click "Deploy from GitHub repo"
   - Select this repository

2. **Environment Variables (Optional):**
   - Set these in Railway dashboard if needed:
   ```
   SECRET_KEY=your-production-secret-key
   MAX_FILE_SIZE=16777216
   CORS_ORIGINS=*
   ```

3. **Deployment:**
   - Railway will automatically detect the configuration
   - Uses nixpacks.toml for build configuration
   - Uses Procfile for start command
   - Health check available at `/health`

## Configuration Files

- `Procfile`: Gunicorn configuration for Railway
- `nixpacks.toml`: Build dependencies and commands
- `railway.json`: Railway-specific deployment settings
- `config.py`: Application configuration with environment variables

## API Endpoints

After deployment, your API will be available at:
- `GET /health` - Health check
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