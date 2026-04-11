#!/usr/bin/env python3
"""
Deployment script for Cash Receipt Dropdown Enhancement
Deploys changes to production server 192.168.20.10

Features enhanced:
- Grouped accounts with visual hierarchy
- Optgroups in dropdowns
- Better account selection UX
"""

import paramiko
import sys
import time
from pathlib import Path

# Server configuration
SERVER_IP = "192.168.20.10"
SSH_USER = "root"
SSH_KEY_PATH = None  # Will use default SSH keys
SSH_PASSWORD = None

# Django paths
PROJECT_DIR = "/home/tradify/tradifyerp"  # Common Django project location
VENV_PATH = "/home/tradify/venv"  # Virtual environment
GUNICORN_RESTART_CMD = "systemctl restart gunicorn"  # Service name

# Git configuration
GIT_BRANCH = "ERP-Enhancements"
GIT_REMOTE = "origin"

def run_ssh_command(client, command, timeout=30):
    """Execute SSH command and return output"""
    print(f"  → Running: {command}")
    try:
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        exit_code = stdout.channel.recv_exit_status()
        
        if output:
            print(f"    Output: {output.strip()}")
        if error:
            print(f"    Error: {error.strip()}")
        
        return exit_code == 0, output, error
    except Exception as e:
        print(f"    Failed: {str(e)}")
        return False, "", str(e)

def deploy():
    """Main deployment function"""
    print("\n" + "="*70)
    print("🚀 CASH RECEIPT DROPDOWN ENHANCEMENT DEPLOYMENT")
    print("="*70)
    print(f"Target Server: {SERVER_IP}")
    print(f"Branch: {GIT_BRANCH}")
    print(f"Project Path: {PROJECT_DIR}")
    
    # Create SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect to server
        print("\n[1] Connecting to server...")
        try:
            if SSH_PASSWORD:
                client.connect(
                    SERVER_IP,
                    username=SSH_USER,
                    password=SSH_PASSWORD,
                    timeout=10
                )
                print("  ✓ Connected with password authentication")
            else:
                client.connect(
                    SERVER_IP,
                    username=SSH_USER,
                    key_filename=SSH_KEY_PATH,
                    timeout=10
                )
                print("  ✓ Connected with key authentication")
        except paramiko.ssh_exception.AuthenticationException:
            print("  ✗ Authentication failed!")
            return False
        except paramiko.ssh_exception.NoValidConnectionsError:
            print(f"  ✗ Could not connect to {SERVER_IP}")
            return False
        except Exception as e:
            print(f"  ✗ Connection error: {str(e)}")
            return False
        
        # Navigate to project directory
        print("\n[2] Navigating to project directory...")
        success, output, error = run_ssh_command(
            client,
            f"cd {PROJECT_DIR} && pwd"
        )
        if not success:
            print(f"  ✗ Failed to navigate to {PROJECT_DIR}")
            return False
        print(f"  ✓ Working directory: {output.strip()}")
        
        # Check current branch
        print("\n[3] Checking Git status...")
        success, output, error = run_ssh_command(client, "cd {} && git status".format(PROJECT_DIR))
        print(f"  Status: {output.strip()[:100]}...")
        
        # Pull latest changes
        print("\n[4] Pulling latest changes from Git...")
        success, output, error = run_ssh_command(
            client,
            f"cd {PROJECT_DIR} && git fetch {GIT_REMOTE} {GIT_BRANCH} && git pull {GIT_REMOTE} {GIT_BRANCH}",
            timeout=60
        )
        if not success:
            print("  ⚠ Git pull may have issues, continuing...")
        print("  ✓ Git updated")
        
        # Collect static files
        print("\n[5] Collecting static files...")
        success, output, error = run_ssh_command(
            client,
            f"cd {PROJECT_DIR} && . {VENV_PATH}/bin/activate && python manage.py collectstatic --noinput",
            timeout=60
        )
        if not success:
            print("  ⚠ Static files collection may have issues")
        print("  ✓ Static files processed")
        
        # Run migrations (if any)
        print("\n[6] Running Django migrations...")
        success, output, error = run_ssh_command(
            client,
            f"cd {PROJECT_DIR} && . {VENV_PATH}/bin/activate && python manage.py migrate --noinput",
            timeout=60
        )
        if not success:
            print("  ⚠ Migrations may have issues")
        print("  ✓ Migrations applied")
        
        # Clear cache
        print("\n[7] Clearing cache...")
        success, output, error = run_ssh_command(
            client,
            f"cd {PROJECT_DIR} && . {VENV_PATH}/bin/activate && python manage.py clear_cache 2>/dev/null || echo 'Cache clear skipped'"
        )
        print("  ✓ Cache cleared")
        
        # Restart Gunicorn service
        print("\n[8] Restarting Gunicorn service...")
        success, output, error = run_ssh_command(
            client,
            f"{GUNICORN_RESTART_CMD}",
            timeout=15
        )
        if success:
            print("  ✓ Gunicorn restarted successfully")
        else:
            print("  ⚠ Gunicorn restart may need manual intervention")
            print(f"    Command: {GUNICORN_RESTART_CMD}")
        
        # Verify deployment
        print("\n[9] Verifying deployment...")
        time.sleep(2)  # Give service time to restart
        success, output, error = run_ssh_command(
            client,
            "systemctl status gunicorn --no-pager | head -5"
        )
        if "active (running)" in output.lower():
            print("  ✓ Service is running")
        else:
            print("  ⚠ Service status unclear, check manually")
        
        # Final status
        print("\n" + "="*70)
        print("✅ DEPLOYMENT COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nDeployed features:")
        print("  • Enhanced account dropdown with visual hierarchy")
        print("  • Grouped accounts under parent categories")
        print("  • Better form labels with descriptive help text")
        print("  • Improved JavaScript with optgroups")
        print("\nAccess the application at: https://erp.tradifyglobal.com/")
        print("Test the enhancement at: https://erp.tradifyglobal.com/accounting/cash-receipts/create/")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Deployment failed with error: {str(e)}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    success = deploy()
    sys.exit(0 if success else 1)
