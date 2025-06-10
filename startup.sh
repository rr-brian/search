#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Start Gunicorn
python -m gunicorn --bind=0.0.0.0:8000 --workers=4 --threads=2 --timeout=600 --log-level info --access-logfile - --error-logfile - wsgi:app
