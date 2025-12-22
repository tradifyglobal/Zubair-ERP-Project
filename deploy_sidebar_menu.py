#!/usr/bin/env python3
"""
Deploy sidebar.html with Trading & Manufacturing menu in correct position
"""
import paramiko
import os

def main():
    hostname = '192.168.2.69'
    username = 'zubair'
    password = 'erp'
    
    local_file = r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP\templates\partials\sidebar.html'
    temp_file = '/tmp/sidebar.html'
    remote_file = '/var/www/tradifyerp/templates/partials/sidebar.html'
    
    print("=" * 80)
    print("DEPLOYING UPDATED SIDEBAR MENU")
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
        print("\nMenu order updated:")
        print("  1. Trial Balances")
        print("  2. Trading & Manufacturing Account  ← (moved here)")
        print("  3. Profit & Loss Reports")
        print("  4. Balance Sheets")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    main()
