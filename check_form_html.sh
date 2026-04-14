#!/bin/bash

# Create temp file
COOKIES="/tmp/csrf_test_cookies.txt"
rm -f $COOKIES
RESPONSE="/tmp/form_response.html"

# Get the form and save full response
curl -s -b $COOKIES -c $COOKIES "http://192.168.20.10/accounting/cash-payments/create/" > $RESPONSE 2>&1

# Check if we got HTML or error
if grep -q "form" $RESPONSE; then
    echo "✓ Form HTML found"
else
    echo "✗ No form found"
fi

# Check response size
SIZE=$(wc -c < $RESPONSE)
echo "Response size: $SIZE bytes"

# Look for key elements
echo "Checking for key elements:"
echo "- Form tag: $(grep -c '<form' $RESPONSE || echo '0')"
echo "- CSRF token: $(grep -c 'csrfmiddlewaretoken' $RESPONSE || echo '0')"  
echo "- Payment date field: $(grep -c 'id_date' $RESPONSE || echo '0')"
echo "- Submit button: $(grep -c 'type=\"submit\"' $RESPONSE || echo '0')"

# Show first 50 lines and last 50 lines
echo ""
echo "=== First 30 lines ==="
head -30 $RESPONSE

echo ""
echo "=== Last 30 lines ==="
tail -30 $RESPONSE
