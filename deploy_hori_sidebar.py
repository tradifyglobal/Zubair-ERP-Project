#!/usr/bin/env python3
"""
Deploy hori-sidebar.html with Trading & Manufacturing menu item
"""
import paramiko
import os

def main():
    hostname = '192.168.20.10'
    username = 'zubair'
    password = 'erp'
    
    local_file = r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP\templates\partials\hori-sidebar.html'
    temp_file = '/tmp/hori-sidebar.html'
    remote_file = '/var/www/tradifyerp/templates/partials/hori-sidebar.html'
    
    print("=" * 80)
    print("DEPLOYING HORIZONTAL NAVIGATION BAR")
    print("=" * 80)
    
    if not os.path.exists(local_file):
        print(f"\n❌ ERROR: Local file not found: {local_file}")
        return False
    
    try:
        print(f"\n[1/5] Connecting to {hostname}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        print("✓ Connected")
        
        print(f"\n[2/5] Uploading to temp location...")
        sftp = ssh.open_sftp()
        sftp.put(local_file, temp_file)
        sftp.close()
        print(f"✓ Uploaded to {temp_file}")
        
        print(f"\n[3/5] Moving to final location...")
        stdin, stdout, stderr = ssh.exec_command(f"echo 'erp' | sudo -S mv {temp_file} {remote_file}")
        stdout.read()
        print(f"✓ Moved to {remote_file}")
        
        print("\n[4/5] Setting permissions...")
        ssh.exec_command(f"echo 'erp' | sudo -S chmod 644 {remote_file}")
        ssh.exec_command(f"echo 'erp' | sudo -S chown www-data:www-data {remote_file}")
        print("✓ Permissions set")
        
        print("\n[5/5] Restarting Gunicorn...")
        stdin, stdout, stderr = ssh.exec_command("echo 'erp' | sudo -S systemctl restart gunicorn")
        stdout.read()
        print("✓ Gunicorn restarted")
        
        ssh.close()
        
        print("\n" + "=" * 80)
        print("✓ DEPLOYMENT COMPLETE!")
        print("=" * 80)
        print("\nHorizontal top navigation bar updated:")
        print("  Accounting > Financial Reports:")
        print("    - General Ledger Dashboard")
        print("    - Capital & Cash Position")
        print("    - Accounts")
        print("    - Ledger Entries")
        print("    - Trial Balances")
        print("    - Trading & Manufacturing Account  ← (now visible)")
        print("    - Profit & Loss Reports")
        print("    - Balance Sheets")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    main()
