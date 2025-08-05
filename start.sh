#!/bin/bash

echo "Starting Background Removal API..."
echo "Python version: $(python --version)"
echo "PORT: ${PORT:-8000}"
echo "Working directory: $(pwd)"
echo "Files in current directory:"
ls -la

echo "Testing basic imports..."
python -c "
import sys
print('Python path:', sys.path)
try:
    from config import Config
    print('✅ Config imported')
    import flask
    print('✅ Flask imported')
    from rembg import remove
    print('✅ rembg imported')
    print('✅ All critical imports successful')
except Exception as e:
    print('❌ Import failed:', e)
    sys.exit(1)
"

echo "Starting gunicorn..."
exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 120 --max-requests 100 --log-level info --access-logfile - --error-logfile - api.app:application