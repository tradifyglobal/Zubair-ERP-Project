#!/usr/bin/env python
"""Check actual model fields on production server."""

import sys
import os

# SSH connection details
SERVER = "192.168.20.10"
USER = "zubair"
DJANGO_PATH = "/var/www/tradifyerp"

import paramiko

def check_model_fields():
    """Connect and check model fields."""
    print("=" * 80)
    print("CHECKING MODEL FIELDS ON PRODUCTION")
    print("=" * 80)
    print(f"Server: {SERVER}")
    print("=" * 80 + "\n")
    
    # Create SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect
        ssh.connect(SERVER, username=USER, password="erp")
        print("✅ Connected to server\n")
        
        # Check WorkOrder fields
        print("1. MAINTENANCE WorkOrder Fields")
        print("-" * 80)
        cmd = f'cd {DJANGO_PATH} && source venv/bin/activate && python manage.py shell -c "from maintenance.models import WorkOrder; import pprint; pprint.pprint([f.name for f in WorkOrder._meta.get_fields()])"'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if output:
            print(output)
        if error:
            print(f"Error: {error}")
        
        # Check Customer fields
        print("\n2. SALES Customer Fields")
        print("-" * 80)
        cmd = f'cd {DJANGO_PATH} && source venv/bin/activate && python manage.py shell -c "from sales.models import Customer; import pprint; pprint.pprint([f.name for f in Customer._meta.get_fields()])"'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if output:
            print(output)
        if error:
            print(f"Error: {error}")
        
        # Check Product fields
        print("\n3. MANUFACTURING Product Fields")
        print("-" * 80)
        cmd = f'cd {DJANGO_PATH} && source venv/bin/activate && python manage.py shell -c "from manufacturing.models import Product; import pprint; pprint.pprint([f.name for f in Product._meta.get_fields()])"'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if output:
            print(output)
        if error:
            print(f"Error: {error}")
        
        # Check Vendor fields
        print("\n4. ACCOUNTING Vendor Fields")
        print("-" * 80)
        cmd = f'cd {DJANGO_PATH} && source venv/bin/activate && python manage.py shell -c "from accounting.models import Vendor; import pprint; pprint.pprint([f.name for f in Vendor._meta.get_fields()])"'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if output:
            print(output)
        if error:
            print(f"Error: {error}")
        
        # Check ExpenseCategory fields
        print("\n5. EXPENSES ExpenseCategory Fields")
        print("-" * 80)
        cmd = f'cd {DJANGO_PATH} && source venv/bin/activate && python manage.py shell -c "from expenses.models import ExpenseCategory; import pprint; pprint.pprint([f.name for f in ExpenseCategory._meta.get_fields()])"'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if output:
            print(output)
        if error:
            print(f"Error: {error}")
        
        print("\n" + "=" * 80)
        print("✅ Field check completed")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    check_model_fields()
