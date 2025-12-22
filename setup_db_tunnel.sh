#!/bin/bash
# Setup PostgreSQL access through SSH tunnel
# Run this on the app server to enable secure remote database access

# Create SSH tunnel in background (forward local port 5432 to remote PostgreSQL)
echo "Creating SSH tunnel to database server..."
ssh -L 127.0.0.1:5432:127.0.0.1:5432 zubair@192.168.20.11 -N -f

# Wait for tunnel to establish
sleep 2

# Verify tunnel is active
if ss -tlnp | grep -q ":5432"; then
    echo "✅ SSH tunnel established successfully"
    echo "PostgreSQL is now accessible at localhost:5432"
else
    echo "⚠️  SSH tunnel may not be fully established yet"
fi
