#!/usr/bin/env python3
"""
Production Deployment Script for Zubair ERP
Deploys the application to the production server via SSH
"""

import subprocess
import sys
import os
from pathlib import Path

# Configuration
SERVER_IP = "192.168.2.185"
SERVER_USER = "Zubair"
SERVER_HOST = f"{SERVER_USER}@{SERVER_IP}"
REMOTE_APP_PATH = "/home/Zubair/tradifyerp"  # Adjust if different
LOCAL_REPO_PATH = Path(__file__).parent

def run_command(cmd, description="", shell=False):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}\n")
    
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            check=True,
            cwd=LOCAL_REPO_PATH
        )
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e}")
        return False
    except FileNotFoundError as e:
        print(f"❌ Command not found: {e}")
        return False

def verify_ssh_connection():
    """Verify SSH connection to server"""
    print("\n" + "="*60)
    print("🔐 Verifying SSH Connection")
    print("="*60)
    
    cmd = f'ssh {SERVER_HOST} "echo SSH connection successful!"'
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        print(f"✅ SSH Connection: SUCCESS")
        print(f"Response: {result.stdout.strip()}")
        return True
    except subprocess.TimeoutExpired:
        print(f"❌ SSH Connection: TIMEOUT")
        print("The server did not respond in time. Check the IP address and network connectivity.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ SSH Connection: FAILED")
        print(f"Error: {e.stderr}")
        print("\nTroubleshooting:")
        print("1. Verify server IP: 192.168.2.185")
        print("2. Verify username: Zubair")
        print("3. Ensure SSH keys are set up (see SECURE_DEPLOYMENT_SETUP.md)")
        print("4. Check firewall allows SSH (port 22)")
        return False

def get_server_info():
    """Get server information"""
    cmd = f'ssh {SERVER_HOST} "uname -a && pwd"'
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        print("📊 Server Information:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Could not retrieve server info: {e.stderr}")

def backup_remote_app():
    """Backup current remote application"""
    print("\n" + "="*60)
    print("💾 Backing Up Remote Application")
    print("="*60)
    
    timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{REMOTE_APP_PATH}_backup_{timestamp}"
    
    cmd = f'ssh {SERVER_HOST} "[ -d {REMOTE_APP_PATH} ] && cp -r {REMOTE_APP_PATH} {backup_path} && echo Backup created at {backup_path} || echo No existing app to backup"'
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Warning: Backup may have failed: {e.stderr}")
        return False

def sync_repository():
    """Sync repository to server using rsync"""
    print("\n" + "="*60)
    print("📤 Syncing Repository to Server")
    print("="*60)
    
    # Exclude unwanted directories
    exclude_patterns = [
        ".git",
        "__pycache__",
        "*.pyc",
        ".pytest_cache",
        "node_modules",
        "db.sqlite3",
        ".env",
        ".venv",
        "venv",
        "BACKUPS",
        ".vscode"
    ]
    
    exclude_args = " ".join([f"--exclude='{p}'" for p in exclude_patterns])
    
    cmd = f'rsync -avz {exclude_args} --delete "{LOCAL_REPO_PATH.as_posix()}/" {SERVER_HOST}:{REMOTE_APP_PATH}/'
    
    return run_command(cmd, "Repository Sync via rsync")

def install_dependencies():
    """Install Python dependencies on server"""
    print("\n" + "="*60)
    print("📦 Installing Dependencies on Server")
    print("="*60)
    
    cmd = f'ssh {SERVER_HOST} "cd {REMOTE_APP_PATH} && python3 -m pip install -r requirements.txt --upgrade"'
    
    return run_command(cmd, "Install Python Dependencies")

def run_remote_migrations():
    """Run Django migrations on server"""
    print("\n" + "="*60)
    print("🗄️ Running Database Migrations")
    print("="*60)
    
    cmd = f'ssh {SERVER_HOST} "cd {REMOTE_APP_PATH} && python3 manage.py migrate"'
    
    return run_command(cmd, "Run Migrations")

def collect_static_files():
    """Collect static files on server"""
    print("\n" + "="*60)
    print("📂 Collecting Static Files")
    print("="*60)
    
    cmd = f'ssh {SERVER_HOST} "cd {REMOTE_APP_PATH} && python3 manage.py collectstatic --noinput"'
    
    return run_command(cmd, "Collect Static Files")

def restart_application():
    """Restart the application on server"""
    print("\n" + "="*60)
    print("🔄 Restarting Application")
    print("="*60)
    
    # Try multiple restart strategies
    commands = [
        f'ssh {SERVER_HOST} "sudo systemctl restart gunicorn"',  # Gunicorn service
        f'ssh {SERVER_HOST} "sudo systemctl restart tradifyerp"',  # Custom service
        f'ssh {SERVER_HOST} "pkill -f gunicorn && sleep 2"',  # Force kill gunicorn
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"✅ Application restarted successfully")
                return True
        except subprocess.TimeoutExpired:
            continue
        except Exception:
            continue
    
    print("⚠️ Could not restart application - manual restart may be required")
    return False

def verify_deployment():
    """Verify deployment was successful"""
    print("\n" + "="*60)
    print("✅ Verifying Deployment")
    print("="*60)
    
    cmd = f'ssh {SERVER_HOST} "curl -s http://localhost:8000/health || echo Application may still be starting..."'
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        print("Server response:")
        print(result.stdout)
    except Exception as e:
        print(f"Could not verify: {e}")

def main():
    """Main deployment orchestration"""
    print("\n" + "="*70)
    print("🚀 PRODUCTION DEPLOYMENT - Zubair ERP")
    print("="*70)
    print(f"Target Server: {SERVER_HOST}")
    print(f"Remote Path: {REMOTE_APP_PATH}")
    print(f"Local Repo: {LOCAL_REPO_PATH}")
    print("="*70)
    
    steps = [
        ("SSH Connection", verify_ssh_connection),
        ("Server Info", get_server_info),
        ("Backup", backup_remote_app),
        ("Sync Repository", sync_repository),
        ("Install Dependencies", install_dependencies),
        ("Run Migrations", run_remote_migrations),
        ("Collect Static", collect_static_files),
        ("Restart App", restart_application),
        ("Verify", verify_deployment),
    ]
    
    results = {}
    
    for step_name, step_func in steps:
        try:
            results[step_name] = step_func()
            if step_name == "SSH Connection" and not results[step_name]:
                print("\n❌ Cannot proceed without SSH connection!")
                print("Please follow SECURE_DEPLOYMENT_SETUP.md to configure SSH keys.")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error in {step_name}: {e}")
            results[step_name] = False
    
    # Summary
    print("\n" + "="*70)
    print("📋 DEPLOYMENT SUMMARY")
    print("="*70)
    
    for step, result in results.items():
        status = "✅ SUCCESS" if result else "❌ FAILED"
        print(f"{step:.<40} {status}")
    
    all_success = all(results.values())
    
    if all_success:
        print("\n" + "="*70)
        print("🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"Your application is now deployed at: http://192.168.2.185")
        return 0
    else:
        print("\n" + "="*70)
        print("⚠️ DEPLOYMENT COMPLETED WITH ERRORS")
        print("="*70)
        print("Please review the errors above and try again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
