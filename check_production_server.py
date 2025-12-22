#!/usr/bin/env python3
"""
Direct SSH check of production server status
"""
import paramiko
import sys

def ssh_command(ssh, command):
    """Execute SSH command and return output"""
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return output, error

def main():
    # Production server details
    hostname = '192.168.2.69'
    username = 'zubair'
    password = 'erp'
    
    print("=" * 70)
    print("PRODUCTION SERVER STATUS CHECK")
    print("=" * 70)
    
    try:
        # Connect to server
        print(f"\n[1/8] Connecting to {hostname}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        print("✓ Connected successfully")
        
        # Check Gunicorn status
        print("\n[2/8] Checking Gunicorn status...")
        output, error = ssh_command(ssh, "systemctl status gunicorn | head -20")
        print(output)
        
        # Check DEBUG setting
        print("\n[3/8] Checking DEBUG mode...")
        output, error = ssh_command(ssh, "grep 'DEBUG = ' /var/www/tradifyerp/tradifyerp/settings.py")
        print(f"DEBUG setting: {output.strip()}")
        
        # Check if views_tm.py exists
        print("\n[4/8] Checking Trading Manufacturing files...")
        output, error = ssh_command(ssh, "ls -lh /var/www/tradifyerp/accounting/views_tm.py")
        if error:
            print(f"ERROR: {error}")
        else:
            print(f"views_tm.py: {output.strip()}")
            
        output, error = ssh_command(ssh, "ls -lh /var/www/tradifyerp/templates/accounting/trading_manufacturing_account.html")
        if error:
            print(f"ERROR: {error}")
        else:
            print(f"template: {output.strip()}")
        
        # Check template extends line
        print("\n[5/8] Checking template base extends...")
        output, error = ssh_command(ssh, "head -1 /var/www/tradifyerp/templates/accounting/trading_manufacturing_account.html")
        print(f"First line: {output.strip()}")
        
        # Check URL pattern
        print("\n[6/8] Checking URL pattern...")
        output, error = ssh_command(ssh, "grep -n 'trading-manufacturing' /var/www/tradifyerp/accounting/urls.py")
        if output:
            print(f"URL found:\n{output}")
        else:
            print("URL pattern NOT found!")
        
        # Get recent Gunicorn errors
        print("\n[7/8] Fetching recent Gunicorn errors...")
        output, error = ssh_command(ssh, "sudo journalctl -u gunicorn -n 100 --no-pager | grep -i 'error\\|exception\\|traceback' | tail -20")
        if output:
            print("Recent errors:")
            print(output)
        else:
            print("No recent errors in journalctl")
        
        # Check Django error log if DEBUG is on
        print("\n[8/8] Trying to get Django traceback...")
        output, error = ssh_command(ssh, "sudo tail -100 /var/log/gunicorn/error.log 2>/dev/null | tail -30")
        if output:
            print("Error log:")
            print(output)
        else:
            print("No error log at /var/log/gunicorn/error.log")
        
        # Save full output to file
        print("\n" + "=" * 70)
        print("SAVING DETAILED OUTPUT TO production_check.txt")
        print("=" * 70)
        
        with open('production_check.txt', 'w') as f:
            f.write("PRODUCTION SERVER CHECK\n")
            f.write("=" * 70 + "\n\n")
            
            f.write("1. GUNICORN STATUS:\n")
            output, _ = ssh_command(ssh, "systemctl status gunicorn")
            f.write(output + "\n\n")
            
            f.write("2. DEBUG SETTING:\n")
            output, _ = ssh_command(ssh, "grep 'DEBUG' /var/www/tradifyerp/tradifyerp/settings.py")
            f.write(output + "\n\n")
            
            f.write("3. TEMPLATE FIRST LINE:\n")
            output, _ = ssh_command(ssh, "head -1 /var/www/tradifyerp/templates/accounting/trading_manufacturing_account.html")
            f.write(output + "\n\n")
            
            f.write("4. URL PATTERN:\n")
            output, _ = ssh_command(ssh, "grep 'trading-manufacturing' /var/www/tradifyerp/accounting/urls.py")
            f.write(output + "\n\n")
            
            f.write("5. RECENT GUNICORN LOG (last 200 lines):\n")
            output, _ = ssh_command(ssh, "sudo journalctl -u gunicorn -n 200 --no-pager")
            f.write(output + "\n\n")
            
            f.write("6. VIEWS_TM.PY CONTENT:\n")
            output, _ = ssh_command(ssh, "cat /var/www/tradifyerp/accounting/views_tm.py")
            f.write(output + "\n\n")
            
        print("✓ Detailed output saved to production_check.txt")
        
        ssh.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
