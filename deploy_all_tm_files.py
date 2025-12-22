#!/usr/bin/env python3
"""
Deploy all Trading & Manufacturing files to production
"""
import paramiko
import os

def deploy_all_tm_files():
    hostname = '192.168.2.69'
    username = 'zubair'
    password = 'erp'
    
    # Files to deploy
    files = [
        {
            'local': r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP\accounting\trading_manufacturing.py',
            'remote': '/var/www/tradifyerp/accounting/trading_manufacturing.py'
        },
        {
            'local': r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP\templates\accounting\trading_manufacturing_account.html',
            'remote': '/var/www/tradifyerp/templates/accounting/trading_manufacturing_account.html'
        }
    ]
    
    print("=" * 70)
    print("DEPLOYING ALL TRADING & MANUFACTURING FILES")
    print("=" * 70)
    
    try:
        # Connect
        print(f"\n[1/4] Connecting to {hostname}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        print("✓ Connected successfully")
        
        # Ensure directories exist
        print(f"\n[2/5] Creating directories if needed...")
        ssh.exec_command("mkdir -p /var/www/tradifyerp/templates/accounting")
        ssh.exec_command("echo 'erp' | sudo -S chown -R zubair:www-data /var/www/tradifyerp/templates")
        print("✓ Directories ready")
        
        # Upload files
        print(f"\n[3/5] Uploading files...")
        sftp = ssh.open_sftp()
        
        for file_info in files:
            local_file = file_info['local']
            remote_file = file_info['remote']
            
            if not os.path.exists(local_file):
                print(f"❌ Local file not found: {local_file}")
                continue
                
            print(f"  • Uploading {os.path.basename(local_file)}...")
            sftp.put(local_file, remote_file)
            print(f"    ✓ Uploaded to {remote_file}")
        
        sftp.close()
        
        # Set permissions
        print("\n[3/4] Setting file permissions...")
        for file_info in files:
            remote_file = file_info['remote']
            ssh.exec_command(f"chmod 644 {remote_file}")
            ssh.exec_command(f"chown zubair:www-data {remote_file}")
        print("✓ Permissions set")
        
        # Restart Gunicorn
        print("\n[4/4] Restarting Gunicorn...")
        stdin, stdout, stderr = ssh.exec_command("echo 'erp' | sudo -S systemctl restart gunicorn")
        stdout.read()
        print("✓ Gunicorn restarted")
        
        # Verify deployment
        print("\n" + "=" * 70)
        print("VERIFYING DEPLOYMENT")
        print("=" * 70)
        
        for file_info in files:
            remote_file = file_info['remote']
            stdin, stdout, stderr = ssh.exec_command(f"ls -lh {remote_file}")
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            
            if error:
                print(f"❌ {remote_file} - NOT FOUND")
            else:
                print(f"✓ {output.strip()}")
        
        ssh.close()
        
        print("\n" + "=" * 70)
        print("✓ COMPLETE DEPLOYMENT FINISHED!")
        print("=" * 70)
        print("\nAll Trading & Manufacturing files are now deployed.")
        print("Test the application in your browser.")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    deploy_all_tm_files()
