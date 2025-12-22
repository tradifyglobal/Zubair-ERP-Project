#!/usr/bin/env python3
"""
Verify all Trading & Manufacturing files on production
"""
import paramiko

def check_files():
    hostname = '192.168.20.10'
    username = 'zubair'
    password = 'erp'
    
    files_to_check = [
        '/var/www/tradifyerp/accounting/views_tm.py',
        '/var/www/tradifyerp/accounting/trading_manufacturing.py',
        '/var/www/tradifyerp/templates/accounting/trading_manufacturing_account.html'
    ]
    
    print("=" * 70)
    print("CHECKING TRADING & MANUFACTURING FILES ON PRODUCTION")
    print("=" * 70)
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        
        missing_files = []
        
        for file_path in files_to_check:
            stdin, stdout, stderr = ssh.exec_command(f"ls -lh {file_path}")
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            
            if error:
                print(f"\n❌ MISSING: {file_path}")
                missing_files.append(file_path)
            else:
                print(f"\n✓ EXISTS: {file_path}")
                print(f"   {output.strip()}")
        
        # Check recent errors
        print("\n" + "=" * 70)
        print("RECENT GUNICORN ERRORS:")
        print("=" * 70)
        stdin, stdout, stderr = ssh.exec_command("journalctl -u gunicorn --since '5 minutes ago' | grep -i error | tail -10")
        errors = stdout.read().decode('utf-8')
        if errors:
            print(errors)
        else:
            print("No recent errors found")
        
        ssh.close()
        
        if missing_files:
            print("\n" + "=" * 70)
            print("⚠️  MISSING FILES FOUND!")
            print("=" * 70)
            for f in missing_files:
                print(f"  - {f}")
            return False
        else:
            print("\n" + "=" * 70)
            print("✓ ALL FILES PRESENT")
            print("=" * 70)
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

if __name__ == '__main__':
    check_files()
