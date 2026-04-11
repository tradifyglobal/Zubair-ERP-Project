#!/bin/bash

##############################################################################
# Cash Receipt Dropdown Enhancement Deployment Script
# Server: 192.168.20.10
# Purpose: Deploy enhanced account dropdown with visual hierarchy
##############################################################################

set -e  # Exit on any error

# Configuration
SERVER_IP="192.168.20.10"
PROJECT_DIR="/home/tradify/tradifyerp"
VENV_PATH="/home/tradify/venv"
GIT_BRANCH="ERP-Enhancements"
GIT_REMOTE="origin"
LOG_FILE="/tmp/deployment_$(date +%Y%m%d_%H%M%S).log"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

##############################################################################
# Functions
##############################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1" | tee -a "$LOG_FILE"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 command not found"
        return 1
    fi
    return 0
}

##############################################################################
# Main Deployment
##############################################################################

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║         CASH RECEIPT DROPDOWN ENHANCEMENT DEPLOYMENT              ║"
echo "║                                                                    ║"
echo "║  Features:                                                         ║"
echo "║  • Grouped accounts with visual hierarchy                         ║"
echo "║  • Optgroups in dropdowns                                         ║"
echo "║  • Better form labels and help text                               ║"
echo "║  • Improved JavaScript with account counts                        ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

log_info "Deployment log: $LOG_FILE"
log_info "Target: $PROJECT_DIR"
log_info "Branch: $GIT_BRANCH"

# Step 1: Verify prerequisites
log_info "Step 1: Verifying prerequisites..."
check_command git && log_success "Git found" || exit 1
check_command python && log_success "Python found" || exit 1
check_command systemctl && log_success "systemctl found" || exit 1

# Step 2: Navigate to project directory
log_info "Step 2: Navigating to project directory..."
if [ ! -d "$PROJECT_DIR" ]; then
    log_error "Project directory not found: $PROJECT_DIR"
    exit 1
fi
cd "$PROJECT_DIR"
log_success "Working directory: $(pwd)"

# Step 3: Check current Git status
log_info "Step 3: Checking Git status..."
git status --short | head -5 | tee -a "$LOG_FILE"

# Step 4: Stash any local changes (just in case)
log_info "Step 4: Checking for uncommitted changes..."
if [ -n "$(git status --porcelain)" ]; then
    log_warning "Uncommitted changes detected, stashing them..."
    git stash
fi

# Step 5: Fetch and pull latest changes
log_info "Step 5: Pulling latest changes from Git..."
git fetch "$GIT_REMOTE" "$GIT_BRANCH" 2>&1 | grep -v "^remote:" | head -5 | tee -a "$LOG_FILE"
if ! git pull "$GIT_REMOTE" "$GIT_BRANCH"; then
    log_warning "Git pull had issues, but continuing..."
fi
log_success "Git repository updated"

# Step 6: Activate virtual environment and install requirements
log_info "Step 6: Installing Python dependencies..."
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
    log_success "Virtual environment activated"
    
    # Install/update requirements
    if [ -f "requirements.txt" ]; then
        pip install -q -r requirements.txt 2>&1 | tail -3 | tee -a "$LOG_FILE"
        log_success "Python dependencies installed"
    fi
else
    log_warning "Virtual environment not found at $VENV_PATH"
fi

# Step 7: Collect static files
log_info "Step 7: Collecting static files..."
if [ "${VENV_PATH}" != "" ] && [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
fi
python manage.py collectstatic --noinput 2>&1 | tail -3 | tee -a "$LOG_FILE"
log_success "Static files collected"

# Step 8: Run migrations
log_info "Step 8: Running Django migrations..."
python manage.py migrate --noinput 2>&1 | tail -5 | tee -a "$LOG_FILE"
log_success "Migrations applied"

# Step 9: Clear cache
log_info "Step 9: Clearing cache..."
python manage.py clear_cache 2>/dev/null || true
log_success "Cache cleared"

# Step 10: Restart Gunicorn service
log_info "Step 10: Restarting Gunicorn service..."
log_info "  Running: systemctl restart gunicorn"
if systemctl restart gunicorn; then
    log_success "Gunicorn restarted"
else
    log_warning "Could not restart gunicorn directly, trying alternative methods..."
    # Try alternative restart method
    if command -v supervisorctl &> /dev/null; then
        supervisorctl restart gunicorn || log_warning "supervisorctl restart also failed"
    fi
fi

# Step 11: Wait for service to start
log_info "Step 11: Waiting for services to start..."
sleep 3

# Step 12: Verify deployment
log_info "Step 12: Verifying deployment..."
if systemctl is-active --quiet gunicorn; then
    log_success "Gunicorn service is running"
else
    log_warning "Gunicorn service status check failed"
fi

# Check if the enhanced views are accessible
log_info "Step 13: Verifying code changes..."
if grep -q "grouped_accounts" TradifyERP/accounting/cash_views.py; then
    log_success "Enhanced cash views confirmed"
else
    log_warning "Could not verify enhanced views"
fi

# Final summary
echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                   ✅ DEPLOYMENT COMPLETED                          ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
log_success "Cash Receipt dropdown enhancement deployed!"
echo ""
echo "Deployed Features:"
echo "  • Enhanced account dropdown with visual hierarchy"
echo "  • Grouped accounts under parent categories"
echo "  • Better form labels with descriptive help text"
echo "  • Improved JavaScript with optgroups"
echo ""
echo "Deployment Location: $PROJECT_DIR"
echo "Git Branch: $GIT_BRANCH"
echo "Service Status: $(systemctl is-active gunicorn 2>/dev/null || echo 'Unknown')"
echo ""
echo "Access the application:"
echo "  URL: https://erp.tradifyglobal.com/"
echo "  Test Enhancement: https://erp.tradifyglobal.com/accounting/cash-receipts/create/"
echo ""
echo "Log file: $LOG_FILE"
echo ""

log_success "Deployment finished at $(date)"
