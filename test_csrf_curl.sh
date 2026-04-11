#!/bin/bash
# Test CSRF form submission directly

# Create temp cookie file
COOKIES="/tmp/csrf_test_cookies.txt"
rm -f $COOKIES

# Step 1: GET the login page to start session
echo "=== Step 1: GET login page ==="
curl -s -c $COOKIES "http://192.168.20.10/accounts/login/?next=/accounting/cash-payments/create/" > /dev/null

# Step 2: Login
echo "=== Step 2: POST login ==="
curl -s -b $COOKIES -c $COOKIES \
  -X POST \
  -d "username=admin&password=admin123" \
  "http://192.168.20.10/accounts/login/" > /dev/null

# Step 3: Select entity
echo "=== Step 3: POST entity selection ==="
curl -s -b $COOKIES -c $COOKIES \
  -X POST \
  -d "entity_id=6" \
  "http://192.168.20.10/accounting/select-entity/" > /dev/null

# Step 4: GET the form to extract CSRF token
echo "=== Step 4: GET cash-payments form ==="
FORM_HTML=$(curl -s -b $COOKIES "http://192.168.20.10/accounting/cash-payments/create/")
CSRF_TOKEN=$(echo "$FORM_HTML" | grep -oP "'csrfmiddlewaretoken' value='\K[^']+")

if [ -z "$CSRF_TOKEN" ]; then
    echo "ERROR: CSRF token not found in form"
    echo "Searching for csrf in response..."
    echo "$FORM_HTML" | grep -i csrf | head -3
    exit 1
fi

echo "CSRF Token extracted: ${CSRF_TOKEN:0:20}..."

# Step 5: POST the payment form
echo "=== Step 5: POST cash payment ==="
curl -s -b $COOKIES -c $COOKIES \
  -X POST \
  -d "csrfmiddlewaretoken=$CSRF_TOKEN&date=2026-04-08&description=Test+Payment+from+curl&debit_amount=5000&credit_amount=5000" \
  "http://192.168.20.10/accounting/cash-payments/create/" \
  -i | head -20

echo -e "\n=== Done ==="
