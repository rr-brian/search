#!/bin/bash

# Enable error handling
set -e

# Debug: Show current directory and list files
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# Find the correct directory
if [ -d "/home/site/wwwroot" ]; then
    cd /home/site/wwwroot
else
    echo "Warning: /home/site/wwwroot not found, staying in current directory"
fi

echo "Working directory: $(pwd)"
echo "Directory contents after cd:"
ls -la

# Set environment variables
export PORT=${PORT:-8000}
export PYTHONPATH=$(pwd):${PYTHONPATH}
export WEBSITE_HOSTNAME=${WEBSITE_HOSTNAME:-localhost:8000}

# Verify requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found in $(pwd)"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

# Verify gunicorn.conf.py exists
if [ ! -f "gunicorn.conf.py" ]; then
    echo "Warning: gunicorn.conf.py not found, creating default configuration"
    cat > gunicorn.conf.py << EOL
bind = "0.0.0.0:${PORT}"
workers = 2
threads = 2
timeout = 300
keepalive = 2
worker_class = "sync"
loglevel = "info"
accesslog = "-"
errorlog = "-"
capture_output = True
enable_stdio_inheritance = True
EOL
fi

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn -c gunicorn.conf.py wsgi:app
