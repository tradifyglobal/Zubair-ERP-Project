#!/usr/bin/env python3
"""
Interactive script to configure PostgreSQL firewall access
Provides step-by-step instructions for manual configuration
"""

import subprocess
import sys

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def main():
    print_header("PostgreSQL Firewall Configuration Guide")
    
    print("""
This script will help you configure firewall access to PostgreSQL.

Since the zubair user doesn't have passwordless sudo, you'll need to 
manually run a couple of commands on the DB server.

STEPS:
1. Open a new terminal/PowerShell
2. Connect to DB server: ssh zubair@192.168.20.11
3. When prompted, enter the server password
4. Run the commands shown below
5. Return here and continue

""")
    
    print_header("Step 1: SSH into Database Server")
    print("""
Command to run on your local machine:
    ssh zubair@192.168.20.11

Password: (enter the DB server password when prompted)
""")
    
    response = input("Have you connected to the DB server via SSH? (y/n): ")
    if response.lower() != 'y':
        print("Please connect first, then run this script again.")
        return False
    
    print_header("Step 2: Set Up Passwordless Sudo")
    print("""
Run these commands on the DB server (you may be prompted for password once):

    echo 'zubair ALL=(ALL) NOPASSWD: /usr/sbin/ufw' | sudo tee /etc/sudoers.d/zubair-nopass
    sudo chmod 0440 /etc/sudoers.d/zubair-nopass
    sudo visudo -c

""")
    
    response = input("Have you run the passwordless sudo setup commands? (y/n): ")
    if response.lower() != 'y':
        print("Please run the commands above first.")
        return False
    
    print_header("Step 3: Add Firewall Rule")
    print("""
Now run this command on the DB server:

    sudo ufw allow from 192.168.20.10/32 to any port 5432 proto tcp

Then verify it was added:

    sudo ufw status | grep 5432

The output should show:
    5432/tcp            ALLOW       192.168.20.10

""")
    
    response = input("Have you added the firewall rule? (y/n): ")
    if response.lower() != 'y':
        print("Please run the UFW commands above.")
        return False
    
    print_header("Step 4: Test Database Connection")
    print("""
Now testing database connectivity from the app server...
""")
    
    # Test connection
    result = subprocess.run(
        'ssh zubair@192.168.20.10 "cd /var/www/tradifyerp && ./venv/bin/python /tmp/test_db_connection.py"',
        shell=True,
        capture_output=True,
        text=True
    )
    
    if "successfully" in result.stdout:
        print("✅ " + result.stdout.strip())
        return True
    else:
        print("❌ " + result.stderr.strip())
        print("\nIf the rule was added correctly, the connection should work.")
        print("You may need to wait a moment for the firewall rule to take effect.")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print_header("Configuration Complete!")
        print("""
✅ Firewall is now properly configured!

You can now:
1. Run Django migrations
2. Apply pending migrations to the database
3. Continue with the deployment process

To run the migration now, use:
    ssh zubair@192.168.20.10 "cd /var/www/tradifyerp && ./venv/bin/python manage.py migrate accounting --settings=TradifyERP.settings_production"
""")
    else:
        print_header("Configuration Incomplete")
        print("""
⚠️  Please complete the steps above and try again.

If you're still having issues, verify:
1. UFW rule was added correctly: sudo ufw status
2. PostgreSQL is listening: sudo ss -tlnp | grep 5432
3. No other firewall is blocking traffic
""")
        sys.exit(1)
