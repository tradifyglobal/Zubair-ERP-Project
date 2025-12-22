#!/bin/bash

# PostgreSQL Setup Script for TradifyERP
# Database Server: 192.168.2.59
# Created: December 13, 2025

echo "=========================================="
echo "PostgreSQL Setup for TradifyERP"
echo "=========================================="

# Update system
echo "[1/5] Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install PostgreSQL 16
echo "[2/5] Installing PostgreSQL 16..."
sudo apt-get install -y postgresql postgresql-contrib postgresql-16
sudo apt-get install -y postgresql-client

# Start PostgreSQL service
echo "[3/5] Starting PostgreSQL service..."
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo systemctl status postgresql

# Create database and user
echo "[4/5] Creating database and user..."
sudo -u postgres psql << EOF
-- Create database
CREATE DATABASE tradify ENCODING 'UTF8';

-- Create user
CREATE USER zubair WITH PASSWORD 'zubair@0862';

-- Grant privileges
ALTER ROLE zubair SET client_encoding TO 'utf8';
ALTER ROLE zubair SET default_transaction_isolation TO 'read committed';
ALTER ROLE zubair SET default_transaction_deferrable TO on;
ALTER ROLE zubair SET default_transaction_level TO 'read committed';
ALTER ROLE zubair SET timezone TO 'UTC';

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE tradify TO zubair;
ALTER USER zubair CREATEDB;
ALTER USER zubair SUPERUSER;

-- Verify
\l
\du
EOF

# Configure PostgreSQL for remote connections
echo "[5/5] Configuring PostgreSQL for remote access..."

# Find PostgreSQL config directory
PG_VERSION=$(sudo -u postgres psql --version | awk '{print $3}' | cut -d. -f1)
PG_CONFIG="/etc/postgresql/${PG_VERSION}/main"

# Update postgresql.conf
echo "Updating postgresql.conf..."
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" ${PG_CONFIG}/postgresql.conf
sudo sed -i "s/max_connections = 100/max_connections = 200/g" ${PG_CONFIG}/postgresql.conf

# Update pg_hba.conf to allow remote connections
echo "Updating pg_hba.conf..."
sudo bash -c "cat >> ${PG_CONFIG}/pg_hba.conf << 'PGEOF'

# Allow connection from application server
host    tradify    zubair    192.168.2.69/32    md5
host    all        all       192.168.2.0/24     md5
PGEOF"

# Restart PostgreSQL to apply changes
echo "Restarting PostgreSQL..."
sudo systemctl restart postgresql
sudo systemctl status postgresql

# Verify connection
echo "=========================================="
echo "PostgreSQL Setup Complete!"
echo "=========================================="
echo ""
echo "Connection Details:"
echo "  Host: 192.168.2.59"
echo "  Port: 5432"
echo "  Database: tradify"
echo "  User: zubair"
echo "  Password: zubair@0862"
echo ""
echo "Test local connection:"
echo "  sudo -u postgres psql -d tradify"
echo ""
echo "Test remote connection from app server:"
echo "  psql -h 192.168.2.59 -U zubair -d tradify"
echo "=========================================="
