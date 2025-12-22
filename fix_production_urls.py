#!/usr/bin/env python3
import re

# Read the production urls.py file
with open('/var/www/tradifyerp/accounting/urls.py', 'r') as f:
    content = f.read()

# Add the import if missing
if 'from .views_tm import TradingManufacturingAccountView' not in content:
    # Find the line with other imports from views
    content = re.sub(
        r'(from \.views import.*)',
        r'\1\nfrom .views_tm import TradingManufacturingAccountView',
        content
    )
    print("Added import for TradingManufacturingAccountView")

# Add the URL pattern if missing  
if 'trading-manufacturing' not in content:
    # Find the accounting-dashboard path and add our path after it
    content = re.sub(
        r"(path\('accounting-dashboard/', AccountingDashboardView\.as_view\(\), name='accounting_dashboard'\),)",
        r"\1\n    path('trading-manufacturing/', TradingManufacturingAccountView.as_view(), name='trading_manufacturing'),",
        content
    )
    print("Added URL pattern for trading-manufacturing")

# Write back
with open('/var/www/tradifyerp/accounting/urls.py', 'w') as f:
    f.write(content)

print("Production urls.py updated successfully!")
