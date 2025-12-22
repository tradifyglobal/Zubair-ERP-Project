#!/usr/bin/env python3
"""
Configure UFW firewall on DB server to allow PostgreSQL connections from app server
"""

import subprocess
import sys

DB_SERVER = "192.168.2.59"
APP_SERVER = "192.168.2.69"
SSH_USER = "zubair"

def run_remote_command(host, cmd):
    """Run a command on remote server via SSH"""
    full_cmd = f'ssh {SSH_USER}@{host} "{cmd}"'
    print(f"Running: {cmd}")
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def main():
    print("=" * 70)
    print("PostgreSQL UFW Firewall Configuration")
    print("=" * 70)
    print(f"\nDB Server: {DB_SERVER}")
    print(f"App Server: {APP_SERVER}")
    
    # Try to add UFW rule allowing PostgreSQL from app server
    commands = [
        # First check if UFW is enabled
        ("systemctl status ufw --no-pager | head -3", "Check UFW status"),
        # Allow PostgreSQL from app server
        ("sudo -n ufw allow from {}/32 to any port 5432 proto tcp".format(APP_SERVER), "Allow PostgreSQL from app server"),
        # Verify the rule was added
        ("sudo -n ufw status | grep 5432", "Verify UFW rule added"),
    ]
    
    for cmd, description in commands:
        print(f"\n▶ {description}")
        print(f"  Command: {cmd}")
        code, stdout, stderr = run_remote_command(DB_SERVER, cmd)
        
        if stdout:
            print(f"  Output: {stdout.strip()}")
        if stderr and code != 0:
            print(f"  Error: {stderr.strip()}")
            if "sudo:" in stderr.lower() and "password" in stderr.lower():
                print(f"  ⚠️  Passwordless sudo not available on {DB_SERVER}")
                print(f"      You need to run this command manually on the DB server:")
                print(f"      sudo ufw allow from {APP_SERVER}/32 to any port 5432 proto tcp")
                return False
        elif code == 0:
            print(f"  ✅ Success")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n" + "=" * 70)
        print("⚠️  MANUAL FIREWALL CONFIGURATION REQUIRED")
        print("=" * 70)
        print("\nTo fix this, log in to the DB server and run:")
        print(f"  ssh {SSH_USER}@192.168.2.59")
        print(f"  sudo ufw allow from 192.168.2.69/32 to any port 5432 proto tcp")
        print(f"  sudo ufw status")
        print("\nThen try the migration again.")
        sys.exit(1)
    else:
        print("\n" + "=" * 70)
        print("✅ Firewall configured successfully!")
        print("=" * 70)
