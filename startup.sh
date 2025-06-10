#!/bin/bash

# Make startup script executable
chmod +x startup.sh

# Add current directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Set environment variables for better performance
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
export WEB_CONCURRENCY=2

# Start Gunicorn with increased timeout and worker class
exec gunicorn \
    --bind=0.0.0.0:${PORT:-8000} \
    --timeout 300 \
    --worker-class sync \
    --workers ${WEB_CONCURRENCY:-2} \
    --threads 2 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance \
    rt_search_flask:app
