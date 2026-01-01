#!/bin/bash
# Script to start PostgreSQL on database server

echo "Starting PostgreSQL service..."
systemctl start postgresql
sleep 2

echo "Checking PostgreSQL status..."
systemctl status postgresql

echo "Checking if PostgreSQL is listening on port 5432..."
netstat -tlnp | grep 5432 || ss -tlnp | grep 5432 || echo "Port 5432 not found"

echo "PostgreSQL startup completed."
