#!/bin/bash
pkill -9 gunicorn
sleep 2
cd /var/www/tradifyerp/TradifyERP
/var/www/tradifyerp/venv/bin/gunicorn \
  --workers=8 \
  --worker-class=sync \
  --bind=unix:/var/www/tradifyerp/gunicorn.sock \
  --access-logfile=/var/log/tradifyerp/gunicorn_access.log \
  --error-logfile=/var/log/tradifyerp/gunicorn_error.log \
  --log-level=info \
  TradifyERP.wsgi:application > /dev/null 2>&1 &
sleep 5
ps aux | grep gunicorn | grep -v grep | wc -l
