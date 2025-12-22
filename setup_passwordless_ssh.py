#!/usr/bin/env python3
"""
Setup Passwordless SSH for Both Servers
Configures public key authentication for zubair@192.168.20.10 and zubair@192.168.20.11
"""

import subprocess
import os
from pathlib import Path

SSH_KEY_PATH = Path.home() / ".ssh" / "id_rsa"
SSH_PUB_KEY_PATH = Path.home() / ".ssh" / "id_rsa.pub"

APP_SERVER = "192.168.20.10"
DB_SERVER = "192.168.20.11"
APP_USER = "zubair"
DB_USER = "zubair"

def generate_ssh_key():
    """Generate SSH key if it doesn't exist"""
    print("\n" + "="*70)
    print("Step 1: Generate SSH Key (if needed)")
    print("="*70)
    
    if SSH_KEY_PATH.exists() and SSH_PUB_KEY_PATH.exists():
        print(f"✓ SSH key already exists: {SSH_KEY_PATH}")
        return True
    
    print(f"Generating new SSH key at {SSH_KEY_PATH}...")
    try:
        result = subprocess.run(
            ["ssh-keygen", "-t", "rsa", "-b", "4096", "-f", str(SSH_KEY_PATH), "-N", ""],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✓ SSH key generated successfully")
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def get_public_key():
    """Read the public key content"""
    try:
        with open(SSH_PUB_KEY_PATH, 'r') as f:
            return f.read().strip()
    except Exception as e:
        print(f"❌ Error reading public key: {e}")
        return None

def setup_server_passwordless(server, user, password):
    """Setup passwordless SSH on a server"""
    print(f"\n{'='*70}")
    print(f"Setting up passwordless SSH: {user}@{server}")
    print(f"{'='*70}")
    
    pub_key = get_public_key()
    if not pub_key:
        print("❌ Could not read public key")
        return False
    
    # Commands to run on remote server
    commands = [
        "mkdir -p ~/.ssh",
        "chmod 700 ~/.ssh",
        f"echo '{pub_key}' >> ~/.ssh/authorized_keys",
        "chmod 600 ~/.ssh/authorized_keys",
        "echo '✓ Public key added to authorized_keys'",
        "cat ~/.ssh/authorized_keys",
    ]
    
    cmd_str = "; ".join(commands)
    
    print(f"\n⏳ Connecting to {user}@{server}...")
    print(f"   (You may be prompted for password '{password}')\n")
    
    ssh_cmd = ["ssh", "-o", "StrictHostKeyChecking=no", f"{user}@{server}", cmd_str]
    
    try:
        result = subprocess.run(ssh_cmd, timeout=120)
        if result.returncode == 0:
            print(f"\n✓ Public key successfully added to {user}@{server}")
            return True
        else:
            print(f"\n❌ Failed to add public key to {user}@{server}")
            return False
    except subprocess.TimeoutExpired:
        print(f"\n❌ Timeout connecting to {server}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def test_passwordless_ssh(server, user):
    """Test passwordless SSH connection"""
    print(f"\n{'='*70}")
    print(f"Testing passwordless SSH: {user}@{server}")
    print(f"{'='*70}\n")
    
    ssh_cmd = ["ssh", "-o", "ConnectTimeout=5", f"{user}@{server}", "echo 'Passwordless SSH working! Connected to:'$(hostname)"]
    
    try:
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✓ {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Connection failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║  Setup Passwordless SSH for TradifyERP Servers            ║
║  App: 192.168.20.10 | DB: 192.168.20.11                    ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Generate SSH key
    if not generate_ssh_key():
        print("\n❌ Failed to generate SSH key")
        return False
    
    # Step 2: Setup App Server
    print(f"\n\n🔐 APP SERVER SETUP")
    if not setup_server_passwordless(APP_SERVER, APP_USER, "erp"):
        print(f"❌ Failed to setup {APP_USER}@{APP_SERVER}")
        return False
    
    # Step 3: Setup DB Server
    print(f"\n\n🔐 DB SERVER SETUP")
    if not setup_server_passwordless(DB_SERVER, DB_USER, "sql"):
        print(f"❌ Failed to setup {DB_USER}@{DB_SERVER}")
        return False
    
    # Step 4: Test both connections
    print("\n\n" + "="*70)
    print("TESTING PASSWORDLESS CONNECTIONS")
    print("="*70)
    
    success = True
    if not test_passwordless_ssh(APP_SERVER, APP_USER):
        print(f"❌ Test failed for {APP_USER}@{APP_SERVER}")
        success = False
    
    if not test_passwordless_ssh(DB_SERVER, DB_USER):
        print(f"❌ Test failed for {DB_USER}@{DB_SERVER}")
        success = False
    
    if success:
        print("\n" + "="*70)
        print("✅ PASSWORDLESS SSH SETUP COMPLETE!")
        print("="*70)
        print("\nYou can now connect without entering passwords:")
        print(f"  ssh {APP_USER}@{APP_SERVER}")
        print(f"  ssh {DB_USER}@{DB_SERVER}")
        print("\nNext step: Run deployment scripts")
        print("  python deploy_phase1_servers.py")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
