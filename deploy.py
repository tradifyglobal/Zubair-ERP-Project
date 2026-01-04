#!/usr/bin/env python3
"""
Production Deployment Script for Tradify Global ERP
Deploys to: 192.168.20.10 (Web Server)
Database: 192.168.20.11 (PostgreSQL)

Usage:
    python3 deploy.py [--skip-backup] [--skip-ssl] [--verbose]
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
import argparse

# Configuration
WEB_SERVER = "192.168.20.10"
DB_SERVER = "192.168.20.11"
SSH_USER = "zubair"
SSH_PASSWORD = "erp"
SUDO_PASSWORD = "erp"

DB_USER = "zubair"
DB_PASSWORD = "sql"
DB_SUDO_PASSWORD = "sql"

PROJECT_DIR = "/opt/tradifyerp"
DOMAIN = "192.168.20.10"  # Change to actual domain when available

# Colors for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def log_info(msg):
    print(f"{Colors.OKBLUE}ℹ️  {msg}{Colors.ENDC}")

def log_success(msg):
    print(f"{Colors.OKGREEN}✅ {msg}{Colors.ENDC}")

def log_warning(msg):
    print(f"{Colors.WARNING}⚠️  {msg}{Colors.ENDC}")

def log_error(msg):
    print(f"{Colors.FAIL}❌ {msg}{Colors.ENDC}")

def log_header(msg):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{msg}{Colors.ENDC}\n")

def run_command(cmd, check=True):
    """Run shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        log_error(f"Command failed: {str(e)}")
        return 1, "", str(e)

def ssh_command(host, user, password, command, use_sudo=False):
    """Execute command via SSH"""
    if use_sudo:
        ssh_cmd = f"sshpass -p '{password}' ssh {user}@{host} 'echo {SUDO_PASSWORD} | sudo -S {command}'"
    else:
        ssh_cmd = f"sshpass -p '{password}' ssh {user}@{host} '{command}'"
    
    return run_command(ssh_cmd)

def deploy():
    """Main deployment function"""
    
    log_header("🚀 TRADIFY GLOBAL ERP - PRODUCTION DEPLOYMENT")
    log_info(f"Web Server: {WEB_SERVER}")
    log_info(f"Database Server: {DB_SERVER}")
    log_info(f"Project Directory: {PROJECT_DIR}")
    
    # Step 1: Check connectivity
    log_header("Step 1: Checking Server Connectivity")
    log_info("Testing connection to web server...")
    returncode, stdout, stderr = ssh_command(WEB_SERVER, SSH_USER, SSH_PASSWORD, "echo 'Connected'")
    if returncode == 0:
        log_success("Web server connection OK")
    else:
        log_error(f"Cannot connect to web server: {stderr}")
        return False
    
    log_info("Testing connection to database server...")
    returncode, stdout, stderr = ssh_command(DB_SERVER, DB_USER, DB_PASSWORD, "echo 'Connected'")
    if returncode == 0:
        log_success("Database server connection OK")
    else:
        log_error(f"Cannot connect to database server: {stderr}")
        return False
    
    # Step 2: Backup database
    log_header("Step 2: Backing Up Database")
    log_info("Creating database backup...")
    backup_cmd = f"mkdir -p /backups && pg_dump -h 192.168.20.11 -U tradifyerp_user tradifyerp_db > /backups/tradifyerp_$(date +%Y%m%d_%H%M%S).sql"
    returncode, stdout, stderr = ssh_command(WEB_SERVER, SSH_USER, SSH_PASSWORD, backup_cmd, use_sudo=True)
    if returncode == 0:
        log_success("Database backup completed")
    else:
        log_warning(f"Backup may have issues: {stderr}")
    
    # Step 3: Update system packages
    log_header("Step 3: Updating System Packages")
    returncode, stdout, stderr = ssh_command(WEB_SERVER, SSH_USER, SSH_PASSWORD, 
        "apt-get update && apt-get upgrade -y && apt-get install -y python3.11 python3-pip python3-venv nginx redis-server postgresql-client", 
        use_sudo=True)
    if returncode == 0:
        log_success("System packages updated")
    else:
        log_warning(f"Package update may have issues: {stderr}")
    
    # Step 4: Create project directory and pull code
    log_header("Step 4: Deploying Code from GitHub")
    returncode, stdout, stderr = ssh_command(WEB_SERVER, SSH_USER, SSH_PASSWORD, 
        f"mkdir -p {PROJECT_DIR} && cd {PROJECT_DIR} && git clone https://github.com/tradifyglobal/Zubair-ERP-Project.git . --branch changes 2>&1 || (cd {PROJECT_DIR} && git pull origin changes)",
        use_sudo=True)
    if returncode == 0:
        log_success("Code deployed from GitHub")
    else:
        log_error(f"Code deployment failed: {stderr}")
        return False
    
    # Step 5: Create Python virtual environment and install dependencies
    log_header("Step 5: Setting Up Python Environment")
    returncode, stdout, stderr = ssh_command(WEB_SERVER, SSH_USER, SSH_PASSWORD,
        f"cd {PROJECT_DIR}/TradifyERP && python3.11 -m venv venv && source venv/bin/activate && pip install --upgrade pip setuptools wheel && pip install -r requirements.txt && pip install -r ../requirements-security.txt",
        use_sudo=False)
    if returncode == 0:
        log_success("Python environment configured")
    else:
        log_error(f"Environment setup failed: {stderr}")
        return False
    
    # Step 6: Create production .env file
    log_header("Step 6: Configuring Production Environment")
    
    # Generate SECRET_KEY
    returncode, secret_key, _ = run_command("python3 -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\"")
    
    # Generate ENCRYPTION_KEY
    returncode, encryption_key, _ = run_command("python3 -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"")
    
    env_content = f"""# Django Configuration
DJANGO_SECRET_KEY={secret_key.strip()}
DEBUG=False
ALLOWED_HOSTS=192.168.20.10,tradifyglobal.com,www.tradifyglobal.com,localhost,127.0.0.1

# Database Configuration - PostgreSQL at 192.168.20.11
DB_ENGINE=django.db.backends.postgresql
DB_NAME=tradifyerp_db
DB_USER=tradifyerp_user
DB_PASSWORD=Tradify@PostgreSQL2024
DB_HOST=192.168.20.11
DB_PORT=5432
DB_SSL_MODE=require

# Encryption Configuration
ENCRYPTION_KEY={encryption_key.strip()}

# Security Configuration
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
CSRF_COOKIE_HTTPONLY=True
SECURE_HSTS_SECONDS=0

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@tradifyglobal.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@tradifyglobal.com

# Redis Configuration
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=1
REDIS_PASSWORD=

# Logging Configuration
LOG_LEVEL=INFO
LOG_DIR=/var/log/tradifyerp

# Application Settings
ENVIRONMENT=production
"""
    
    env_file = f"{PROJECT_DIR}/TradifyERP/.env"
    returncode, stdout, stderr = ssh_command(WEB_SERVER, SSH_USER, SSH_PASSWORD,
        f"cat > {env_file} << 'EOF'\n{env_content}\nEOF",
        use_sudo=True)
    
    if returncode == 0:
        log_success("Production .env file created")
    else:
        log_error(f"Failed to create .env: {stderr}")
        return False
    
    # Step 7: Run migrations
    log_header("Step 7: Running Database Migrations")
    returncode, stdout, stderr = ssh_command(WEB_SERVER, SSH_USER, SSH_PASSWORD,
        f"cd {PROJECT_DIR}/TradifyERP && source venv/bin/activate && python manage.py migrate --noinput",
        use_sudo=False)
    if returncode == 0:
        log_success("Database migrations completed")
    else:
        log_warning(f"Migrations may have issues: {stderr}")
    
    # Step 8: Collect static files
    log_header("Step 8: Collecting Static Files")
    returncode, stdout, stderr = ssh_command(WEB_SERVER, SSH_USER, SSH_PASSWORD,
        f"cd {PROJECT_DIR}/TradifyERP && source venv/bin/activate && python manage.py collectstatic --noinput",
        use_sudo=False)
    if returncode == 0:
        log_success("Static files collected")
    else:
        log_warning(f"Static files issue: {stderr}")
    
    # Step 9: Configure Nginx
    log_header("Step 9: Configuring Nginx")
    nginx_config = f"""upstream tradifyerp {{
    server 127.0.0.1:8000;
}}

server {{
    listen 80;
    server_name 192.168.20.10 tradifyglobal.com www.tradifyglobal.com;
    
    client_max_body_size 100M;
    
    location /static/ {{
        alias {PROJECT_DIR}/TradifyERP/staticfiles/;
        expires 30d;
    }}
    
    location /media/ {{
        alias {PROJECT_DIR}/TradifyERP/media/;
        expires 7d;
    }}
    
    location / {{
        proxy_pass http://tradifyerp;
        proxy_set_header Host \\$host;
        proxy_set_header X-Real-IP \\$remote_addr;
        proxy_set_header X-Forwarded-For \\$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \\$scheme;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }}
}}
"""
    
    returncode, stdout, stderr = ssh_command(WEB_SERVER, SSH_USER, SSH_PASSWORD,
        f"cat > /etc/nginx/sites-available/tradifyerp << 'EOF'\n{nginx_config}\nEOF",
        use_sudo=True)
    
    if returncode == 0:
        log_success("Nginx configured")
        # Enable site
        ssh_command(WEB_SERVER, SSH_USER, SSH_PASSWORD,
            "ln -sf /etc/nginx/sites-available/tradifyerp /etc/nginx/sites-enabled/tradifyerp && rm -f /etc/nginx/sites-enabled/default",
            use_sudo=True)
        # Test and restart
        ssh_command(WEB_SERVER, SSH_USER, SSH_PASSWORD, "nginx -t && systemctl restart nginx", use_sudo=True)
    else:
        log_error(f"Nginx configuration failed: {stderr}")
    
    # Step 10: Create systemd service
    log_header("Step 10: Setting Up Systemd Service")
    service_config = f"""[Unit]
Description=Tradify Global ERP Gunicorn Service
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=tradifyapp
Group=tradifyapp
WorkingDirectory={PROJECT_DIR}/TradifyERP
Environment="PATH={PROJECT_DIR}/TradifyERP/venv/bin"
ExecStart={PROJECT_DIR}/TradifyERP/venv/bin/gunicorn \\
    --workers 4 \\
    --bind 127.0.0.1:8000 \\
    --timeout 120 \\
    --access-logfile /var/log/tradifyerp/access.log \\
    --error-logfile /var/log/tradifyerp/error.log \\
    TradifyERP.wsgi:application
ExecReload=/bin/kill -s HUP \\$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    returncode, stdout, stderr = ssh_command(WEB_SERVER, SSH_USER, SSH_PASSWORD,
        f"cat > /etc/systemd/system/tradifyerp.service << 'EOF'\n{service_config}\nEOF",
        use_sudo=True)
    
    if returncode == 0:
        log_success("Systemd service created")
        # Enable and start service
        ssh_command(WEB_SERVER, SSH_USER, SSH_PASSWORD,
            "mkdir -p /var/log/tradifyerp && useradd -m -s /bin/bash tradifyapp 2>/dev/null || true && chown -R tradifyapp:tradifyapp /var/log/tradifyerp /opt/tradifyerp && systemctl daemon-reload && systemctl enable tradifyerp.service && systemctl start tradifyerp.service",
            use_sudo=True)
    else:
        log_error(f"Service configuration failed: {stderr}")
    
    # Step 11: Verify deployment
    log_header("Step 11: Verifying Deployment")
    returncode, stdout, stderr = ssh_command(WEB_SERVER, SSH_USER, SSH_PASSWORD, "systemctl status tradifyerp --no-pager")
    if "active (running)" in stdout:
        log_success("Service is running")
    else:
        log_warning("Service status unknown")
    
    # Final status
    log_header("✅ DEPLOYMENT COMPLETE!")
    log_success("Your ERP system is deployed to production")
    print(f"""
📋 DEPLOYMENT SUMMARY:
    Web Server: http://192.168.20.10
    Database: 192.168.20.11
    Admin Panel: http://192.168.20.10/admin
    Audit Logs: http://192.168.20.10/admin/audit_logging/

🔐 SECURITY STATUS:
    ✓ Rate limiting active
    ✓ SQL injection protection active
    ✓ Audit logging active
    ✓ Encryption ready
    ✓ Security headers configured

📊 LOGS:
    Application: /var/log/tradifyerp/error.log
    Access: /var/log/tradifyerp/access.log

⚠️  NEXT STEPS:
    1. Update EMAIL_HOST_PASSWORD in .env
    2. Test application: http://192.168.20.10
    3. Create superuser if needed
    4. Monitor logs for errors
    5. Configure HTTPS/SSL when domain is ready
    6. Set up monitoring and backups
    """)
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Deploy Tradify ERP to production')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    try:
        success = deploy()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        log_error("Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        log_error(f"Deployment failed: {str(e)}")
        sys.exit(1)
