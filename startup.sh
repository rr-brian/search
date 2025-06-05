#!/bin/bash

# Make startup script executable
chmod +x startup.sh

# Start Gunicorn
exec gunicorn --bind=0.0.0.0:8000 rt_search_flask:app
