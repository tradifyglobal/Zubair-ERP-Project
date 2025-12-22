#!/usr/bin/env python3
"""
Verify the deployed template on production
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
    
    print("Verifying deployed template on production...")
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        
        print("\n[1] Checking for 'Sales Returns' in template:")
        output, error = ssh_command(ssh, "grep -n 'Sales Returns' /var/www/tradifyerp/templates/accounting/trading_manufacturing_account.html")
        print(output if output else "NOT FOUND")
        
        print("\n[2] Checking for 'Purchase Returns' in template:")
        output, error = ssh_command(ssh, "grep -n 'Purchase Returns' /var/www/tradifyerp/templates/accounting/trading_manufacturing_account.html")
        print(output if output else "NOT FOUND")
        
        print("\n[3] Checking for 'Net Sales' in template:")
        output, error = ssh_command(ssh, "grep -n 'Net Sales' /var/www/tradifyerp/templates/accounting/trading_manufacturing_account.html")
        print(output if output else "NOT FOUND")
        
        print("\n[4] Checking for 'Net Purchases' in template:")
        output, error = ssh_command(ssh, "grep -n 'Net Purchases' /var/www/tradifyerp/templates/accounting/trading_manufacturing_account.html")
        print(output if output else "NOT FOUND")
        
        print("\n[5] Checking last modification time:")
        output, error = ssh_command(ssh, "ls -lh /var/www/tradifyerp/templates/accounting/trading_manufacturing_account.html")
        print(output)
        
        print("\n[6] Checking sales revenue section (lines 115-125):")
        output, error = ssh_command(ssh, "sed -n '115,135p' /var/www/tradifyerp/templates/accounting/trading_manufacturing_account.html")
        print(output)
        
        ssh.close()
        
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == '__main__':
    main()
