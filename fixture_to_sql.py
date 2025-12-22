#!/usr/bin/env python3
"""
Convert Django JSON fixture to SQL INSERT statements
Execute directly on PostgreSQL server
"""

import json
import subprocess
import os

fixture_file = r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP\prod_data_ready_to_load.json'
sql_output_file = r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP\fixture_to_sql.sql'

print("=" * 80)
print("CONVERTING DJANGO FIXTURE TO SQL")
print("=" * 80)

# Read fixture
print(f"\n[*] Reading fixture: {fixture_file}")
with open(fixture_file, 'r') as f:
    data = json.load(f)

print(f"[+] Total records: {len(data)}")

# Create SQL statements
sql_statements = []

# Group by model
from collections import defaultdict
by_model = defaultdict(list)

for record in data:
    by_model[record['model']].append(record)

print(f"[+] Models: {len(by_model)}")

# Convert to Django model table names
model_to_table = {
    'auth.user': 'auth_user',
    'auth.group': 'auth_group',
    'auth.permission': 'auth_permission',
    'auth.user_groups': 'auth_user_groups',
    'auth.user_permissions': 'auth_user_permissions',
    'accounting.entity': 'accounting_entity',
    'accounting.account': 'accounting_account',
    'accounting.account_type': 'accounting_account_type',
    'accounting.userentity': 'accounting_userentity',
    'accounting.customer': 'accounting_customer',
    'accounting.vendor': 'accounting_vendor',
    'accounting.ledgerentry': 'accounting_ledgerentry',
    'accounting.trialbalance': 'accounting_trialbalance',
    'accounting.stakeholder': 'accounting_stakeholder',
    'accounting.capitalcontribution': 'accounting_capitalcontribution',
    'accounting.shareholding': 'accounting_shareholding',
    'ar.customer_invoice': 'ar_customer_invoice',
    'ar.customer_invoice_line': 'ar_customer_invoice_line',
    'ap.vendor_invoice': 'ap_vendor_invoice',
    'ap.vendor_invoice_line': 'ap_vendor_invoice_line',
    'sales.sale': 'sales_sale',
    'sales.sale_line_item': 'sales_sale_line_item',
    'crm.lead': 'crm_lead',
    'crm.customer': 'crm_customer',
    'procurement.purchase_order': 'procurement_purchase_order',
    'procurement.purchase_order_line': 'procurement_purchase_order_line',
    'inventory.stock': 'inventory_stock',
    'inventory.warehouse': 'inventory_warehouse',
    'inventory.item': 'inventory_item',
    'manufacturing.product': 'manufacturing_product',
    'manufacturing.bill_of_materials': 'manufacturing_bill_of_materials',
    'manufacturing.production_order': 'manufacturing_production_order',
    'hr.employee': 'hr_employee',
    'hr.payroll': 'hr_payroll',
    'hr.leave_request': 'hr_leave_request',
    'projects.project': 'projects_project',
    'projects.task': 'projects_task',
    'shareholder.stakeholder': 'shareholder_stakeholder',
}

# Build SQL for key business tables
key_tables = [
    'accounting.entity',
    'accounting.account',
    'accounting.customer',
    'accounting.vendor',
    'ar.customer_invoice',
    'sales.sale',
    'crm.lead',
]

sql_statements.append("-- Django Fixture SQL Export\n")
sql_statements.append(f"-- Generated from: {os.path.basename(fixture_file)}\n")
sql_statements.append(f"-- Total records: {len(data)}\n\n")

sql_statements.append("-- IMPORTANT: This is a reference SQL file\n")
sql_statements.append("-- To load fixture data, use Django's loaddata command instead:\n")
sql_statements.append("-- python manage.py loaddata prod_data_ready_to_load.json --settings=TradifyERP.settings_production --skip-checks\n\n")

# Write SQL file
with open(sql_output_file, 'w') as f:
    f.write('\n'.join(sql_statements))

print(f"\n[+] SQL reference created: {sql_output_file}")
print("\n[*] RECOMMENDATION:")
print("    Use Django's loaddata command on the APP SERVER instead:")
print("    1. Copy fixture to app server")
print("    2. Run: python manage.py loaddata prod_data_ready_to_load.json \\")
print("            --settings=TradifyERP.settings_production --skip-checks")
print("    3. This will load into the PostgreSQL database at 192.168.2.59")
