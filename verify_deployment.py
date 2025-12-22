#!/usr/bin/env python3
"""Verify ShareholderInvestmentRegister deployment"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
sys.path.insert(0, '/var/www/tradifyerp')
sys.path.insert(0, '/var/www/tradifyerp/TradifyERP')

django.setup()

from django.db import connection
from accounting.models import ShareholderInvestmentRegister, ShareholderInvestmentSummary

print("=" * 70)
print("DEPLOYMENT VERIFICATION")
print("=" * 70)
print()

# Test 1: Check models exist
print("[Test 1] Checking models...")
print(f"✓ ShareholderInvestmentRegister model exists")
print(f"✓ ShareholderInvestmentSummary model exists")
print()

# Test 2: Check database tables
print("[Test 2] Checking database tables...")
cursor = connection.cursor()
cursor.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name LIKE 'accounting_shareholder%'
    ORDER BY table_name
""")
tables = [row[0] for row in cursor.fetchall()]

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"✓ {table}: {count} records")

print()

# Test 3: Check views are importable
print("[Test 3] Checking views...")
try:
    from accounting.views_reports import (
        ShareholderInvestmentRegisterListView,
        ShareholderInvestmentReportView,
        ShareholderCapitalStatusView,
        ShareholderInvestmentDetailView,
        ShareholderInvestmentAuditTrailView,
    )
    print("✓ ShareholderInvestmentRegisterListView")
    print("✓ ShareholderInvestmentReportView")
    print("✓ ShareholderCapitalStatusView")
    print("✓ ShareholderInvestmentDetailView")
    print("✓ ShareholderInvestmentAuditTrailView")
except ImportError as e:
    print(f"✗ Error importing views: {e}")

print()

# Test 4: Check signals are loaded
print("[Test 4] Checking signals...")
try:
    from accounting import signals
    print("✓ Signals module imported successfully")
    # Check for specific signal handlers
    import inspect
    for name, obj in inspect.getmembers(signals):
        if 'investment' in name.lower():
            print(f"✓ Found signal handler: {name}")
except ImportError as e:
    print(f"✗ Error importing signals: {e}")

print()

# Test 5: Check URLs are registered
print("[Test 5] Checking URL configuration...")
try:
    from accounting import urls
    print("✓ URLs module imported")
    # Check for shareholder investment paths
    url_file = '/var/www/tradifyerp/accounting/urls.py'
    with open(url_file, 'r') as f:
        content = f.read()
    
    if 'shareholder-investment' in content:
        print("✓ Shareholder investment URLs registered")
        count = content.count('shareholder-investment')
        print(f"  Found {count} URL patterns")
    else:
        print("✗ Shareholder investment URLs not found")
except Exception as e:
    print(f"✗ Error checking URLs: {e}")

print()

# Test 6: Check template exists
print("[Test 6] Checking templates...")
template_path = '/var/www/tradifyerp/accounting/templates/accounting/shareholder_investment_report.html'
if os.path.exists(template_path):
    size = os.path.getsize(template_path)
    print(f"✓ Template found: shareholder_investment_report.html ({size} bytes)")
else:
    print("✗ Template not found")

print()

# Test 7: Check permissions
print("[Test 7] Checking permissions...")
try:
    from django.contrib.auth.models import Permission
    perms = Permission.objects.filter(codename='view_sharehoiderinvestmentregister')
    if perms.exists():
        print(f"✓ Permission 'view_sharehoiderinvestmentregister' exists")
    else:
        print("ℹ Permission not yet created (will be created on first access)")
except Exception as e:
    print(f"✗ Error checking permissions: {e}")

print()
print("=" * 70)
print("✓ DEPLOYMENT VERIFICATION COMPLETE")
print("=" * 70)
print()
print("Next steps:")
print("1. Login to Django admin")
print("2. Create a test Cash Receipt")
print("3. Approve it (status → APPROVED)")
print("4. Authorize it (status → AUTHORIZED)")
print("5. Check ShareholderInvestmentRegister for new entry")
print("6. Access reports: /accounting/shareholder-investment-report/")
