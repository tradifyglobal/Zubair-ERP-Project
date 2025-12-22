#!/usr/bin/env python3
"""
TradifyERP Deployment - Complete Setup with Proper Credentials
App: 192.168.20.10 (zubair/erp, sudo: erp)
DB: 192.168.20.11 (zubair/sql, sudo: sql)
"""
import subprocess
import sys

# Server Configuration
SERVERS = {
    "db": {
        "host": "192.168.20.11",
        "user": "zubair",
        "sudo_pass": "sql",
        "name": "PostgreSQL-ERP"
    },
    "app": {
        "host": "192.168.20.10",
        "user": "zubair",
        "sudo_pass": "erp",
        "name": "APP-ERP"
    }
}

DB_PASSWORD = "zubair@0862"
DB_NAME = "tradify"
APP_DIR = "/var/www/tradifyerp"

def ssh_cmd(server_key, commands_list):
    """Execute SSH commands with sudo password"""
    server = SERVERS[server_key]
    host = server["host"]
    user = server["user"]
    sudo_pass = server["sudo_pass"]
    
    # Replace 'sudo' with 'echo password | sudo -S' for each command
    modified_commands = []
    for cmd in commands_list:
        if cmd.strip().startswith("sudo "):
            # Insert password for sudo commands
            modified_commands.append(f"echo '{sudo_pass}' | {cmd}")
        else:
            modified_commands.append(cmd)
    
    cmd_str = "; ".join(modified_commands)
    ssh_command = ["ssh", f"{user}@{host}", cmd_str]
    
    print(f"\n{'='*70}")
    print(f">> {server['name']}: {user}@{host}")
    print(f"{'='*70}\n")
    
    try:
        result = subprocess.run(ssh_command, timeout=1200)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"ERROR: Timeout on {server['name']}")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    print("""
========================================
TradifyERP Deployment
App: 192.168.20.10 | DB: 192.168.20.11
========================================
    """)
    
    # Test connectivity
    print("\n[TEST] Connecting to servers...")
    if not ssh_cmd("app", ["echo 'APP Server: '$(hostname)"]):
        print("ERROR: Cannot connect to APP server")
        sys.exit(1)
    
    if not ssh_cmd("db", ["echo 'DB Server: '$(hostname)"]):
        print("ERROR: Cannot connect to DB server")
        sys.exit(1)
    
    # Phase 1: PostgreSQL Setup
    print("\n" + "="*70)
    print("PHASE 1: PostgreSQL Setup (192.168.20.11)")
    print("="*70)
    
    pg_commands = [
        "echo '>>> System update'",
        "sudo apt-get update -y",
        "sudo apt-get upgrade -y",
        
        "echo '>>> Installing PostgreSQL 16'",
        "sudo apt-get install -y postgresql postgresql-contrib postgresql-16 postgresql-client",
        
        "echo '>>> Starting PostgreSQL'",
        "sudo systemctl start postgresql",
        "sudo systemctl enable postgresql",
        "sudo systemctl status postgresql | head -3",
        
        f"echo '>>> Creating database {DB_NAME}'",
        f"sudo -u postgres psql -c 'CREATE DATABASE {DB_NAME} ENCODING UTF8;' 2>/dev/null || echo 'Database already exists'",
        
        "echo '>>> Creating user zubair'",
        f"sudo -u postgres psql -c 'CREATE USER zubair WITH PASSWORD \"{DB_PASSWORD}\";' 2>/dev/null || echo 'User already exists'",
        
        "echo '>>> Granting privileges'",
        f"sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO zubair; ALTER USER zubair SUPERUSER CREATEDB;'",
        
        "echo '>>> Configuring remote access'",
        "PG_VER=$(sudo -u postgres psql --version | awk '{print $3}' | cut -d. -f1)",
        "sudo sed -i \"s/#listen_addresses = 'localhost'/listen_addresses = '*'/g\" /etc/postgresql/${PG_VER}/main/postgresql.conf",
        
        "echo '>>> Adding network access for app server'",
        "sudo bash -c \"echo 'host    tradify    zubair    192.168.20.10/32    md5' >> /etc/postgresql/${PG_VER}/main/pg_hba.conf\"",
        "sudo bash -c \"echo 'host    all        all       192.168.2.0/24     md5' >> /etc/postgresql/${PG_VER}/main/pg_hba.conf\"",
        
        "echo '>>> Restarting PostgreSQL'",
        "sudo systemctl restart postgresql",
        "sleep 2",
        "sudo systemctl status postgresql | head -3",
        
        "echo 'OK: PostgreSQL setup complete'",
    ]
    
    if not ssh_cmd("db", pg_commands):
        print("\nERROR: PostgreSQL setup failed")
        sys.exit(1)
    
    print("\nOK: PostgreSQL setup completed!")
    
    # Phase 2: Django Setup
    print("\n" + "="*70)
    print("PHASE 2: Django Setup (192.168.20.10)")
    print("="*70)
    
    django_commands = [
        "echo '>>> System update'",
        "sudo apt-get update -y",
        
        "echo '>>> Installing dependencies'",
        "sudo apt-get install -y python3.12 python3.12-venv python3.12-dev",
        "sudo apt-get install -y python3-pip git curl wget nginx",
        "sudo apt-get install -y build-essential libpq-dev postgresql-client",
        
        f"echo '>>> Creating {APP_DIR}'",
        f"sudo mkdir -p {APP_DIR}",
        f"sudo chown -R zubair:zubair {APP_DIR}",
        
        "echo '>>> Creating Python virtual environment'",
        f"python3.12 -m venv {APP_DIR}/venv",
        
        "echo '>>> Installing Python packages'",
        f"source {APP_DIR}/venv/bin/activate && pip install --upgrade pip setuptools wheel",
        f"source {APP_DIR}/venv/bin/activate && pip install django==5.2.9 gunicorn==23.0.0 psycopg2-binary djangorestframework django-cors-headers pillow",
        
        "echo '>>> Verifying Django installation'",
        f"source {APP_DIR}/venv/bin/activate && python -c 'import django; print(\"Django\", django.get_version())'",
        
        "echo '>>> Directory structure'",
        f"ls -la {APP_DIR}/",
        
        "echo 'OK: Django setup complete'",
    ]
    
    if not ssh_cmd("app", django_commands):
        print("\nERROR: Django setup failed")
        sys.exit(1)
    
    print("\nOK: Django setup completed!")
    
    print("\n" + "="*70)
    print("SUCCESS: Phase 1-2 Complete!")
    print("="*70)
    print("\nNext Steps:")
    print("  1. Copy TradifyERP application code to app server")
    print("  2. Run Django migrations")
    print("  3. Import production data")
    print("  4. Configure Gunicorn and Nginx")
    print("  5. Start services")

if __name__ == "__main__":
    main()
