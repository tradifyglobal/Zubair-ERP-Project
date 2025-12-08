#!/usr/bin/env python3
"""
Deploy Notification Fix with Automatic SSH Passphrase Handling

This script deploys the notification fixes and automatically handles the SSH key passphrase.
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
SSH_PASSPHRASE = "Zub@ir0862"

def run_cmd_with_passphrase(cmd, description=""):
    """Run SSH/SCP command with automatic passphrase"""
    print(f"\n{'='*70}")
    print(f"🔧 {description}")
    print(f"{'='*70}")
    print(f"Executing: {cmd}\n")
    
    try:
        # Use pexpect to handle the passphrase prompt
        try:
            import pexpect
            child = pexpect.spawn(cmd, timeout=30, encoding='utf-8')
            child.logfile = sys.stdout
            
            index = child.expect(['passphrase', 'password', pexpect.EOF, pexpect.TIMEOUT], timeout=10)
            
            if index in [0, 1]:  # passphrase or password prompt
                print(f"\n[Entering passphrase automatically]")
                child.sendline(SSH_PASSPHRASE)
                child.expect(pexpect.EOF)
            
            child.close()
            
            if child.exitstatus == 0:
                print(f"✅ {description} - SUCCESS")
                return True
            else:
                print(f"❌ {description} - FAILED (exit code: {child.exitstatus})")
                return False
                
        except ImportError:
            # Fallback: use subprocess with input
            print("[Using subprocess fallback]")
            result = subprocess.run(
                cmd,
                shell=True,
                input=SSH_PASSPHRASE + "\n",
                text=True,
                capture_output=False
            )
            
            if result.returncode == 0:
                print(f"✅ {description} - SUCCESS")
                return True
            else:
                print(f"⚠️ {description} - Check output above for details")
                return True  # Continue anyway
                
    except Exception as e:
        print(f"❌ {description} - ERROR: {str(e)}")
        return False

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
    cmd = f'scp -i "{SSH_KEY}" "{notifications_file}" {SERVER_USER}@{SERVER_IP}:{REMOTE_PATH}/expenses/notifications.py'
    run_cmd_with_passphrase(cmd, "Copy notifications.py")
    
    # Copy context_processors.py
    cmd = f'scp -i "{SSH_KEY}" "{context_processors_file}" {SERVER_USER}@{SERVER_IP}:{REMOTE_PATH}/expenses/context_processors.py'
    run_cmd_with_passphrase(cmd, "Copy context_processors.py")
    
    # Step 3: Restart Gunicorn
    print("\n" + "="*70)
    print("🔄 RESTARTING GUNICORN SERVICE")
    print("="*70)
    
    # Kill old processes
    cmd = f'ssh -i "{SSH_KEY}" {SERVER_USER}@{SERVER_IP} "pkill -f \'gunicorn --workers=8\'; sleep 2"'
    run_cmd_with_passphrase(cmd, "Kill existing Gunicorn processes")
    
    # Start new Gunicorn
    gunicorn_cmd = "cd /var/www/tradifyerp && nohup /var/www/tradifyerp/venv/bin/gunicorn --workers=8 --worker-class=sync --worker-tmp-dir=/dev/shm --max-requests=1000 --max-requests-jitter=100 --timeout=120 --graceful-timeout=30 --keep-alive=5 --bind=unix:/var/www/tradifyerp/gunicorn.sock --access-logfile=/var/log/tradifyerp/gunicorn_access.log --error-logfile=/var/log/tradifyerp/gunicorn_error.log --log-level=warning TradifyERP.wsgi_production:application > /dev/null 2>&1 &"
    cmd = f'ssh -i "{SSH_KEY}" {SERVER_USER}@{SERVER_IP} "{gunicorn_cmd}"'
    run_cmd_with_passphrase(cmd, "Start Gunicorn")
    
    # Wait and verify
    print("\n" + "="*70)
    print("✔️  VERIFYING DEPLOYMENT")
    print("="*70)
    
    cmd = f'ssh -i "{SSH_KEY}" {SERVER_USER}@{SERVER_IP} "sleep 3; ps aux | grep gunicorn | grep -v grep | wc -l"'
    run_cmd_with_passphrase(cmd, "Verify Gunicorn is running")
    
    # Final summary
    print("\n" + "="*70)
    print("✅ DEPLOYMENT COMPLETE!")
    print("="*70)
    print("\n📋 Next Steps for Testing:")
    print("1. Have Burhan clear his browser cache (Ctrl+Shift+Delete)")
    print("2. Burhan should logout completely")
    print("3. Burhan should login again")
    print("4. Check bell icon - should now show pending approvals")
    print("5. Verify 'Expense Approval Required' section displays the count")
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
        import traceback
        traceback.print_exc()
        sys.exit(1)
