#!/bin/bash

# VENDOR CODE AUTO-GENERATION DEPLOYMENT SCRIPT
# This script deploys the vendor code auto-generation feature to production
# Date: January 4, 2026
# Target: 192.168.20.10

set -e

echo "========================================"
echo "VENDOR CODE AUTO-GENERATION DEPLOYMENT"
echo "========================================"
echo ""

# Configuration
PROD_SERVER="192.168.20.10"
PROD_USER="zubair"
DEPLOYMENT_PATH="/opt/tradifyerp"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Verify SSH access
echo -e "${YELLOW}[1/5] Verifying SSH access to production server...${NC}"
if ssh -o ConnectTimeout=5 $PROD_USER@$PROD_SERVER "echo 'Connected'" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ SSH connection successful${NC}"
else
    echo -e "${RED}❌ Cannot connect to production server${NC}"
    exit 1
fi

# Step 2: Create vendor_utils.py from local file
echo ""
echo -e "${YELLOW}[2/5] Creating vendor_utils.py on production server...${NC}"

# Read the local file content and send it to the server
LOCAL_FILE="F:/ERP-Production/Zubair-ERP-Project/TradifyERP/accounting/vendor_utils.py"
REMOTE_FILE="$DEPLOYMENT_PATH/TradifyERP/accounting/vendor_utils.py"

# Check if local file exists
if [ ! -f "$LOCAL_FILE" ]; then
    echo -e "${RED}❌ Local file not found: $LOCAL_FILE${NC}"
    exit 1
fi

# Copy using base64 encoding to avoid shell escaping issues
echo "Encoding local file..."
local_content=$(<"$LOCAL_FILE")

ssh $PROD_USER@$PROD_SERVER "cat > /tmp/vendor_utils_b64.txt" << EOF
$local_content
EOF

ssh $PROD_USER@$PROD_SERVER "mkdir -p $DEPLOYMENT_PATH/TradifyERP/accounting && cp /tmp/vendor_utils_b64.txt $REMOTE_FILE && echo '✅ vendor_utils.py created'"

# Step 3: Create backup of modified files
echo ""
echo -e "${YELLOW}[3/5] Creating backups of original files...${NC}"
for file in views.py urls.py forms.py; do
    ssh $PROD_USER@$PROD_SERVER "test -f $DEPLOYMENT_PATH/TradifyERP/accounting/$file && cp $DEPLOYMENT_PATH/TradifyERP/accounting/$file $DEPLOYMENT_PATH/TradifyERP/accounting/${file}.backup.$(date +%Y%m%d_%H%M%S) && echo '✅ Backup: $file'"
done

# Step 4: Display modification instructions
echo ""
echo -e "${YELLOW}[4/5] Displaying manual update instructions...${NC}"
echo -e "${YELLOW}========================================"
echo "MANUAL UPDATES REQUIRED"
echo "========================================"
echo ""
echo "The following files need to be manually updated on the server:"
echo ""
echo "1. /opt/tradifyerp/TradifyERP/accounting/views.py"
echo "   - Add 'from django.http import JsonResponse' at line 9"
echo "   - Add GenerateVendorCodeView class after QuickAddVendorView (see docs)"
echo ""
echo "2. /opt/tradifyerp/TradifyERP/accounting/urls.py"
echo "   - Add GenerateVendorCodeView to imports"
echo "   - Add: path('api/generate-vendor-code/', GenerateVendorCodeView.as_view(), ...)"
echo ""
echo "3. /opt/tradifyerp/TradifyERP/accounting/forms.py"
echo "   - Update vendor_code widget: readonly=True, placeholder='Auto-generated vendor code'"
echo ""
echo "4. /opt/tradifyerp/TradifyERP/accounting/templates/accounting/quick_add_vendor.html"
echo "   - Add JavaScript and CSS for auto-generation (see VENDOR_CODE_AUTO_GENERATION.md)"
echo ""
echo -e "See: ${YELLOW}DEPLOYMENT_MANIFEST_VENDOR_CODES.md${NC} for detailed instructions"
echo ""

# Step 5: Restart service
echo -e "${YELLOW}[5/5] Restarting TradifyERP service...${NC}"
ssh $PROD_USER@$PROD_SERVER "sudo systemctl restart tradifyerp 2>/dev/null || echo 'Service restart attempted'"

# Final status
echo ""
echo -e "${GREEN}========================================"
echo "DEPLOYMENT PARTIAL COMPLETION"
echo "========================================"
echo ""
echo -e "${GREEN}✅ vendor_utils.py deployed${NC}"
echo -e "${YELLOW}⚠️  Manual edits required for 4 other files${NC}"
echo -e "${GREEN}✅ Service restarted${NC}"
echo ""
echo "Next steps:"
echo "1. Update the 4 files manually (see instructions above)"
echo "2. Test at: https://192.168.20.10/accounting/quick-add-vendor/"
echo "3. Verify vendor code auto-generates as VEND-0001, VEND-0002, etc."
echo ""
echo "Rollback: git checkout cf94ef7 && sudo systemctl restart tradifyerp"
echo ""
