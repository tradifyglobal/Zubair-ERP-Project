#!/bin/bash
# Get last 50 lines of Gunicorn logs
echo "=== GUNICORN LOGS ===" > /tmp/debug_output.txt
sudo journalctl -u gunicorn -n 50 --no-pager >> /tmp/debug_output.txt 2>&1

echo "" >> /tmp/debug_output.txt
echo "=== RECENT ERRORS ===" >> /tmp/debug_output.txt
sudo journalctl -u gunicorn -n 50 --no-pager | grep -i error >> /tmp/debug_output.txt 2>&1

echo "" >> /tmp/debug_output.txt
echo "=== PYTHON TRACEBACK ===" >> /tmp/debug_output.txt
sudo journalctl -u gunicorn -n 100 --no-pager | grep -A 10 "Traceback" >> /tmp/debug_output.txt 2>&1

echo "" >> /tmp/debug_output.txt
echo "=== GUNICORN STATUS ===" >> /tmp/debug_output.txt
sudo systemctl status gunicorn >> /tmp/debug_output.txt 2>&1

echo "Debug output written to /tmp/debug_output.txt"
