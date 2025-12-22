#!/usr/bin/env python3
"""
Verify what's actually deployed on production server
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
    
    print("Checking production sidebar.html...")
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        
        print("\n[1] Checking Trial Balances section in sidebar:")
        output, error = ssh_command(ssh, "grep -A 20 'Trial Balances' /var/www/tradifyerp/templates/partials/sidebar.html | head -30")
        print(output)
        
        print("\n[2] Checking for Trading Manufacturing link:")
        output, error = ssh_command(ssh, "grep -n 'trading_manufacturing' /var/www/tradifyerp/templates/partials/sidebar.html")
        print(output if output else "NOT FOUND!")
        
        ssh.close()
        
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == '__main__':
    main()
