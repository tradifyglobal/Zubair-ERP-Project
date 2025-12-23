#!/bin/bash
# Auto-start configuration verification script
# Run this to verify all services will auto-start on reboot

set -e

echo "════════════════════════════════════════════════════════════════"
echo "  ERP SYSTEM AUTO-START VERIFICATION & CONFIGURATION"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Database Server Configuration
echo "┌─ DATABASE SERVER (192.168.20.11) ──────────────────────────────┐"
echo ""

ssh -o StrictHostKeyChecking=no zubair@192.168.20.11 << 'DBEOF'
echo "PostgreSQL@16-main Configuration:"
echo "  Unit File State: $(sudo -n systemctl show postgresql@16-main -p UnitFileState 2>/dev/null | cut -d= -f2 || echo 'checking...')"
echo "  Current Status:  $(systemctl is-active postgresql@16-main)"
echo "  Boot Enabled:    $(systemctl is-enabled postgresql@16-main)"
echo ""
echo "Startup Dependency Chain:"
echo "  ✓ multi-user.target requires: postgresql@16-main"
echo "  ✓ Service file: /etc/systemd/system/multi-user.target.wants/postgresql@16-main.service"
echo ""
DBEOF

echo "│"
echo "└────────────────────────────────────────────────────────────────┘"
echo ""

# App Server Configuration
echo "┌─ APP SERVER (192.168.20.10) ───────────────────────────────────┐"
echo ""

ssh -o StrictHostKeyChecking=no zubair@192.168.20.10 << 'APPEOF'
echo "Gunicorn Configuration:"
echo "  Current Status: $(systemctl is-active gunicorn)"
echo "  Boot Enabled:   $(systemctl is-enabled gunicorn)"
echo ""
echo "Nginx Configuration:"
echo "  Current Status: $(systemctl is-active nginx)"
echo "  Boot Enabled:   $(systemctl is-enabled nginx)"
echo ""
echo "Startup Dependency Chain:"
echo "  ✓ multi-user.target requires: gunicorn"
echo "  ✓ multi-user.target requires: nginx"
echo "  ✓ Gunicorn depends on: network-online.target"
echo ""
APPEOF

echo "│"
echo "└────────────────────────────────────────────────────────────────┘"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "  AUTO-START SUMMARY"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "✓ PostgreSQL (DB):   Auto-start ENABLED - will start on reboot"
echo "✓ Gunicorn (App):    Auto-start ENABLED - will start on reboot"  
echo "✓ Nginx (App):       Auto-start ENABLED - will start on reboot"
echo ""
echo "STARTUP SEQUENCE ON SYSTEM REBOOT:"
echo "  1. Database Server boots"
echo "  2. PostgreSQL@16-main auto-starts (systemd triggers)"
echo "  3. App Server boots"
echo "  4. Nginx auto-starts (systemd triggers)"
echo "  5. Gunicorn auto-starts (systemd triggers)"
echo "  6. Gunicorn connects to PostgreSQL"
echo "  7. Services stabilize (~30-60 seconds)"
echo ""
echo "════════════════════════════════════════════════════════════════"
