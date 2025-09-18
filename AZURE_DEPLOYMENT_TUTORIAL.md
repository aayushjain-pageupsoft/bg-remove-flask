# Complete Azure App Service Deployment Tutorial for Flask Background Removal API

## Table of Contents
1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Project Structure](#project-structure)
4. [Azure-Specific File Configuration](#azure-specific-file-configuration)
5. [Docker Multi-Platform Build](#docker-multi-platform-build)
6. [Azure Container Registry Setup](#azure-container-registry-setup)
7. [Azure App Service Deployment](#azure-app-service-deployment)
8. [Troubleshooting Common Issues](#troubleshooting-common-issues)
9. [Security Best Practices](#security-best-practices)
10. [Monitoring and Maintenance](#monitoring-and-maintenance)

---

## Project Overview

This tutorial demonstrates how to deploy a Flask-based background removal API to Azure App Service using Docker containers. The application uses the `rembg` library for AI-powered background removal and is optimized for production deployment on Azure.

### Key Technologies Used:
- **Flask**: Web framework for the API
- **rembg**: AI library for background removal
- **Docker**: Containerization platform
- **Azure Container Registry**: Private container registry
- **Azure App Service**: Platform-as-a-Service hosting
- **Gunicorn**: Production WSGI server

---

## Prerequisites

### Required Tools:
1. **Docker Desktop**: For building and testing containers locally
2. **Azure CLI**: For managing Azure resources
3. **Python 3.11+**: For local development (optional)
4. **Azure Subscription**: With appropriate permissions

### Required Azure Resources:
1. **Azure Container Registry**: To store Docker images
2. **Azure App Service**: To host the application
3. **Resource Group**: To organize resources

### Permission Requirements:
- Contributor access to Resource Group
- AcrPush/AcrPull permissions on Container Registry
- App Service Contributor role

---

## Project Structure

```
bg-remove-flask/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker container definition
├── startup.txt                 # Azure App Service startup command
├── web.config                  # IIS configuration for Azure
├── .deployment                 # Azure deployment configuration
├── deploy.sh                   # Deployment script
├── .dockerignore              # Docker ignore file
└── utils/                     # Utility modules
    ├── __init__.py
    ├── image_processor.py
    └── validators.py
```

---

## Azure-Specific File Configuration

### 1. Dockerfile Configuration

**Purpose**: Defines how to build the Docker container for Azure App Service

**Key Azure Optimizations**:
- Uses Python 3.11 (better Azure compatibility)
- Installs system dependencies for image processing
- Creates `/tmp/uploads` directory for Azure's file system
- Uses dynamic port binding with `$PORT` environment variable
- Optimized gunicorn settings for Azure

```dockerfile
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
```

**Why these settings?**:
- `--workers 1`: Azure App Service has memory limitations
- `--timeout 240`: Image processing can take time
- `--max-requests 1000`: Prevents memory leaks
- `$PORT`: Azure dynamically assigns ports

### 2. startup.txt

**Purpose**: Tells Azure App Service how to start the container

```bash
gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 240 --max-requests 1000 --max-requests-jitter 100 --log-level info app:application
```

**Why needed?**: Provides an alternative startup method for Azure App Service

### 3. web.config

**Purpose**: IIS configuration for Python applications on Azure

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified"/>
    </handlers>
    <httpPlatform processPath="D:\home\Python\python.exe"
                  arguments="D:\home\site\wwwroot\startup.py"
                  stdoutLogEnabled="true"
                  stdoutLogFile="D:\home\LogFiles\python.log"
                  startupTimeLimit="60"
                  startupRetryCount="3">
      <environmentVariables>
        <environmentVariable name="PYTHONPATH" value="D:\home\site\wwwroot" />
      </environmentVariables>
    </httpPlatform>
  </system.webServer>
</configuration>
```

**Why needed?**: Provides routing configuration for Azure's IIS-based hosting

### 4. .deployment

**Purpose**: Specifies custom deployment script for Azure

```ini
[config]
command = bash deploy.sh
```

### 5. deploy.sh

**Purpose**: Custom deployment script for Azure

```bash
#!/bin/bash

# Azure App Service deployment script
echo "Starting Azure deployment..."

# Install Python dependencies
echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Deployment completed successfully!"
```

**Why needed?**: Provides custom deployment logic if needed

### 6. Updated requirements.txt

**Purpose**: Pinned dependencies for production stability

```txt
Flask==3.0.3
Flask-CORS==4.0.1
rembg==2.0.59
Pillow==10.4.0
numpy==1.26.4
gunicorn==22.0.0
python-dotenv==1.0.1
Werkzeug==3.0.3
onnxruntime==1.18.1
```

**Why pinned versions?**: Ensures consistent deployments and prevents breaking changes

### 7. Updated config.py

**Purpose**: Azure-optimized configuration settings

```python
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
```

**Key Azure Changes**:
- Reduced file size limits (8MB vs 16MB)
- Lower image dimensions (2048px vs 4000px)
- `/tmp/uploads` for temporary files
- Azure environment variable detection

---

## Docker Multi-Platform Build

### Step 1: Create Multi-Platform Builder

```bash
docker buildx create --name multiplatform --use
```

**Why?**: Enables building for multiple CPU architectures (Intel/AMD and ARM)

### Step 2: Build Multi-Platform Image

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t bg-remove-flask:multiplatform --push .
```

**Platforms Explained**:
- `linux/amd64`: Intel/AMD processors (most common)
- `linux/arm64`: ARM processors (Apple Silicon, some cloud instances)

### Step 3: Verify Multi-Platform Build

```bash
docker buildx imagetools inspect veenag.azurecr.io/bg-remove-flask:latest
```

**Expected Output**:
```
Manifests: 
  Platform:    linux/amd64
  Platform:    linux/arm64
```

---

## Azure Container Registry Setup

### Step 1: Login to Azure Container Registry

```bash
az login
az acr login --name veenag
```

### Step 2: Build and Push to ACR

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t veenag.azurecr.io/bg-remove-flask:latest --push .
```

**Why Multi-Platform?**:
- Ensures compatibility across different Azure regions
- Supports various Azure App Service plan types
- Future-proofs deployment for ARM-based instances

### Step 3: Verify Image in Registry

```bash
az acr repository list --name veenag --output table
az acr repository show-tags --name veenag --repository bg-remove-flask --output table
```

---

## Azure App Service Deployment

### Method 1: Azure Portal Deployment

#### Step 1: Configure Container Settings
1. Navigate to App Service in Azure Portal
2. Go to **Deployment Center**
3. Select **Container Registry** as source
4. Configure:
   - **Registry**: `veenag`
   - **Image**: `bg-remove-flask`
   - **Tag**: `latest`

#### Step 2: Configure Application Settings
Navigate to **Configuration** → **Application settings** and add:

| Setting Name | Value | Purpose |
|--------------|-------|---------|
| `WEBSITES_ENABLE_APP_SERVICE_STORAGE` | `false` | Uses container's file system |
| `WEBSITES_PORT` | `8000` | Tells Azure which port to use |
| `PORT` | `8000` | Environment variable for gunicorn |
| `SECRET_KEY` | `[secure-random-key]` | Flask security |
| `DEBUG` | `false` | Production mode |

#### Step 3: Enable Managed Identity
1. Go to **Identity** → **System assigned**
2. Turn **Status** to **On**
3. Copy the **Object (principal) ID**

#### Step 4: Grant ACR Access
1. Navigate to Container Registry
2. Go to **Access control (IAM)**
3. Add role assignment:
   - **Role**: `AcrPull`
   - **Assign access to**: `Managed identity`
   - **Select**: Your App Service

### Method 2: Azure CLI Deployment

```bash
# Configure container
az webapp config container set \
  --name veena-bg-remover \
  --resource-group veena-garments \
  --docker-custom-image-name veenag.azurecr.io/bg-remove-flask:latest \
  --docker-registry-server-url https://veenag.azurecr.io

# Enable managed identity
az webapp identity assign \
  --name veena-bg-remover \
  --resource-group veena-garments

# Grant ACR access
az role assignment create \
  --assignee $(az webapp identity show --name veena-bg-remover --resource-group veena-garments --query principalId --output tsv) \
  --scope $(az acr show --name veenag --query id --output tsv) \
  --role "AcrPull"

# Set application settings
az webapp config appsettings set \
  --name veena-bg-remover \
  --resource-group veena-garments \
  --settings \
    WEBSITES_ENABLE_APP_SERVICE_STORAGE=false \
    WEBSITES_PORT=8000 \
    PORT=8000 \
    SECRET_KEY="$(openssl rand -base64 32)" \
    DEBUG=false

# Restart app
az webapp restart \
  --name veena-bg-remover \
  --resource-group veena-garments
```

---

## Troubleshooting Common Issues

### Issue 1: ImagePullFailure

**Symptoms**: Container fails to pull from registry
```
Container pull image failed with reason: ImagePullFailure
```

**Solutions**:
1. **Check image name**: Ensure correct repository name
2. **Verify authentication**: Enable managed identity and grant AcrPull role
3. **Temporary workaround**: Make registry public temporarily

### Issue 2: Port Number Error

**Symptoms**: 
```
Error: '' is not a valid port number
```

**Solution**: Add `PORT=8000` to application settings

### Issue 3: Container Startup Timeout

**Symptoms**: Container takes too long to start

**Solutions**:
1. Increase `--timeout` in gunicorn command
2. Reduce dependencies in requirements.txt
3. Optimize Docker image size

### Issue 4: Memory Issues

**Symptoms**: App restarts frequently, out of memory errors

**Solutions**:
1. Upgrade App Service plan
2. Reduce image processing limits
3. Use `--workers 1` in gunicorn

### Issue 5: File Upload Failures

**Symptoms**: Large file uploads fail

**Solutions**:
1. Check `MAX_CONTENT_LENGTH` setting
2. Verify `WEBSITES_PORT` configuration
3. Increase timeout settings

---

## Security Best Practices

### 1. Environment Variables
- Use Azure Key Vault for sensitive data
- Never commit secrets to source code
- Use strong, randomly generated SECRET_KEY

### 2. Container Registry Security
- Keep registry private
- Use managed identities instead of access keys
- Regularly update base images

### 3. Network Security
- Configure network restrictions if needed
- Use HTTPS only
- Implement rate limiting

### 4. Application Security
- Validate all inputs
- Implement file type restrictions
- Use secure headers

---

## Monitoring and Maintenance

### Application Insights Setup
```bash
az webapp config appsettings set \
  --name veena-bg-remover \
  --resource-group veena-garments \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY="your-key"
```

### Log Monitoring
- Use **Log stream** for real-time logs
- Configure **Application Insights** for metrics
- Set up **Alerts** for failures

### Regular Maintenance
1. **Update dependencies** regularly
2. **Monitor resource usage**
3. **Review security recommendations**
4. **Backup configuration settings**

### Performance Optimization
1. **Monitor response times**
2. **Optimize image processing settings**
3. **Consider CDN for static content**
4. **Scale up/out as needed**

---

## Testing the Deployed Application

### Health Check Endpoints
```bash
# Test health endpoint
curl https://veena-bg-remover.azurewebsites.net/health

# Test main endpoint
curl https://veena-bg-remover.azurewebsites.net/

# Test API info
curl https://veena-bg-remover.azurewebsites.net/api-info
```

### Background Removal Test
```bash
# Upload an image for background removal
curl -X POST https://veena-bg-remover.azurewebsites.net/remove-background \
  -F "image=@test-image.jpg" \
  -o result.png
```

---

## Conclusion

This tutorial covered the complete process of deploying a Flask application to Azure App Service using Docker containers. Key achievements:

1. ✅ **Containerized** the Flask application for Azure
2. ✅ **Built multi-platform** Docker images
3. ✅ **Configured** Azure-specific settings
4. ✅ **Deployed** to Azure App Service
5. ✅ **Secured** with managed identities
6. ✅ **Optimized** for production performance

The application is now running on Azure App Service with proper security, scalability, and monitoring capabilities.

---

## Additional Resources

- [Azure App Service Documentation](https://docs.microsoft.com/en-us/azure/app-service/)
- [Azure Container Registry Documentation](https://docs.microsoft.com/en-us/azure/container-registry/)
- [Docker Multi-platform Documentation](https://docs.docker.com/build/building/multi-platform/)
- [Flask Production Deployment Guide](https://flask.palletsprojects.com/en/2.3.x/deploying/)

---

**Created**: September 18, 2025  
**Last Updated**: September 18, 2025  
**Version**: 1.0  
**Project**: Background Removal Flask API on Azure