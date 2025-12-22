#!/usr/bin/env python3
"""
TradifyERP Deployment - Phase 1-2 (with proper TTY for sudo)
"""
import subprocess
import sys

DB_SERVER = "192.168.20.11"
APP_SERVER = "192.168.20.10"
DB_USER = "zubair"
APP_USER = "zubair"
DB_PASSWORD = "zubair@0862"
DB_NAME = "tradify"

def run_ssh_cmd(host, user, cmd_list, use_tty=False):
    """Run SSH command, using TTY for sudo if needed"""
    cmd_str = "; ".join(cmd_list)
    
    if use_tty:
        ssh_cmd = ["ssh", "-t", f"{user}@{host}", cmd_str]
    else:
        ssh_cmd = ["ssh", f"{user}@{host}", cmd_str]
    
    print(f"\n{'='*70}\n>> SSH {user}@{host}\n{'='*70}\n")
    
    try:
        result = subprocess.run(ssh_cmd, timeout=900)
        return result.returncode == 0
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    print("\nTradifyERP Deployment Phase 1-2\nApp: 192.168.20.10 | DB: 192.168.20.11\n")
    
    # Test connectivity
    if not run_ssh_cmd(APP_SERVER, APP_USER, ["echo 'APP: OK'$(hostname)"]):
        print("ERROR: Cannot connect to APP Server")
        sys.exit(1)
    
    if not run_ssh_cmd(DB_SERVER, DB_USER, ["echo 'DB: OK'$(hostname)"]):
        print("ERROR: Cannot connect to DB Server")
        sys.exit(1)
    
    # Phase 1: PostgreSQL (use TTY for sudo)
    print("\n" + "="*70)
    print("PHASE 1: PostgreSQL Setup")
    print("="*70)
    
    pg_commands = [
        "echo '[1/6] Updating packages'",
        "sudo apt-get update -y",
        "echo '[2/6] Installing PostgreSQL'",
        "sudo apt-get install -y postgresql postgresql-contrib postgresql-16 postgresql-client",
        "echo '[3/6] Enabling and starting PostgreSQL'",
        "sudo systemctl start postgresql; sudo systemctl enable postgresql",
        f"echo '[4/6] Creating database {DB_NAME}'",
        f"sudo -u postgres psql -c 'CREATE DATABASE {DB_NAME} ENCODING UTF8;' 2>/dev/null || echo 'DB exists'",
        f"sudo -u postgres psql -c \"CREATE USER {DB_USER} WITH PASSWORD '{DB_PASSWORD}';\" 2>/dev/null || echo 'User exists'",
        f"sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER}; ALTER USER {DB_USER} SUPERUSER CREATEDB;'",
        "echo '[5/6] Configuring remote access'",
        f"PG_VER=$(sudo -u postgres psql --version | awk '{{print $3}}' | cut -d. -f1)",
        "sudo sed -i \"s/#listen_addresses = 'localhost'/listen_addresses = '*'/g\" /etc/postgresql/${PG_VER}/main/postgresql.conf",
        f"sudo bash -c \"echo '' >> /etc/postgresql/${{PG_VER}}/main/pg_hba.conf; echo 'host {DB_NAME} {DB_USER} {APP_SERVER}/32 md5' >> /etc/postgresql/${{PG_VER}}/main/pg_hba.conf; echo 'host all all 192.168.2.0/24 md5' >> /etc/postgresql/${{PG_VER}}/main/pg_hba.conf\"",
        "echo '[6/6] Restarting PostgreSQL'",
        "sudo systemctl restart postgresql; sleep 2",
        "echo 'OK: PostgreSQL Ready'",
    ]
    
    if not run_ssh_cmd(DB_SERVER, DB_USER, pg_commands, use_tty=True):
        print("ERROR: PostgreSQL setup failed")
        sys.exit(1)
    
    print("\nOK: PostgreSQL setup completed!")
    
    # Phase 2: Django (use TTY for sudo)
    print("\n" + "="*70)
    print("PHASE 2: Django Setup")
    print("="*70)
    
    django_commands = [
        "echo '[1/8] Updating packages'",
        "sudo apt-get update -y",
        "echo '[2/8] Installing dependencies'",
        "sudo apt-get install -y python3.12 python3.12-venv python3.12-dev python3-pip git curl wget nginx build-essential libpq-dev postgresql-client",
        "echo '[3/8] Creating app directory'",
        f"sudo mkdir -p /var/www/tradifyerp; sudo chown -R {APP_USER}:{APP_USER} /var/www/tradifyerp",
        "echo '[4/8] Creating virtualenv'",
        "python3.12 -m venv /var/www/tradifyerp/venv",
        "echo '[5/8] Installing Python packages'",
        "source /var/www/tradifyerp/venv/bin/activate; pip install --upgrade pip setuptools wheel",
        "source /var/www/tradifyerp/venv/bin/activate; pip install django==5.2.9 gunicorn==23.0.0 psycopg2-binary djangorestframework django-cors-headers pillow",
        "echo '[6/8] Verifying Django'",
        "source /var/www/tradifyerp/venv/bin/activate; python -c 'import django; print(\"Django\", django.get_version())'",
        "echo '[7/8] Checking app directory'",
        "ls -la /var/www/tradifyerp/",
        "echo '[8/8] Django setup complete'",
    ]
    
    if not run_ssh_cmd(APP_SERVER, APP_USER, django_commands, use_tty=True):
        print("ERROR: Django setup failed")
        sys.exit(1)
    
    print("\nOK: Django setup completed!")
    
    print("\n" + "="*70)
    print("SUCCESS: Phase 1-2 Complete!")
    print("="*70)
    print("\nNext steps:")
    print("  1. python deploy_app_code.py - Copy TradifyERP code")
    print("  2. python deploy_migrations_and_data.py - Run migrations and import data")

if __name__ == "__main__":
    main()
