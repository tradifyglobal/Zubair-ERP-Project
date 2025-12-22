#!/usr/bin/env python3
"""
Check horizontal sidebar on production server
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
    
    print("Checking horizontal sidebar on production...")
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        
        print("\n[1] Checking if hori-sidebar.html exists:")
        output, error = ssh_command(ssh, "find /var/www/tradifyerp/templates -name 'hori-sidebar.html' 2>/dev/null")
        print(output if output else "NOT FOUND")
        
        print("\n[2] Checking Financial Reports section in hori-sidebar.html:")
        output, error = ssh_command(ssh, "grep -A 10 'Financial Reports' /var/www/tradifyerp/templates/partials/hori-sidebar.html 2>/dev/null || echo 'File not found'")
        print(output)
        
        ssh.close()
        
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == '__main__':
    main()
