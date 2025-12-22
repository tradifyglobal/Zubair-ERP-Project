#!/usr/bin/env python3
"""
Check and display hori-sidebar.html Financial Reports section
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
    
    print("Checking hori-sidebar.html Financial Reports section...")
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        
        print("\n[Displaying Financial Reports section:]")
        output, error = ssh_command(ssh, "grep -n -A 8 'Financial Reports' /var/www/tradifyerp/templates/partials/hori-sidebar.html | head -15")
        print(output)
        
        ssh.close()
        
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == '__main__':
    main()
