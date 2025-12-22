#!/bin/bash
# Trigger the error and capture it
echo "Accessing the URL to trigger error..."
curl -s https://tradifyglobal.com/accounting/trading-manufacturing/ > /dev/null

echo "Getting last 30 lines with errors..."
sudo journalctl -u gunicorn -n 100 --no-pager | grep -A 15 "Exception\|Error\|Traceback" | tail -50 > /tmp/error_details.txt

cat /tmp/error_details.txt
