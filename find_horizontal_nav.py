#!/usr/bin/env python3
"""
Find the horizontal navigation bar template on production
"""
import paramiko

def ssh_command(ssh, command):
    """Execute SSH command and return output"""
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return output, error

def main():
    hostname = '192.168.2.69'
    username = 'zubair'
    password = 'erp'
    
    print("Finding horizontal top navigation template on production...")
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        
        print("\n[1] Finding all templates with 'Accounting' dropdown:")
        output, error = ssh_command(ssh, "grep -r 'Accounting' /var/www/tradifyerp/templates/partials/*.html | grep -i 'dropdown\\|nav'")
        print(output)
        
        print("\n[2] Checking base.html for layout includes:")
        output, error = ssh_command(ssh, "grep -i 'include\\|topnav\\|horizontal' /var/www/tradifyerp/templates/partials/base.html | head -20")
        print(output)
        
        print("\n[3] List all partial templates:")
        output, error = ssh_command(ssh, "ls -la /var/www/tradifyerp/templates/partials/")
        print(output)
        
        ssh.close()
        
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == '__main__':
    main()
