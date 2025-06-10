#!/bin/bash

# Enable error handling and debugging
set -ex

# Debug: Show environment
echo "Python version:"
python --version
echo "Pip version:"
pip --version

# Set environment variables
export PORT=${PORT:-8000}
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Debug: Show current state
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# Navigate to application directory
if [ -d "/home/site/wwwroot" ]; then
    cd /home/site/wwwroot
else
    echo "Warning: /home/site/wwwroot not found, staying in current directory"
fi

echo "Working directory: $(pwd)"
echo "Directory contents after cd:"
ls -la

# Create and activate virtual environment
echo "Setting up virtual environment..."
python -m venv antenv
source antenv/bin/activate

# Upgrade pip and install dependencies
echo "Installing dependencies..."
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Verify gunicorn installation
if ! command -v gunicorn &> /dev/null; then
    echo "Gunicorn not found, installing..."
    pip install gunicorn
fi

# Create gunicorn config if it doesn't exist
if [ ! -f "gunicorn.conf.py" ]; then
    echo "Creating gunicorn configuration..."
    cat > gunicorn.conf.py << EOL
import multiprocessing

bind = "0.0.0.0:${PORT}"
workers = multiprocessing.cpu_count() * 2 + 1
threads = 4
timeout = 600
keepalive = 5
worker_class = "sync"
worker_tmp_dir = "/dev/shm"
loglevel = "info"
accesslog = "-"
errorlog = "-"
capture_output = True
enable_stdio_inheritance = True
EOL
fi

# Start Gunicorn with debugging information
echo "Starting Gunicorn on port ${PORT}..."
exec gunicorn -c gunicorn.conf.py wsgi:app
