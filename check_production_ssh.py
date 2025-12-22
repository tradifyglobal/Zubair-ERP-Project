#!/usr/bin/env python3
import paramiko
import sys

# SSH connection details
hostname = '192.168.20.10'
username = 'zubair'
password = 'erp'

try:
    # Create SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print(f"Connecting to {hostname}...")
    client.connect(hostname, username=username, password=password)
    
    print("\n" + "="*60)
    print("CHECKING GUNICORN STATUS")
    print("="*60)
    stdin, stdout, stderr = client.exec_command('systemctl status gunicorn --no-pager')
    print(stdout.read().decode())
    
    print("\n" + "="*60)
    print("CHECKING LAST 30 LINES OF GUNICORN ERROR LOG")
    print("="*60)
    stdin, stdout, stderr = client.exec_command('echo erp | sudo -S journalctl -u gunicorn -n 30 --no-pager')
    print(stdout.read().decode())
    
    print("\n" + "="*60)
    print("CHECKING DEBUG SETTING")
    print("="*60)
    stdin, stdout, stderr = client.exec_command("grep 'DEBUG =' /var/www/tradifyerp/tradifyerp/settings.py")
    print(stdout.read().decode())
    
    print("\n" + "="*60)
    print("CHECKING TEMPLATE EXTENDS LINE")
    print("="*60)
    stdin, stdout, stderr = client.exec_command('head -1 /var/www/tradifyerp/templates/accounting/trading_manufacturing_account.html')
    print(stdout.read().decode())
    
    print("\n" + "="*60)
    print("CHECKING IF VIEWS_TM EXISTS")
    print("="*60)
    stdin, stdout, stderr = client.exec_command('ls -la /var/www/tradifyerp/accounting/views_tm.py')
    result = stdout.read().decode()
    print(result if result else stderr.read().decode())
    
    print("\n" + "="*60)
    print("CHECKING DJANGO ERROR (if any)")
    print("="*60)
    stdin, stdout, stderr = client.exec_command('echo erp | sudo -S tail -100 /var/log/syslog | grep -i "django\\|gunicorn" | tail -20')
    print(stdout.read().decode())
    
    client.close()
    print("\n" + "="*60)
    print("CONNECTION CLOSED")
    print("="*60)
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
