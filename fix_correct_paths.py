#!/usr/bin/env python3
"""Fix deployment to correct production paths"""
import subprocess
import sys

def run_ssh(command):
    """Run SSH command and return output"""
    try:
        result = subprocess.run(
            ['ssh', 'zubair@192.168.20.10', command],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"ERROR: {e}"

def run_scp(local, remote):
    """Run SCP command"""
    try:
        result = subprocess.run(
            ['scp', local, f'zubair@192.168.20.10:{remote}'],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except Exception as e:
        print(f"SCP ERROR: {e}")
        return False

print("=" * 60)
print("CHECKING PRODUCTION SERVER STRUCTURE")
print("=" * 60)

# Check the correct structure
print("\n1. Checking directory structure...")
output = run_ssh("ls -la /var/www/tradifyerp/")
print(output)

print("\n2. Checking TradifyERP directory...")
output = run_ssh("ls -la /var/www/tradifyerp/TradifyERP/")
print(output)

print("\n3. Checking accounting app location...")
output = run_ssh("ls -la /var/www/tradifyerp/TradifyERP/accounting/ 2>&1 | head -20")
print(output)

print("\n4. Checking templates location...")
output = run_ssh("ls -la /var/www/tradifyerp/TradifyERP/templates/accounting/ 2>&1 | head -20")
print(output)

print("\n5. Checking current Gunicorn status...")
output = run_ssh("systemctl status gunicorn | head -15")
print(output)

print("\n6. Checking DEBUG setting...")
output = run_ssh("grep 'DEBUG =' /var/www/tradifyerp/TradifyERP/tradifyerp/settings.py")
print(output)

print("\n" + "=" * 60)
print("DEPLOYING TO CORRECT PATHS")
print("=" * 60)

# Deploy to correct locations
files_to_deploy = [
    ('TradifyERP/accounting/trading_manufacturing.py', '/var/www/tradifyerp/TradifyERP/accounting/'),
    ('TradifyERP/accounting/views_tm.py', '/var/www/tradifyerp/TradifyERP/accounting/'),
    ('TradifyERP/accounting/urls.py', '/var/www/tradifyerp/TradifyERP/accounting/'),
    ('trading_manufacturing_minimal.html', '/var/www/tradifyerp/TradifyERP/templates/accounting/trading_manufacturing_account.html'),
]

for local, remote in files_to_deploy:
    print(f"\nUploading {local} to {remote}")
    if run_scp(local, remote):
        print(f"  ✓ Success")
    else:
        print(f"  ✗ Failed")

# Disable DEBUG and restart
print("\n7. Disabling DEBUG mode...")
output = run_ssh("echo erp | sudo -S sed -i 's/DEBUG = True/DEBUG = False/' /var/www/tradifyerp/TradifyERP/tradifyerp/settings.py")
print(output)

print("\n8. Restarting Gunicorn...")
output = run_ssh("echo erp | sudo -S systemctl restart gunicorn")
print(output)

print("\n9. Checking Gunicorn status after restart...")
output = run_ssh("systemctl status gunicorn | head -10")
print(output)

print("\n" + "=" * 60)
print("DEPLOYMENT COMPLETE - CHECK https://tradifyglobal.com/")
print("=" * 60)
