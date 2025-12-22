"""
Simple Module GL Integration Test
Tests each module's GL posting by checking existing transactions
"""

import paramiko
from datetime import datetime

def test_module_integration(ssh):
    """Check if modules are posting to GL"""
    
    test_script = """
import os, sys, django
sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import LedgerEntry

print("="*80)
print("MODULE → ACCOUNTING INTEGRATION CHECK")
print("="*80)
print()

# Check Sales
inv_count = LedgerEntry.objects.filter(reference_number__startswith='INV-').count()
print(f"1. Sales Module (INV-):           {inv_count} GL entries")
if inv_count > 0:
    latest = LedgerEntry.objects.filter(reference_number__startswith='INV-').latest('id')
    print(f"   Latest: {latest.reference_number} on {latest.entry_date}")
    print(f"   ✅ INTEGRATED")
else:
    print(f"   ⚠️  No invoice GL entries found")

print()

# Check Manufacturing (uses LedgerEntry with MFG reference or check signals)
mfg_count = LedgerEntry.objects.filter(reference_number__startswith='MFG-').count()
print(f"2. Manufacturing (MFG-):          {mfg_count} GL entries")
if mfg_count > 0:
    latest = LedgerEntry.objects.filter(reference_number__startswith='MFG-').latest('id')
    print(f"   Latest: {latest.reference_number} on {latest.entry_date}")
    print(f"   ✅ INTEGRATED")
else:
    # Check if manufacturing uses different reference pattern
    from manufacturing.models import ProductionOrder
    po_count = ProductionOrder.objects.filter(status='COMPLETE').count()
    print(f"   ⚠️  No MFG- GL entries found")
    print(f"   Note: {po_count} completed production orders exist")
    print(f"   ❌ May need signal/GL integration setup")

print()

# Check Procurement  
po_count = LedgerEntry.objects.filter(reference_number__startswith='PO-').count()
gr_count = LedgerEntry.objects.filter(reference_number__startswith='GR-').count()
print(f"3. Procurement (PO-/GR-):         {po_count + gr_count} GL entries")
if po_count > 0 or gr_count > 0:
    print(f"   PO entries: {po_count}, GR entries: {gr_count}")
    print(f"   ✅ INTEGRATED")
else:
    print(f"   ⚠️  No procurement GL entries found")

print()

# Check Expenses
exp_count = LedgerEntry.objects.filter(reference_number__startswith='EXP-').count()
print(f"4. Expenses (EXP-):               {exp_count} GL entries")
if exp_count > 0:
    latest = LedgerEntry.objects.filter(reference_number__startswith='EXP-').latest('id')
    print(f"   Latest: {latest.reference_number} on {latest.entry_date}")
    print(f"   ✅ INTEGRATED")
else:
    print(f"   ⚠️  No expense GL entries found")

print()

# Check HR/Payroll
pay_count = LedgerEntry.objects.filter(reference_number__startswith='PAY-').count()
print(f"5. HR/Payroll (PAY-):             {pay_count} GL entries")
if pay_count > 0:
    latest = LedgerEntry.objects.filter(reference_number__startswith='PAY-').latest('id')
    print(f"   Latest: {latest.reference_number} on {latest.entry_date}")
    print(f"   ✅ INTEGRATED")
else:
    print(f"   ⚠️  No payroll GL entries found")

print()

# Check Maintenance
wo_count = LedgerEntry.objects.filter(reference_number__startswith='WO-').count()
print(f"6. Maintenance (WO-):             {wo_count} GL entries")
if wo_count > 0:
    latest = LedgerEntry.objects.filter(reference_number__startswith='WO-').latest('id')
    print(f"   Latest: {latest.reference_number} on {latest.entry_date}")
    print(f"   ✅ INTEGRATED")
else:
    print(f"   ❌ NOT INTEGRATED (as expected)")

print()
print("="*80)
print("INTEGRATION STATUS SUMMARY")
print("="*80)
print(f"✅ Sales:          {'YES' if inv_count > 0 else 'NO'}")
print(f"⚠️  Manufacturing:  {'YES' if mfg_count > 0 else 'NEEDS CHECK'}")
print(f"✅ Procurement:    {'YES' if (po_count + gr_count) > 0 else 'NO'}")
print(f"✅ Expenses:       {'YES' if exp_count > 0 else 'NO'}")
print(f"✅ HR/Payroll:     {'YES' if pay_count > 0 else 'NO'}")
print(f"❌ Maintenance:    {'YES' if wo_count > 0 else 'NO (needs implementation)'}")
print("="*80)
"""
    
    # Upload script
    sftp = ssh.open_sftp()
    script_path = '/tmp/check_gl_integration.py'
    with sftp.file(script_path, 'w') as f:
        f.write(test_script)
    sftp.close()
    
    # Execute
    stdin, stdout, stderr = ssh.exec_command(
        f'/var/www/tradifyerp/venv/bin/python {script_path}',
        timeout=60
    )
    
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    # Cleanup
    ssh.exec_command(f'rm {script_path}')
    
    return output, error

def main():
    host = '192.168.2.69'
    username = 'zubair'
    password = 'erp'
    
    print(f"🔍 Module → Accounting Integration Test")
    print(f"Server: {host}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Connect
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)
        
        # Run test
        output, error = test_module_integration(ssh)
        
        print(output)
        
        if error and ('Traceback' in error or 'Error' in error):
            print("\n⚠️ Errors encountered:")
            print(error)
        
        ssh.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
