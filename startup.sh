#!/bin/bash

# Make startup script executable
chmod +x startup.sh

# Add current directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start Gunicorn with increased timeout and worker class
exec gunicorn \
    --bind=0.0.0.0:8000 \
    --timeout 120 \
    --worker-class sync \
    --workers 2 \
    --log-level debug \
    rt_search_flask:app
