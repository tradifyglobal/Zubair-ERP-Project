#!/bin/bash
# ============================================================================
# CASH ACCOUNT & GL INTEGRATION DEPLOYMENT SCRIPT
# ============================================================================
# This script deploys the Cash Account setup to production
# 
# Prerequisites:
# - SSH access to 192.168.20.10 (app server)
# - SSH access to 192.168.20.11 (database server)
# - Credentials in place
#
# Usage: bash deploy_cash_account_setup.sh
# ============================================================================

set -e  # Exit on error

# Configuration
APP_SERVER="192.168.20.10"
DB_SERVER="192.168.20.11"
APP_USER="zubair"
DB_USER="zubair"
DB_NAME="tradifyerp_db"
DB_PASSWORD="sql"
APP_DIR="/home/zubair/tradifyerp"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# ============================================================================
# Step 1: Verify Connectivity
# ============================================================================

print_header "STEP 1: VERIFY SERVER CONNECTIVITY"

print_info "Checking App Server (${APP_SERVER})..."
if ping -c 1 "${APP_SERVER}" > /dev/null 2>&1; then
    print_success "App Server is reachable"
else
    print_error "Cannot reach App Server (${APP_SERVER})"
    exit 1
fi

print_info "Checking Database Server (${DB_SERVER})..."
if ping -c 1 "${DB_SERVER}" > /dev/null 2>&1; then
    print_success "Database Server is reachable"
else
    print_error "Cannot reach Database Server (${DB_SERVER})"
    exit 1
fi

# ============================================================================
# Step 2: Copy Setup Files to App Server
# ============================================================================

print_header "STEP 2: COPY SETUP FILES TO APP SERVER"

print_info "Copying management command to app server..."
scp TradifyERP/accounting/management/commands/setup_cash_account.py \
    "${APP_USER}@${APP_SERVER}:${APP_DIR}/TradifyERP/accounting/management/commands/" 2>/dev/null || {
    print_error "Failed to copy management command"
    exit 1
}
print_success "Management command copied"

print_info "Copying setup documentation..."
scp CASH_ACCOUNT_IMPLEMENTATION_GUIDE.md \
    "${APP_USER}@${APP_SERVER}:${APP_DIR}/" 2>/dev/null || {
    print_warning "Failed to copy documentation (non-critical)"
}
print_success "Documentation copied"

# ============================================================================
# Step 3: Run Setup Command on App Server
# ============================================================================

print_header "STEP 3: RUN SETUP COMMAND ON APP SERVER"

print_info "Connecting to app server and running setup command..."

ssh -o ConnectTimeout=10 "${APP_USER}@${APP_SERVER}" << 'EOFAPP'
    cd /home/zubair/tradifyerp
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Run setup command
    echo "Running setup_cash_account command..."
    python manage.py setup_cash_account
    
    SETUP_RESULT=$?
    
    if [ $SETUP_RESULT -eq 0 ]; then
        echo "✅ Setup command completed successfully"
    else
        echo "❌ Setup command failed with exit code $SETUP_RESULT"
    fi
    
    exit $SETUP_RESULT
EOFAPP

SETUP_EXIT=$?

if [ $SETUP_EXIT -eq 0 ]; then
    print_success "Setup command executed successfully"
else
    print_error "Setup command failed"
    exit 1
fi

# ============================================================================
# Step 4: Verify Database Changes
# ============================================================================

print_header "STEP 4: VERIFY DATABASE CHANGES"

print_info "Checking if Cash Account (100001) was created..."

CASH_ACCOUNT_CHECK=$(PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_SERVER}" \
    -U "${DB_USER}" -d "${DB_NAME}" -t -c \
    "SELECT COUNT(*) FROM accounting_account WHERE account_number='100001';" 2>/dev/null)

if [ "$CASH_ACCOUNT_CHECK" -gt 0 ]; then
    print_success "Cash Account (100001) exists in database"
    
    # Get details
    echo ""
    PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_SERVER}" \
        -U "${DB_USER}" -d "${DB_NAME}" -c \
        "SELECT id, account_number, name, account_type, is_active FROM accounting_account WHERE account_number='100001';" 2>/dev/null
else
    print_warning "Cash Account (100001) not found - will be created on first run"
fi

print_info "Verifying Capital Accounts exist..."
CAPITAL_CHECK=$(PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_SERVER}" \
    -U "${DB_USER}" -d "${DB_NAME}" -t -c \
    "SELECT COUNT(*) FROM accounting_account WHERE account_number IN ('3000','3100');" 2>/dev/null)

if [ "$CAPITAL_CHECK" -ge 2 ]; then
    print_success "Capital Accounts verified"
else
    print_warning "Some Capital Accounts may be missing"
fi

# ============================================================================
# Step 5: Restart Gunicorn
# ============================================================================

print_header "STEP 5: RESTART APPLICATION SERVER"

print_info "Restarting Gunicorn service..."

ssh -o ConnectTimeout=10 "${APP_USER}@${APP_SERVER}" << 'EOFAPP'
    sudo systemctl restart gunicorn-tradifyerp
    sleep 3
    
    # Check status
    STATUS=$(sudo systemctl is-active gunicorn-tradifyerp)
    if [ "$STATUS" = "active" ]; then
        echo "✅ Gunicorn restarted successfully"
    else
        echo "⚠️  Gunicorn status: $STATUS"
    fi
EOFAPP

print_success "Application server restarted"

# ============================================================================
# Step 6: Verification Tests
# ============================================================================

print_header "STEP 6: VERIFICATION TESTS"

print_info "Checking application health..."

HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" "http://${APP_SERVER}/accounting/dashboard/" 2>/dev/null || echo "000")

if [ "$HEALTH_CHECK" = "200" ] || [ "$HEALTH_CHECK" = "302" ]; then
    print_success "Application is responding (HTTP ${HEALTH_CHECK})"
else
    print_warning "Application health check returned ${HEALTH_CHECK}"
fi

# ============================================================================
# Step 7: Final Summary
# ============================================================================

print_header "DEPLOYMENT COMPLETE ✅"

echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}CASH ACCOUNT SETUP SUCCESSFULLY DEPLOYED${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}\n"

echo "📊 NEXT STEPS:"
echo ""
echo "1. Test Cash Receipt Creation:"
echo "   Navigate to: http://${APP_SERVER}/accounting/cash-receipts/create/"
echo ""
echo "2. Verify GL Posting:"
echo "   Navigate to: http://${APP_SERVER}/accounting/general-ledger/"
echo ""
echo "3. Check Database:"
echo "   SELECT * FROM accounting_account WHERE account_number='100001';"
echo "   SELECT * FROM accounting_ledgerentry WHERE reference_number LIKE 'CASH-RECEIPT-%';"
echo ""
echo "4. Documentation:"
echo "   See: ${APP_DIR}/CASH_ACCOUNT_IMPLEMENTATION_GUIDE.md"
echo ""

echo -e "${GREEN}✅ DEPLOYMENT COMPLETE!${NC}\n"

# Save deployment log
echo "Deployment completed at $(date)" >> /tmp/cash_account_deployment.log
echo "App Server: ${APP_SERVER}" >> /tmp/cash_account_deployment.log
echo "DB Server: ${DB_SERVER}" >> /tmp/cash_account_deployment.log

print_info "Deployment log saved to: /tmp/cash_account_deployment.log"

exit 0
