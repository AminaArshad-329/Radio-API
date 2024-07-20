#!/bin/bash

sleep 10

# Apply database migrations
python3 manage.py migrate

# Start Gunicorn server
gunicorn analytics_api.wsgi --bind 0.0.0.0:8001 --timeout 120 --workers 4
