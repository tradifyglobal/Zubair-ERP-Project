#!/usr/bin/env python3
"""
Orchestrated deployment to new servers (192.168.20.10 + 192.168.20.11)
Handles PostgreSQL setup, Django deployment, and data import
"""

import subprocess
import sys
import os
from pathlib import Path

# Configuration
DB_SERVER = "192.168.20.11"
APP_SERVER = "192.168.20.10"
DB_USER = "zubair"
DB_PASSWORD = "zubair@0862"
DB_NAME = "tradify"
APP_USER = "zubair"
APP_PASSWORD = "erp"

# Paths
PROJECT_ROOT = Path(__file__).parent
TRADIFY_DIR = PROJECT_ROOT / "TradifyERP"
DATA_BACKUP = TRADIFY_DIR / "prod_data_complete_backup.json"
NGINX_CONF = PROJECT_ROOT / "nginx_tradifyglobal_prod.conf"
DJANGO_SETTINGS = PROJECT_ROOT / "BACKUPS" / "postgres_checkpoint_2025-11-16_09-14-23" / "settings_production.py"

def run_ssh(host, user, command, password=None):
    """Run SSH command on remote host"""
    print(f"\n➤ SSH to {host}: {command[:80]}...")
    try:
        result = subprocess.run(
            ["ssh", f"{user}@{host}", command],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False
        print(f"✓ Success")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def scp_file(local_path, remote_host, remote_user, remote_path):
    """Copy file to remote host"""
    print(f"\n➤ Copying {local_path} to {remote_host}:{remote_path}...")
    try:
        result = subprocess.run(
            ["scp", str(local_path), f"{remote_user}@{remote_host}:{remote_path}"],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False
        print(f"✓ Copied")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def setup_postgres():
    """Setup PostgreSQL on DB server"""
    print("\n" + "="*60)
    print("PHASE 1: Setting up PostgreSQL on 192.168.20.11")
    print("="*60)
    
    commands = [
        "sudo apt-get update -y && sudo apt-get upgrade -y",
        "sudo apt-get install -y postgresql postgresql-contrib postgresql-16 postgresql-client",
        "sudo systemctl start postgresql && sudo systemctl enable postgresql",
        "sudo systemctl status postgresql",
    ]
    
    for cmd in commands:
        if not run_ssh(DB_SERVER, DB_USER, cmd):
            return False
    
    # Create database and user
    psql_cmd = f"""sudo -u postgres psql << 'EOF'
CREATE DATABASE {DB_NAME} ENCODING 'UTF8';
CREATE USER {DB_USER} WITH PASSWORD '{DB_PASSWORD}';
ALTER ROLE {DB_USER} SET client_encoding TO 'utf8';
ALTER ROLE {DB_USER} SET default_transaction_isolation TO 'read committed';
ALTER ROLE {DB_USER} SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER};
ALTER USER {DB_USER} CREATEDB SUPERUSER;
\\l
EOF"""
    
    if not run_ssh(DB_SERVER, DB_USER, psql_cmd):
        return False
    
    # Configure for remote access
    print("\n➤ Configuring PostgreSQL for remote access...")
    config_cmd = """sudo bash -c "
PG_VERSION=$(sudo -u postgres psql --version | awk '{print $3}' | cut -d. -f1)
PG_CONFIG=/etc/postgresql/\\${PG_VERSION}/main
sed -i \"s/#listen_addresses = 'localhost'/listen_addresses = '*'/g\" \\${PG_CONFIG}/postgresql.conf
cat >> \\${PG_CONFIG}/pg_hba.conf << 'PGEOF'

host    {DB_NAME}    {DB_USER}    {APP_SERVER}/32    md5
host    all        all       192.168.2.0/24     md5
PGEOF
systemctl restart postgresql
systemctl status postgresql
"
""".format(DB_NAME=DB_NAME, DB_USER=DB_USER, APP_SERVER=APP_SERVER)
    
    if not run_ssh(DB_SERVER, DB_USER, config_cmd):
        return False
    
    print("\n✅ PostgreSQL Setup Complete!")
    print(f"   Connection: psql -h {DB_SERVER} -U {DB_USER} -d {DB_NAME}")
    return True

def setup_django():
    """Setup Django on App server"""
    print("\n" + "="*60)
    print("PHASE 2: Setting up Django on 192.168.20.10")
    print("="*60)
    
    # Update and install dependencies
    commands = [
        "sudo apt-get update -y && sudo apt-get upgrade -y",
        "sudo apt-get install -y python3.12 python3.12-venv python3.12-dev",
        "sudo apt-get install -y python3-pip git curl wget nginx",
        "sudo apt-get install -y build-essential libpq-dev postgresql-client",
    ]
    
    for cmd in commands:
        if not run_ssh(APP_SERVER, APP_USER, cmd):
            return False
    
    # Create app directory and virtual environment
    setup_app_cmd = """
sudo mkdir -p /var/www/tradifyerp
sudo chown -R {APP_USER}:{APP_USER} /var/www/tradifyerp
cd /var/www/tradifyerp
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
""".format(APP_USER=APP_USER)
    
    if not run_ssh(APP_SERVER, APP_USER, setup_app_cmd):
        return False
    
    print("\n✅ Django Server Base Setup Complete!")
    return True

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║  TradifyERP New Server Deployment Orchestrator            ║
║  App: 192.168.20.10 | DB: 192.168.20.11                    ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Phase 1: PostgreSQL
    if not setup_postgres():
        print("\n❌ PostgreSQL setup failed!")
        sys.exit(1)
    
    # Phase 2: Django
    if not setup_django():
        print("\n❌ Django setup failed!")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ DEPLOYMENT PHASES 1-2 COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Copy application code to app server")
    print("2. Run migrations")
    print("3. Import data")
    print("4. Configure Gunicorn and Nginx")
    print("5. Start services and test")

if __name__ == "__main__":
    main()
