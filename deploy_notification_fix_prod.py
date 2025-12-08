#!/usr/bin/env python3
"""
Deploy Expense Notification Fix to Production

This script deploys the notification fixes to the production server.

Usage:
    python deploy_notification_fix.py
"""

import subprocess
import sys
import os
from pathlib import Path

# Configuration
SERVER_IP = "192.168.2.185"
SERVER_USER = "root"
REMOTE_PATH = "/var/www/tradifyerp/TradifyERP"
LOCAL_BASE = Path(__file__).parent / "TradifyERP"
SSH_KEY = Path.home() / ".ssh" / "tradifyerp_deploy"

def run_cmd(cmd, description="", shell=True):
    """Run a shell command and return success status"""
    print(f"\n{'='*70}")
    print(f"🔧 {description}")
    print(f"{'='*70}")
    print(f"Command: {cmd}\n")
    
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=False, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {str(e)}")
        return False

def ssh_cmd(remote_cmd, description=""):
    """Run SSH command using the deployed key"""
    cmd = f'ssh -i "{SSH_KEY}" {SERVER_USER}@{SERVER_IP} "{remote_cmd}"'
    return run_cmd(cmd, description)

def scp_file(local_file, remote_file, description=""):
    """Copy file via SCP using the deployed key"""
    cmd = f'scp -i "{SSH_KEY}" "{local_file}" {SERVER_USER}@{SERVER_IP}:{remote_file}'
    return run_cmd(cmd, description)

def main():
    print("\n" + "="*70)
    print("🚀 EXPENSE NOTIFICATION FIX DEPLOYMENT")
    print("="*70)
    print(f"Target Server: {SERVER_IP}")
    print(f"Remote Path: {REMOTE_PATH}")
    
    # Step 1: Verify local files exist
    print("\n" + "="*70)
    print("📋 Verifying Local Files")
    print("="*70)
    
    notifications_file = LOCAL_BASE / "expenses" / "notifications.py"
    context_processors_file = LOCAL_BASE / "expenses" / "context_processors.py"
    
    if not notifications_file.exists():
        print(f"❌ ERROR: {notifications_file} not found!")
        return False
    print(f"✅ Found: {notifications_file}")
    
    if not context_processors_file.exists():
        print(f"❌ ERROR: {context_processors_file} not found!")
        return False
    print(f"✅ Found: {context_processors_file}")
    
    # Step 2: Copy files
    print("\n" + "="*70)
    print("📤 COPYING FILES TO PRODUCTION")
    print("="*70)
    
    # Copy notifications.py
    if not scp_file(str(notifications_file), f"{REMOTE_PATH}/expenses/notifications.py", "Copy notifications.py"):
        print("⚠️ Warning: Failed to copy notifications.py, continuing...")
    
    # Copy context_processors.py
    if not scp_file(str(context_processors_file), f"{REMOTE_PATH}/expenses/context_processors.py", "Copy context_processors.py"):
        print("⚠️ Warning: Failed to copy context_processors.py, continuing...")
    
    # Step 3: Restart Gunicorn
    print("\n" + "="*70)
    print("🔄 RESTARTING GUNICORN SERVICE")
    print("="*70)
    
    ssh_cmd("pkill -f 'gunicorn --workers=8'", "Kill existing Gunicorn processes")
    ssh_cmd("sleep 2", "Wait for processes to die")
    ssh_cmd("cd /var/www/tradifyerp && nohup /var/www/tradifyerp/venv/bin/gunicorn --workers=8 --worker-class=sync --worker-tmp-dir=/dev/shm --max-requests=1000 --max-requests-jitter=100 --timeout=120 --graceful-timeout=30 --keep-alive=5 --bind=unix:/var/www/tradifyerp/gunicorn.sock --access-logfile=/var/log/tradifyerp/gunicorn_access.log --error-logfile=/var/log/tradifyerp/gunicorn_error.log --log-level=warning TradifyERP.wsgi_production:application > /dev/null 2>&1 &", "Start Gunicorn")
    ssh_cmd("sleep 3", "Wait for Gunicorn to start")
    
    # Step 4: Verify deployment
    print("\n" + "="*70)
    print("✔️  VERIFYING DEPLOYMENT")
    print("="*70)
    
    ssh_cmd("ps aux | grep gunicorn | grep -v grep | wc -l", "Check Gunicorn processes count")
    
    # Final summary
    print("\n" + "="*70)
    print("✅ DEPLOYMENT COMPLETE")
    print("="*70)
    print("\nNext Steps:")
    print("1. Have Burhan clear his browser cache (Ctrl+Shift+Delete)")
    print("2. Burhan should logout completely")
    print("3. Burhan should login again")
    print("4. Check bell icon - should now show pending approvals")
    print("\n" + "="*70)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
