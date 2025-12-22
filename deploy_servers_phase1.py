#!/usr/bin/env python3
import subprocess
import sys

DB_SERVER = "192.168.2.59"
APP_SERVER = "192.168.2.69"
DB_USER = "zubair"
APP_USER = "zubair"
DB_PASSWORD = "zubair@0862"
DB_NAME = "tradify"

def ssh_exec(host, user, commands_list):
    cmd_str = "; ".join(commands_list)
    ssh_cmd = ["ssh", f"{user}@{host}", cmd_str]
    print(f"\n{'='*70}\n>> SSH {user}@{host}\n{'='*70}\n")
    try:
        result = subprocess.run(ssh_cmd, timeout=600)
        return result.returncode == 0
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("TradifyERP Deployment Phase 1-2")
    print("App: 192.168.2.69 | DB: 192.168.2.59")
    print("="*70)
    
    # Test connectivity
    print("\nTesting connectivity...")
    if not ssh_exec(APP_SERVER, APP_USER, ["echo 'APP Server OK:'$(hostname)"]):
        print("ERROR: Cannot connect to APP Server")
        sys.exit(1)
    
    if not ssh_exec(DB_SERVER, DB_USER, ["echo 'DB Server OK:'$(hostname)"]):
        print("ERROR: Cannot connect to DB Server")
        sys.exit(1)
    
    # Phase 1: PostgreSQL
    print("\n" + "="*70)
    print("PHASE 1: PostgreSQL Setup")
    print("="*70)
    
    pg_commands = [
        "echo '[1/8] Updating packages'",
        "sudo apt-get update -y",
        "echo '[2/8] Installing PostgreSQL'",
        "sudo apt-get install -y postgresql postgresql-contrib postgresql-16 postgresql-client",
        "echo '[3/8] Starting PostgreSQL'",
        "sudo systemctl start postgresql && sudo systemctl enable postgresql",
        f"echo '[4/8] Creating database and user'",
        f"sudo -u postgres psql -c 'CREATE DATABASE {DB_NAME} ENCODING UTF8;' 2>/dev/null || echo 'DB already exists'",
        f"sudo -u postgres psql -c \"CREATE USER {DB_USER} WITH PASSWORD '{DB_PASSWORD}';\" 2>/dev/null || echo 'User already exists'",
        f"sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER}; ALTER USER {DB_USER} SUPERUSER CREATEDB;'",
        f"echo '[5/8] Configuring remote access'",
        f"PG_VERSION=$(sudo -u postgres psql --version | awk '{{print $3}}' | cut -d. -f1); sudo sed -i \"s/#listen_addresses = 'localhost'/listen_addresses = '*'/g\" /etc/postgresql/${{PG_VERSION}}/main/postgresql.conf",
        f"PG_VERSION=$(sudo -u postgres psql --version | awk '{{print $3}}' | cut -d. -f1); sudo bash -c \"echo '' >> /etc/postgresql/${{PG_VERSION}}/main/pg_hba.conf; echo 'host {DB_NAME} {DB_USER} {APP_SERVER}/32 md5' >> /etc/postgresql/${{PG_VERSION}}/main/pg_hba.conf; echo 'host all all 192.168.2.0/24 md5' >> /etc/postgresql/${{PG_VERSION}}/main/pg_hba.conf\"",
        "echo '[6/8] Restarting PostgreSQL'",
        "sudo systemctl restart postgresql",
        "echo 'OK: PostgreSQL Ready'",
    ]
    
    if not ssh_exec(DB_SERVER, DB_USER, pg_commands):
        print("\nERROR: PostgreSQL setup failed")
        sys.exit(1)
    
    print("\nOK: PostgreSQL setup completed!")
    
    # Phase 2: Django
    print("\n" + "="*70)
    print("PHASE 2: Django Setup")
    print("="*70)
    
    django_commands = [
        "echo '[1/8] Updating packages'",
        "sudo apt-get update -y",
        "echo '[2/8] Installing dependencies'",
        "sudo apt-get install -y python3.12 python3.12-venv python3.12-dev python3-pip git curl wget nginx build-essential libpq-dev postgresql-client",
        "echo '[3/8] Creating app directory'",
        f"sudo mkdir -p /var/www/tradifyerp && sudo chown -R {APP_USER}:{APP_USER} /var/www/tradifyerp",
        "echo '[4/8] Setting up virtual environment'",
        "cd /var/www/tradifyerp && python3.12 -m venv venv",
        "echo '[5/8] Installing Python packages'",
        "source /var/www/tradifyerp/venv/bin/activate && pip install --upgrade pip setuptools wheel",
        "source /var/www/tradifyerp/venv/bin/activate && pip install django==5.2.9 gunicorn==23.0.0 psycopg2-binary djangorestframework django-cors-headers pillow",
        "echo '[6/8] Verifying setup'",
        "source /var/www/tradifyerp/venv/bin/activate && python -c 'import django; print(\"Django version:\", django.get_version())'",
        "echo '[7/8] Checking requirements'",
        "ls -la /var/www/tradifyerp/venv/",
        "echo '[8/8] Django setup complete'",
    ]
    
    if not ssh_exec(APP_SERVER, APP_USER, django_commands):
        print("\nERROR: Django setup failed")
        sys.exit(1)
    
    print("\nOK: Django setup completed!")
    
    print("\n" + "="*70)
    print("SUCCESS: Phase 1-2 Complete!")
    print("="*70)
    print("\nNext: Deploy application code and data")
    print("  Run: python deploy_phase2_app.py")

if __name__ == "__main__":
    main()
