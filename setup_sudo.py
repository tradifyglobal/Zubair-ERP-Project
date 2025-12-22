#!/usr/bin/env python3
"""
Setup servers with manual sudo password input
"""
import subprocess
import sys

servers = [
    {"host": "192.168.2.59", "user": "zubair", "name": "DB"},
    {"host": "192.168.2.69", "user": "zubair", "name": "APP"},
]

def setup_server(host, user, name):
    print(f"\n{'='*70}")
    print(f"Configuring {name} Server: {user}@{host}")
    print(f"{'='*70}\n")
    
    # Commands to run
    commands = f"""
    echo "Configuring passwordless sudo..."
    echo {user} | sudo -S bash << 'EOF'
    # Add passwordless sudo for zubair
    echo "{user} ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/{user}
    chmod 440 /etc/sudoers.d/{user}
    echo "Passwordless sudo configured"
    
    # Verify
    id
    EOF
    """
    
    ssh_cmd = f"ssh -t {user}@{host} '{commands}'"
    print(f"Running: {ssh_cmd}\n")
    
    result = subprocess.run(ssh_cmd, shell=True)
    return result.returncode == 0

if __name__ == "__main__":
    for server in servers:
        if not setup_server(server["host"], server["user"], server["name"]):
            print(f"\nWARNING: Could not configure {server['name']} server")
    
    print("\n" + "="*70)
    print("Passwordless sudo configuration complete!")
    print("="*70)
