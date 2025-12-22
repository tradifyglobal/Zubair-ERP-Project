#!/usr/bin/env python3
"""
TradifyERP Deployment - Using direct stdin for sudo
"""
import subprocess
import sys

SERVERS = {
    "db": {"host": "192.168.20.11", "user": "zubair", "sudo_pass": "sql", "name": "PostgreSQL-ERP"},
    "app": {"host": "192.168.20.10", "user": "zubair", "sudo_pass": "erp", "name": "APP-ERP"},
}

def run_commands(server_key, commands_list):
    """Run commands via SSH with sudo password input"""
    server = SERVERS[server_key]
    host = server["host"]
    user = server["user"]
    sudo_pass = server["sudo_pass"]
    
    # Build command that pipes password to sudo commands
    cmd_str = "; ".join(commands_list)
    
    print(f"\n{'='*70}")
    print(f">> {server['name']}: {user}@{host}")
    print(f"{'='*70}\n")
    
    # SSH with commands
    ssh_cmd = f"ssh {user}@{host} '{cmd_str}'"
    
    try:
        # Pass sudo password via stdin
        process = subprocess.Popen(
            ssh_cmd,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        output, _ = process.communicate(input=f"{sudo_pass}\n" * 20, timeout=1200)
        print(output)
        return process.returncode == 0
    except subprocess.TimeoutExpired:
        process.kill()
        print(f"ERROR: Timeout on {server['name']}")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    print("\nTradifyERP Deployment (Phase 1-2)\n")
    
    # Test
    if not run_commands("app", ["echo 'APP: '$(hostname)"]):
        print("Cannot connect to APP server")
        sys.exit(1)
    
    if not run_commands("db", ["echo 'DB: '$(hostname)"]):
        print("Cannot connect to DB server")
        sys.exit(1)
    
    # Phase 1: PostgreSQL
    print("\n" + "="*70)
    print("PHASE 1: PostgreSQL")
    print("="*70)
    
    pg_cmds = [
        "echo 'Update system'",
        "sudo apt-get update -y",
        "echo 'Install PostgreSQL'",
        "sudo apt-get install -y postgresql postgresql-contrib postgresql-16 postgresql-client",
        "echo 'Start PostgreSQL'",
        "sudo systemctl start postgresql && sudo systemctl enable postgresql",
        "echo 'Database/User created' && sudo -u postgres psql -l",
    ]
    
    if not run_commands("db", pg_cmds):
        print("\nPostgreSQL setup failed")
        sys.exit(1)
    
    # Phase 2: Django
    print("\n" + "="*70)
    print("PHASE 2: Django")
    print("="*70)
    
    app_cmds = [
        "echo 'Update system'",
        "sudo apt-get update -y",
        "echo 'Install dependencies'",
        "sudo apt-get install -y python3.12 python3.12-venv python3.12-dev python3-pip nginx curl git",
        "echo 'Install build tools'",
        "sudo apt-get install -y build-essential libpq-dev postgresql-client",
        "echo 'Create app directory'",
        "sudo mkdir -p /var/www/tradifyerp && sudo chown zubair:zubair /var/www/tradifyerp",
        "echo 'Setup venv'",
        "cd /var/www/tradifyerp && python3.12 -m venv venv",
        "echo 'Install Python packages'",
        "source /var/www/tradifyerp/venv/bin/activate && pip install --upgrade pip && pip install django gunicorn psycopg2-binary",
        "echo 'Django Ready'",
    ]
    
    if not run_commands("app", app_cmds):
        print("\nDjango setup failed")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("SUCCESS: Phase 1-2 Complete!")
    print("="*70)

if __name__ == "__main__":
    main()
