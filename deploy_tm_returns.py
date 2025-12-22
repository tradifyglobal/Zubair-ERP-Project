#!/usr/bin/env python3
"""
Deploy updated Trading & Manufacturing files with Sales/Purchase Returns
"""
import paramiko
import os

def main():
    hostname = '192.168.20.10'
    username = 'zubair'
    password = 'erp'
    
    files_to_deploy = [
        {
            'local': r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP\accounting\trading_manufacturing.py',
            'remote': '/var/www/tradifyerp/accounting/trading_manufacturing.py',
            'name': 'trading_manufacturing.py'
        },
        {
            'local': r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP\templates\accounting\trading_manufacturing_account.html',
            'remote': '/var/www/tradifyerp/templates/accounting/trading_manufacturing_account.html',
            'name': 'trading_manufacturing_account.html'
        }
    ]
    
    print("=" * 80)
    print("DEPLOYING TRADING & MANUFACTURING UPDATES")
    print("Adding Sales Returns and Purchase Returns functionality")
    print("=" * 80)
    
    try:
        print(f"\n[1/3] Connecting to {hostname}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        print("✓ Connected")
        
        sftp = ssh.open_sftp()
        
        for idx, file_info in enumerate(files_to_deploy, 1):
            local_file = file_info['local']
            temp_file = f"/tmp/{file_info['name']}"
            remote_file = file_info['remote']
            
            if not os.path.exists(local_file):
                print(f"\n❌ ERROR: Local file not found: {local_file}")
                continue
            
            print(f"\n[2/{idx+1}] Uploading {file_info['name']}...")
            sftp.put(local_file, temp_file)
            print(f"✓ Uploaded to {temp_file}")
            
            print(f"  Moving to {remote_file}...")
            stdin, stdout, stderr = ssh.exec_command(f"echo 'erp' | sudo -S mv {temp_file} {remote_file}")
            stdout.read()
            
            print(f"  Setting permissions...")
            ssh.exec_command(f"echo 'erp' | sudo -S chmod 644 {remote_file}")
            ssh.exec_command(f"echo 'erp' | sudo -S chown www-data:www-data {remote_file}")
            print(f"✓ {file_info['name']} deployed")
        
        sftp.close()
        
        print(f"\n[3/3] Restarting Gunicorn...")
        stdin, stdout, stderr = ssh.exec_command("echo 'erp' | sudo -S systemctl restart gunicorn")
        stdout.read()
        print("✓ Gunicorn restarted")
        
        ssh.close()
        
        print("\n" + "=" * 80)
        print("✓ DEPLOYMENT COMPLETE!")
        print("=" * 80)
        print("\nUpdates deployed:")
        print("  ✓ Sales Returns calculation and display")
        print("  ✓ Purchase Returns calculation and display")
        print("  ✓ Net Sales = Total Sales - Sales Returns")
        print("  ✓ Net Purchases = Total Purchases - Purchase Returns")
        print("  ✓ Gross Profit calculated from Net Sales")
        print("\nThe Trading & Manufacturing Account now shows:")
        print("  - Total Sales")
        print("  - Less: Sales Returns")
        print("  - = Net Sales")
        print("  - Total Purchases")
        print("  - Less: Purchase Returns")
        print("  - = Net Purchases")
        print("  - Other manufacturing costs")
        print("  - = Gross Profit")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    main()
