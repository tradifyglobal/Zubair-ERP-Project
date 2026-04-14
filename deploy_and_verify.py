#!/usr/bin/env python3
import subprocess
import sys

source_file = r'c:\git-app-repo\Zubair-ERP-Project\TradifyERP\accounting\cash_forms.py'
dest_file = 'root@192.168.20.10:/var/www/tradifyerp/accounting/cash_forms.py'

# Copy file
result = subprocess.run(['scp', source_file, dest_file], capture_output=True, text=True)
print(f"SCP Result: {result.returncode}")
print(f"Stdout: {result.stdout}")
print(f"Stderr: {result.stderr}")

# Now restart gunicorn
result2 = subprocess.run([
    'ssh', 'root@192.168.20.10',
    'systemctl restart gunicorn && sleep 3 && echo Gunicorn restarted'
], capture_output=True, text=True)

print(f"\nGunicorn Restart: {result2.returncode}")
print(f"Stdout: {result2.stdout}")
print(f"Stderr: {result2.stderr}")

# Verify the file
result3 = subprocess.run([
    'ssh', 'root@192.168.20.10',
    "grep -m 1 \"label='Debit Account'\" /var/www/tradifyerp/accounting/cash_forms.py"
], capture_output=True, text=True)

print(f"\nVerify Label Change: {result3.returncode}")
print(f"Output: {result3.stdout}")
if result3.returncode != 0:
    print(f"Error: {result3.stderr}")
