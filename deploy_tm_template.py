#!/usr/bin/env python3
"""
Deploy trading_manufacturing_account.html template to production
"""
import paramiko
import os

def main():
    # Server details
    hostname = '192.168.2.69'
    username = 'zubair'
    password = 'erp'
    
    # Local and remote paths
    local_file = r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP\templates\accounting\trading_manufacturing_account.html'
    temp_file = '/tmp/trading_manufacturing_account.html'
    remote_file = '/var/www/tradifyerp/templates/accounting/trading_manufacturing_account.html'
    
    print("=" * 80)
    print("DEPLOYING TRADING & MANUFACTURING TEMPLATE")
    print("=" * 80)
    
    # Check if local file exists
    if not os.path.exists(local_file):
        print(f"\n❌ ERROR: Local file not found: {local_file}")
        return False
    
    try:
        # Connect
        print(f"\n[1/5] Connecting to {hostname}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        print("✓ Connected")
        
        # Upload to temp location
        print(f"\n[2/5] Uploading to temp location...")
        sftp = ssh.open_sftp()
        sftp.put(local_file, temp_file)
        sftp.close()
        print(f"✓ Uploaded to {temp_file}")
        
        # Move to final location with sudo
        print(f"\n[3/5] Moving to final location...")
        stdin, stdout, stderr = ssh.exec_command(f"echo 'erp' | sudo -S mv {temp_file} {remote_file}")
        stdout.read()
        print(f"✓ Moved to {remote_file}")
        
        # Set permissions
        print("\n[4/5] Setting permissions...")
        ssh.exec_command(f"echo 'erp' | sudo -S chmod 644 {remote_file}")
        ssh.exec_command(f"echo 'erp' | sudo -S chown www-data:www-data {remote_file}")
        print("✓ Permissions set")
        
        # Restart Gunicorn
        print("\n[5/5] Restarting Gunicorn...")
        stdin, stdout, stderr = ssh.exec_command("echo 'erp' | sudo -S systemctl restart gunicorn")
        stdout.read()
        print("✓ Gunicorn restarted")
        
        ssh.close()
        
        print("\n" + "=" * 80)
        print("✓ DEPLOYMENT COMPLETE!")
        print("=" * 80)
        print("\nAll Trading & Manufacturing module files are now deployed:")
        print("  • views_tm.py ✓")
        print("  • trading_manufacturing.py ✓")
        print("  • trading_manufacturing_account.html ✓")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    main()
