#!/bin/bash

# Ensure we're in the right directory
cd /home/site/wwwroot

# Set environment variables
export PORT=${PORT:-8000}
export PYTHONPATH=/home/site/wwwroot:${PYTHONPATH}
export WEBSITE_HOSTNAME=${WEBSITE_HOSTNAME:-localhost:8000}

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Start Gunicorn with our config
exec gunicorn -c gunicorn.conf.py wsgi:app
