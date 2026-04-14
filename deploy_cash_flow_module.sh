#!/bin/bash

# Cash Flow Statement Module - Deployment Script
# Automates installation, migration, and initial setup

set -e

echo "=========================================="
echo "Cash Flow Statement Module Deployment"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_DIR=${1:-/var/www/tradifyerp}
PYTHON_CMD="cd $PROJECT_DIR && python manage.py"

echo -e "${YELLOW}ℹ️  Using project directory: $PROJECT_DIR${NC}"
echo ""

# 1. Check project structure
echo -e "${YELLOW}[1/5] Checking project structure...${NC}"
if [ ! -f "$PROJECT_DIR/manage.py" ]; then
    echo -e "${RED}✗ Django project not found at $PROJECT_DIR${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Django project structure validated${NC}"
echo ""

# 2. Copy model and view files
echo -e "${YELLOW}[2/5] Copying module files...${NC}"
if [ -d "$PROJECT_DIR/TradifyERP/cash_management" ]; then
    cp cash_flow_models.py "$PROJECT_DIR/TradifyERP/cash_management/"
    cp cash_flow_views.py "$PROJECT_DIR/TradifyERP/cash_management/"
    echo -e "${GREEN}✓ Models and views copied${NC}"
else
    echo -e "${RED}✗ cash_management app not found${NC}"
    exit 1
fi
echo ""

# 3. Copy template files
echo -e "${YELLOW}[3/5] Installing templates...${NC}"
TEMPLATE_DIR="$PROJECT_DIR/TradifyERP/templates/cash_management"
mkdir -p "$TEMPLATE_DIR"
cp cash_flow_statements_list.html "$TEMPLATE_DIR/"
cp cash_flow_statement_detail.html "$TEMPLATE_DIR/"
cp cash_flow_generate.html "$TEMPLATE_DIR/"
cp cash_flow_variance_analysis.html "$TEMPLATE_DIR/"
cp cash_flow_comparison.html "$TEMPLATE_DIR/"
echo -e "${GREEN}✓ 5 templates installed${NC}"
echo ""

# 4. Run migrations
echo -e "${YELLOW}[4/5] Running database migrations...${NC}"
(cd "$PROJECT_DIR" && python manage.py makemigrations cash_management && 
 python manage.py migrate cash_management)
echo -e "${GREEN}✓ Database migrations completed${NC}"
echo ""

# 5. Load initial categories
echo -e "${YELLOW}[5/5] Initializing default categories...${NC}"
cat > /tmp/load_categories.py << 'EOF'
from cash_management.cash_flow_models import CashFlowCategory

# Operating Activities
CashFlowCategory.objects.get_or_create(
    name="Collections from Customers",
    defaults={
        "activity_type": "OPERATING",
        "description": "Cash received from customer invoices",
        "account_patterns": "200,201,202,203",
        "is_inflow": True
    }
)

CashFlowCategory.objects.get_or_create(
    name="Payments to Suppliers", 
    defaults={
        "activity_type": "OPERATING",
        "description": "Cash paid to vendors for bills",
        "account_patterns": "300,301,302,303",
        "is_inflow": False
    }
)

CashFlowCategory.objects.get_or_create(
    name="Payroll Payments",
    defaults={
        "activity_type": "OPERATING",
        "description": "Employee salaries and payroll deductions",
        "account_patterns": "500,501,502",
        "is_inflow": False
    }
)

# Investing Activities
CashFlowCategory.objects.get_or_create(
    name="Asset Purchases",
    defaults={
        "activity_type": "INVESTING",
        "description": "Capital expenditures on fixed assets",
        "account_patterns": "1000,1100,1200,1300",
        "is_inflow": False
    }
)

CashFlowCategory.objects.get_or_create(
    name="Asset Sales",
    defaults={
        "activity_type": "INVESTING",
        "description": "Proceeds from sale of assets",
        "account_patterns": "1000,1100,1200,1300",
        "is_inflow": True
    }
)

CashFlowCategory.objects.get_or_create(
    name="Investment Purchases",
    defaults={
        "activity_type": "INVESTING",
        "description": "Purchases of securities and investments",
        "account_patterns": "1400,1500",
        "is_inflow": False
    }
)

# Financing Activities
CashFlowCategory.objects.get_or_create(
    name="Loan Proceeds",
    defaults={
        "activity_type": "FINANCING",
        "description": "New borrowing from financial institutions",
        "account_patterns": "2100,2101,2102",
        "is_inflow": True
    }
)

CashFlowCategory.objects.get_or_create(
    name="Loan Repayments",
    defaults={
        "activity_type": "FINANCING",
        "description": "Repayment of principal on loans",
        "account_patterns": "2100,2101,2102",
        "is_inflow": False
    }
)

CashFlowCategory.objects.get_or_create(
    name="Dividend Payments",
    defaults={
        "activity_type": "FINANCING",
        "description": "Cash dividends paid to shareholders",
        "account_patterns": "3100,3101",
        "is_inflow": False
    }
)

CashFlowCategory.objects.get_or_create(
    name="Capital Contributions",
    defaults={
        "activity_type": "FINANCING",
        "description": "New equity capital invested by owners",
        "account_patterns": "3000,3001",
        "is_inflow": True
    }
)

print("✓ Default categories loaded successfully")
EOF

(cd "$PROJECT_DIR" && python manage.py shell < /tmp/load_categories.py)
rm /tmp/load_categories.py
echo -e "${GREEN}✓ Initial categories loaded${NC}"
echo ""

# Success message
echo -e "${GREEN}=========================================="
echo "✓ Deployment Complete!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Add URL patterns to cash_management/urls.py"
echo "   (See CASH_FLOW_STATEMENT_MODULE_GUIDE.md)"
echo ""
echo "2. Test module access:"
echo "   http://192.168.20.10/cash/statements/"
echo ""
echo "3. Generate first statement:"
echo "   http://192.168.20.10/cash/statements/generate/"
echo ""
echo "4. Review documentation:"
echo "   CASH_FLOW_STATEMENT_MODULE_GUIDE.md"
echo ""

exit 0
