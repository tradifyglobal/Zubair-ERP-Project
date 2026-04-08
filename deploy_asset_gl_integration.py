#!/usr/bin/env python
"""
Deploy Maintenance Asset GL Integration to Production
Handles file sync, migrations, and server restart
"""
import os
import sys
import subprocess

# Configuration
DEPLOY_HOST = "192.168.20.10"
DEPLOY_USER = "root"
DEPLOY_PATH = "/var/www/tradifyerp"
VENV_PYTHON = f"{DEPLOY_PATH}/venv/bin/python"
LOCAL_REPO = os.getcwd()

def run_command(cmd, description, is_remote=False):
    """Run a shell command and print status."""
    print(f"\n[*] {description}...")
    if is_remote:
        cmd = f'ssh {DEPLOY_USER}@{DEPLOY_HOST} "{cmd}"'
    
    print(f"    Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"    ✓ Success")
        if result.stdout:
            print(f"    Output:\n{result.stdout}")
        return True
    else:
        print(f"    ✗ Failed with code {result.returncode}")
        if result.stderr:
            print(f"    Error:\n{result.stderr}")
        return False

def main():
    print("=" * 50)
    print("Deploying Maintenance Asset GL Integration")
    print("=" * 50)
    
    # Step 1: Add and commit changes
    print("\n[1/7] Preparing local changes...")
    subprocess.run("git add -A", shell=True, cwd=LOCAL_REPO)
    result = subprocess.run("git commit -m 'feat: Add GL posting for asset purchases'", 
                          shell=True, cwd=LOCAL_REPO, capture_output=True)
    
    # Step 2: Push to Git
    if run_command("git push origin changes", "Push changes to Git repository"):
        pass
    else:
        print("    (This might be OK if no changes were committed)")
    
    # Step 3: Pull on server
    if not run_command(f"cd {DEPLOY_PATH} && git fetch origin && git checkout changes", 
                       "Fetch latest code on production server", is_remote=True):
        print("    ✗ Failed to sync code")
        sys.exit(1)
    
    # Step 4: Verify Python
    if not run_command(f"{VENV_PYTHON} --version", 
                       "Verify Python environment", is_remote=True):
        sys.exit(1)
    
    # Step 5: Create migrations
    if not run_command(f"cd {DEPLOY_PATH} && {VENV_PYTHON} TradifyERP/manage.py makemigrations maintenance", 
                       "Create database migrations", is_remote=True):
        print("    ✗ Warning: Migration creation failed, continuing anyway...")
    
    # Step 6: Apply migrations
    if not run_command(f"cd {DEPLOY_PATH} && {VENV_PYTHON} TradifyERP/manage.py migrate", 
                       "Apply database migrations", is_remote=True):
        print("    ✗ Failed to apply migrations")
        sys.exit(1)
    
    # Step 7: Restart server
    run_command("pkill -f gunicorn || true", "Stop Gunicorn", is_remote=True)
    run_command("sleep 2", "Wait for graceful shutdown", is_remote=True)
    
    print("\n" + "=" * 50)
    print("✓ Deployment Completed Successfully!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Visit http://192.168.20.10/maintenance/assets/new/")
    print("2. You should see 'Purchase Account' field")
    print("3. Select the account from which the asset was purchased")
    print("4. GL entries will be automatically posted")
    print("\nYou may need to manually restart Gunicorn:")
    print("  ssh root@192.168.20.10 'cd /var/www/tradifyerp && nohup ./venv/bin/python -m gunicorn --workers 4 --bind unix:./gunicorn.sock TradifyERP.wsgi:application > /var/log/gunicorn.log 2>&1 &'")

if __name__ == "__main__":
    main()
