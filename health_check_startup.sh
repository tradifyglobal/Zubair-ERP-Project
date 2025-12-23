#!/bin/bash
# Post-Reboot Health Check Script
# Run this after server reboots to verify all services came up correctly

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="/var/log/erp_startup_health.log"

echo "[$TIMESTAMP] Starting ERP Health Check..." | sudo tee -a $LOG_FILE

check_database_server() {
    echo "[$TIMESTAMP] Checking Database Server..." | sudo tee -a $LOG_FILE
    
    # Check PostgreSQL service status
    PG_STATUS=$(systemctl is-active postgresql@16-main)
    if [ "$PG_STATUS" = "active" ]; then
        echo "  ✓ PostgreSQL@16-main: ACTIVE" | sudo tee -a $LOG_FILE
        
        # Check if port 5432 is listening
        if sudo ss -tlnp 2>/dev/null | grep -q :5432; then
            echo "  ✓ Port 5432: LISTENING" | sudo tee -a $LOG_FILE
            echo "  ✓ Database Server: OPERATIONAL" | sudo tee -a $LOG_FILE
            return 0
        else
            echo "  ✗ Port 5432: NOT LISTENING" | sudo tee -a $LOG_FILE
            return 1
        fi
    else
        echo "  ✗ PostgreSQL@16-main: INACTIVE ($PG_STATUS)" | sudo tee -a $LOG_FILE
        return 1
    fi
}

check_app_server() {
    echo "[$TIMESTAMP] Checking App Server..." | sudo tee -a $LOG_FILE
    
    # Check Gunicorn status
    GUNICORN_STATUS=$(systemctl is-active gunicorn)
    NGINX_STATUS=$(systemctl is-active nginx)
    
    if [ "$GUNICORN_STATUS" = "active" ]; then
        echo "  ✓ Gunicorn: ACTIVE" | sudo tee -a $LOG_FILE
    else
        echo "  ✗ Gunicorn: INACTIVE ($GUNICORN_STATUS)" | sudo tee -a $LOG_FILE
        return 1
    fi
    
    if [ "$NGINX_STATUS" = "active" ]; then
        echo "  ✓ Nginx: ACTIVE" | sudo tee -a $LOG_FILE
    else
        echo "  ✗ Nginx: INACTIVE ($NGINX_STATUS)" | sudo tee -a $LOG_FILE
        return 1
    fi
    
    # Check if Gunicorn is listening
    if ss -tlnp 2>/dev/null | grep -q :8000; then
        echo "  ✓ Gunicorn Port 8000: LISTENING" | sudo tee -a $LOG_FILE
    else
        echo "  ✗ Gunicorn Port 8000: NOT LISTENING" | sudo tee -a $LOG_FILE
        return 1
    fi
    
    # Check if Nginx is listening
    if ss -tlnp 2>/dev/null | grep -q :80; then
        echo "  ✓ Nginx Port 80: LISTENING" | sudo tee -a $LOG_FILE
    else
        echo "  ✗ Nginx Port 80: NOT LISTENING" | sudo tee -a $LOG_FILE
        return 1
    fi
    
    echo "  ✓ App Server: OPERATIONAL" | sudo tee -a $LOG_FILE
    return 0
}

check_connectivity() {
    echo "[$TIMESTAMP] Checking Database Connectivity..." | sudo tee -a $LOG_FILE
    
    # Try to connect from app to database
    if python3 -c "import psycopg2; conn = psycopg2.connect(host='192.168.20.11', port='5432', user='tradifyerp_user', password='Tradify@PostgreSQL2024', database='tradifyerp_db', connect_timeout=5); conn.close()" 2>/dev/null; then
        echo "  ✓ Django ↔ PostgreSQL: CONNECTED" | sudo tee -a $LOG_FILE
        return 0
    else
        echo "  ✗ Django ↔ PostgreSQL: CONNECTION FAILED" | sudo tee -a $LOG_FILE
        echo "    Note: May be normal during service startup (give 30-60 seconds)" | sudo tee -a $LOG_FILE
        return 1
    fi
}

# Run all checks
DB_OK=0
APP_OK=0
CONN_OK=0

check_database_server && DB_OK=1 || DB_OK=0
echo "" | sudo tee -a $LOG_FILE
check_app_server && APP_OK=1 || APP_OK=0
echo "" | sudo tee -a $LOG_FILE
check_connectivity && CONN_OK=1 || CONN_OK=0

echo "" | sudo tee -a $LOG_FILE
echo "[$TIMESTAMP] ════════════════════════════════════" | sudo tee -a $LOG_FILE

if [ $DB_OK -eq 1 ] && [ $APP_OK -eq 1 ] && [ $CONN_OK -eq 1 ]; then
    echo "[$TIMESTAMP] ✓ ALL SYSTEMS OPERATIONAL" | sudo tee -a $LOG_FILE
    echo "[$TIMESTAMP] ERP system is fully operational" | sudo tee -a $LOG_FILE
    exit 0
elif [ $DB_OK -eq 1 ] && [ $APP_OK -eq 1 ]; then
    echo "[$TIMESTAMP] ⚠ SYSTEMS UP - CONNECTIVITY STABILIZING" | sudo tee -a $LOG_FILE
    echo "[$TIMESTAMP] Services running but DB connection not yet ready (normal in startup)" | sudo tee -a $LOG_FILE
    exit 1
else
    echo "[$TIMESTAMP] ✗ SYSTEM ISSUES DETECTED" | sudo tee -a $LOG_FILE
    echo "[$TIMESTAMP] Check server logs for details" | sudo tee -a $LOG_FILE
    exit 2
fi
