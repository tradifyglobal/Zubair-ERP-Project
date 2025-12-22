#!/usr/bin/env python3
"""
Scan production server directory structure
"""
import paramiko

def ssh_command(ssh, command):
    """Execute SSH command and return output"""
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return output, error

def main():
    # Server details
    hostname = '192.168.2.69'
    username = 'zubair'
    password = 'erp'
    
    print("=" * 80)
    print("PRODUCTION SERVER DIRECTORY STRUCTURE SCAN")
    print("=" * 80)
    
    try:
        # Connect
        print(f"\nConnecting to {hostname}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        print("✓ Connected\n")
        
        # Find the main project directory
        print("[1] Locating project root...")
        output, error = ssh_command(ssh, "find /var /home -name 'TradifyERP' -type d 2>/dev/null | head -5")
        print(output)
        
        # Check /var/www structure
        print("\n[2] Checking /var/www structure...")
        output, error = ssh_command(ssh, "ls -la /var/www/")
        print(output)
        
        # Check if tradifyerp exists
        print("\n[3] Checking /var/www/tradifyerp structure...")
        output, error = ssh_command(ssh, "ls -la /var/www/tradifyerp/ 2>/dev/null || echo 'Directory not found'")
        print(output)
        
        # Find manage.py location
        print("\n[4] Finding manage.py location...")
        output, error = ssh_command(ssh, "find /var/www -name 'manage.py' 2>/dev/null")
        print(output if output else "manage.py not found")
        
        # Check accounting app structure
        print("\n[5] Checking accounting app structure...")
        output, error = ssh_command(ssh, "find /var/www -type d -name 'accounting' 2>/dev/null | head -5")
        print(output)
        
        # List accounting directory contents
        print("\n[6] Accounting directory contents...")
        output, error = ssh_command(ssh, "ls -la /var/www/tradifyerp/accounting/ 2>/dev/null || ls -la /var/www/*/accounting/ 2>/dev/null | head -50")
        print(output)
        
        # Check templates structure
        print("\n[7] Checking templates structure...")
        output, error = ssh_command(ssh, "find /var/www -type d -name 'templates' 2>/dev/null | head -10")
        print(output)
        
        # Check accounting templates
        print("\n[8] Checking accounting templates...")
        output, error = ssh_command(ssh, "ls -la /var/www/tradifyerp/templates/accounting/ 2>/dev/null || ls -la /var/www/*/templates/accounting/ 2>/dev/null | head -50")
        if error and 'No such file' in error:
            print("⚠ Accounting templates directory doesn't exist")
        else:
            print(output)
        
        # Check TradifyERP settings location
        print("\n[9] Finding settings.py location...")
        output, error = ssh_command(ssh, "find /var/www -name 'settings.py' -o -name 'settings_production.py' 2>/dev/null")
        print(output)
        
        # Check current user permissions
        print("\n[10] Checking current user and permissions...")
        output, error = ssh_command(ssh, "whoami && groups")
        print(f"Current user: {output}")
        
        # Check project ownership
        print("\n[11] Checking /var/www/tradifyerp ownership...")
        output, error = ssh_command(ssh, "ls -ld /var/www/tradifyerp 2>/dev/null || echo 'Directory not found'")
        print(output)
        
        # Check for static and media directories
        print("\n[12] Checking static/media directories...")
        output, error = ssh_command(ssh, "ls -la /var/www/tradifyerp/ | grep -E 'static|media|templates'")
        print(output)
        
        # Full tree view of accounting app
        print("\n[13] Full accounting app tree (limited to 3 levels)...")
        output, error = ssh_command(ssh, "find /var/www -type d -name 'accounting' -exec sh -c 'echo \"Directory: {}\" && find {} -maxdepth 3 -type f -name \"*.py\" 2>/dev/null' \\; | head -100")
        print(output)
        
        ssh.close()
        
        print("\n" + "=" * 80)
        print("SCAN COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
