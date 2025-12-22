#!/usr/bin/env python3
"""
Check trial balance URL pattern in production
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
    
    print("Checking trial balance URL patterns in production...")
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        
        print("\n[1] Checking accounting/urls.py for trial balance patterns:")
        output, error = ssh_command(ssh, "grep -n 'trial.*balance' /var/www/tradifyerp/accounting/urls.py -i")
        print(output)
        
        print("\n[2] Checking exact URL pattern lines:")
        output, error = ssh_command(ssh, "grep -A 2 -B 2 'TrialBalance' /var/www/tradifyerp/accounting/urls.py")
        print(output)
        
        ssh.close()
        
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == '__main__':
    main()
