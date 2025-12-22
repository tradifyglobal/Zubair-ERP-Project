#!/usr/bin/env python
import os
import sys

# Add the project directory to the path
sys.path.insert(0, '/var/www/tradifyerp')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')

import django
django.setup()

from django.db import connection

# Check actual database columns
with connection.cursor() as cursor:
    # Get columns for cashreceiptline
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'accounting_cashreceiptline'
        ORDER BY column_name;
    """)
    columns = cursor.fetchall()
    
    print("\n" + "="*80)
    print("CASHRECEIPTLINE TABLE COLUMNS")
    print("="*80)
    
    relevant_cols = ['id', 'stakeholder_id', 'workflow_status', 'is_capital_contribution_posted']
    
    print(f"\n{'Column':<40} {'Data Type':<20}")
    print("-" * 60)
    
    col_names = [col[0] for col in columns]
    for col_name, dtype in columns:
        marker = " ← NEEDED" if col_name in relevant_cols else ""
        print(f"{col_name:<40} {dtype:<20} {marker}")
    
    print("\n" + "="*80)
    print("REQUIRED COLUMNS STATUS")
    print("="*80)
    for col in relevant_cols:
        status = "✓" if col in col_names else "✗"
        print(f"{status} {col}")
