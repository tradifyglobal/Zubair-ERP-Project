#!/usr/bin/env python3
"""
Check what base template exists in production
"""
import paramiko

def ssh_command(ssh, command):
    """Execute SSH command and return output"""
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return output, error

def main():
    hostname = '192.168.20.10'
    username = 'zubair'
    password = 'erp'
    
    print("Checking for base templates in production...")
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        
        # Check for layouts directory
        print("\n[1] Looking for layouts directory:")
        output, error = ssh_command(ssh, "find /var/www/tradifyerp/templates -name 'layouts' -type d 2>/dev/null")
        print(output if output else "No layouts directory found")
        
        # Check for base.html files
        print("\n[2] Looking for base.html files:")
        output, error = ssh_command(ssh, "find /var/www/tradifyerp/templates -name 'base.html' 2>/dev/null")
        print(output if output else "No base.html found")
        
        # List templates directory structure
        print("\n[3] Templates directory structure:")
        output, error = ssh_command(ssh, "ls -la /var/www/tradifyerp/templates/")
        print(output)
        
        # Check minia templates
        print("\n[4] Checking minia app templates:")
        output, error = ssh_command(ssh, "find /var/www/tradifyerp/minia/templates -name 'base.html' 2>/dev/null || echo 'Not found'")
        print(output)
        
        # Check what other accounting templates use
        print("\n[5] Checking what other accounting templates extend:")
        output, error = ssh_command(ssh, "grep -h 'extends' /var/www/tradifyerp/templates/accounting/*.html | head -5")
        print(output)
        
        ssh.close()
        
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == '__main__':
    main()
