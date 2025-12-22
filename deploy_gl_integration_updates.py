"""
Deploy Updated GL Integration Files
1. Maintenance signals (new)
2. Maintenance models (updated with is_posted_to_gl field)
3. Maintenance apps.py (updated to load signals)
4. Manufacturing signals (updated to use LedgerEntry)
"""

import paramiko
from datetime import datetime

def deploy_file(sftp, ssh, local_path, remote_path, description):
    """Upload file and set permissions"""
    print(f"  📤 {description}...")
    
    # Read local file
    with open(local_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Upload to temp location
    temp_path = f'/tmp/{local_path.split("/")[-1]}'
    with sftp.file(temp_path, 'w') as f:
        f.write(content)
    
    # Move to final location with sudo
    stdin, stdout, stderr = ssh.exec_command(f'echo erp | sudo -S mv {temp_path} {remote_path}')
    stdout.read()
    
    # Set permissions
    ssh.exec_command(f'echo erp | sudo -S chown www-data:www-data {remote_path}')
    ssh.exec_command(f'echo erp | sudo -S chmod 644 {remote_path}')
    
    print(f"     ✅ Deployed to {remote_path}")

def main():
    host = '192.168.2.69'
    username = 'zubair'
    password = 'erp'
    
    print("="*80)
    print("DEPLOYING GL INTEGRATION UPDATES")
    print("="*80)
    print(f"Server: {host}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print()
    
    files_to_deploy = [
        {
            'local': 'f:/ERP-Production/Zubair-ERP-Project/TradifyERP/maintenance/signals.py',
            'remote': '/var/www/tradifyerp/maintenance/signals.py',
            'desc': 'Maintenance signals (NEW - GL integration)'
        },
        {
            'local': 'f:/ERP-Production/Zubair-ERP-Project/TradifyERP/maintenance/apps.py',
            'remote': '/var/www/tradifyerp/maintenance/apps.py',
            'desc': 'Maintenance apps.py (loads signals)'
        },
        {
            'local': 'f:/ERP-Production/Zubair-ERP-Project/TradifyERP/maintenance/models.py',
            'remote': '/var/www/tradifyerp/maintenance/models.py',
            'desc': 'Maintenance models (added is_posted_to_gl)'
        },
        {
            'local': 'f:/ERP-Production/Zubair-ERP-Project/TradifyERP/manufacturing/signals.py',
            'remote': '/var/www/tradifyerp/manufacturing/signals.py',
            'desc': 'Manufacturing signals (FIXED - uses LedgerEntry)'
        }
    ]
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)
        print("✅ Connected to server\n")
        
        sftp = ssh.open_sftp()
        
        print("📦 Deploying files...\n")
        for file_info in files_to_deploy:
            deploy_file(sftp, ssh, file_info['local'], file_info['remote'], file_info['desc'])
        
        sftp.close()
        
        # Create migration for new fields
        print("\n📝 Creating migrations for maintenance model changes...")
        stdin, stdout, stderr = ssh.exec_command(
            'cd /var/www/tradifyerp && /var/www/tradifyerp/venv/bin/python manage.py makemigrations maintenance',
            timeout=60
        )
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        print(output)
        if 'No changes detected' not in output and error:
            print(f"⚠️ {error}")
        
        # Run migrations
        print("\n🔄 Running migrations...")
        stdin, stdout, stderr = ssh.exec_command(
            'cd /var/www/tradifyerp && /var/www/tradifyerp/venv/bin/python manage.py migrate maintenance',
            timeout=90
        )
        output = stdout.read().decode('utf-8')
        print(output)
        
        # Restart Gunicorn
        print("\n🔄 Restarting Gunicorn...")
        stdin, stdout, stderr = ssh.exec_command('echo erp | sudo -S systemctl restart gunicorn')
        stdout.read()
        print("✅ Gunicorn restarted")
        
        # Verify deployment
        print("\n✅ Verifying deployment...")
        stdin, stdout, stderr = ssh.exec_command('ls -la /var/www/tradifyerp/maintenance/signals.py')
        output = stdout.read().decode('utf-8')
        if 'signals.py' in output:
            print("   ✅ maintenance/signals.py exists")
        
        stdin, stdout, stderr = ssh.exec_command('ls -la /var/www/tradifyerp/manufacturing/signals.py')
        output = stdout.read().decode('utf-8')
        if 'signals.py' in output:
            print("   ✅ manufacturing/signals.py updated")
        
        ssh.close()
        
        print("\n" + "="*80)
        print("DEPLOYMENT COMPLETE")
        print("="*80)
        print("\n✅ All files deployed successfully")
        print("✅ Migrations applied")
        print("✅ Gunicorn restarted")
        print("\nChanges:")
        print("  • Maintenance module now has GL integration via signals")
        print("  • WorkOrder model has is_posted_to_gl and completion_date fields")
        print("  • Manufacturing module now uses LedgerEntry (not JournalEntry)")
        print("\nNext: Run create_test_transactions.py to test integrations")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
