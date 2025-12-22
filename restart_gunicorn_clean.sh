#!/bin/bash
cd /var/www/tradifyerp/TradifyERP

# Kill all gunicorn processes
echo "Killing Gunicorn processes..."
pkill -9 gunicorn
sleep 2

# Clear cache
echo "Clearing Python cache..."
find . -type d -name __pycache__ -delete 2>/dev/null
find . -name '*.pyc' -delete 2>/dev/null

# Start Gunicorn
echo "Starting Gunicorn with 8 workers..."
/var/www/tradifyerp/venv/bin/python -m gunicorn \
    --workers 8 \
    --bind unix:/var/www/tradifyerp/gunicorn.sock \
    --access-logfile /var/log/gunicorn_access.log \
    --error-logfile /var/log/gunicorn_error.log \
    TradifyERP.wsgi:application &

sleep 3

# Verify
WORKER_COUNT=$(pgrep -f 'gunicorn.*TradifyERP' | wc -l)
echo "Gunicorn is running with $WORKER_COUNT processes"
