#!/usr/bin/env python3
"""
Deploy views_tm.py to production server
"""
import paramiko
import os

def deploy_file():
    # Server details
    hostname = '192.168.2.69'
    username = 'zubair'
    password = 'erp'
    
    # Local file
    local_file = r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP\accounting\views_tm.py'
    remote_file = '/var/www/tradifyerp/accounting/views_tm.py'
    
    print("=" * 70)
    print("DEPLOYING views_tm.py TO PRODUCTION")
    print("=" * 70)
    
    try:
        # Connect via SSH
        print(f"\n[1/4] Connecting to {hostname}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        print("✓ Connected successfully")
        
        # Upload file
        print(f"\n[2/4] Uploading {os.path.basename(local_file)}...")
        sftp = ssh.open_sftp()
        sftp.put(local_file, remote_file)
        sftp.close()
        print(f"✓ Uploaded to {remote_file}")
        
        # Set permissions
        print("\n[3/4] Setting file permissions...")
        ssh.exec_command(f"chmod 644 {remote_file}")
        ssh.exec_command(f"chown zubair:www-data {remote_file}")
        print("✓ Permissions set")
        
        # Restart Gunicorn
        print("\n[4/4] Restarting Gunicorn...")
        stdin, stdout, stderr = ssh.exec_command("echo 'erp' | sudo -S systemctl restart gunicorn")
        stdout.read()
        print("✓ Gunicorn restarted")
        
        ssh.close()
        
        print("\n" + "=" * 70)
        print("✓ DEPLOYMENT COMPLETE!")
        print("=" * 70)
        print("\nThe Internal Server Error should now be resolved.")
        print("Test the application in your browser.")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False
    
    return True

if __name__ == '__main__':
    deploy_file()
