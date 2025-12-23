#!/bin/bash
# Diagnostic script for 502 Bad Gateway error

echo "=== Gunicorn Status ==="
systemctl status gunicorn --no-pager

echo ""
echo "=== Gunicorn Logs (last 30 lines) ==="
tail -30 /var/log/gunicorn/error.log 2>/dev/null || echo "Logs not found"

echo ""
echo "=== Nginx Error Log (last 20 lines) ==="
sudo tail -20 /var/log/nginx/error.log 2>/dev/null || echo "Logs not found"

echo ""
echo "=== Testing Database Connectivity ==="
cd /var/www/tradifyerp
source venv/bin/activate
timeout 10 python manage.py check --deploy 2>&1 || echo "Check failed"

echo ""
echo "=== Django Shell Test ==="
python manage.py shell <<EOF
import psycopg2
try:
    conn = psycopg2.connect("dbname=tradifyerp_db user=tradifyerp_user host=192.168.20.11 port=5432 password=tradifypass")
    print("✓ Database connection successful!")
    conn.close()
except Exception as e:
    print(f"✗ Database connection failed: {e}")
EOF

echo ""
echo "=== Restarting Gunicorn ==="
sudo systemctl restart gunicorn
sleep 3
systemctl status gunicorn --no-pager | head -10

echo ""
echo "=== Done ==="
