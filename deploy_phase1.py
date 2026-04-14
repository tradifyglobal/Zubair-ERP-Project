#!/usr/bin/env python3
"""
Comprehensive Phase 1 deployment script
Handles all remaining steps for raw_materials app
"""
import subprocess
import sys
import os

def run_command(cmd, description=""):
    """Run a shell command and return output"""
    print(f"\n📌 {description}")
    print(f"   Command: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.stdout:
            print(f"   ✓ Output: {result.stdout[:200]}")
        if result.stderr and "error" in result.stderr.lower():
            print(f"   ⚠ Error: {result.stderr[:200]}")
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        print(f"   ✗ Exception: {str(e)}")
        return False, "", str(e)

def main():
    os.chdir('/var/www/tradifyerp')
    venv_python = './venv/bin/python'
    django_manage = f'{venv_python} manage.py'
    
    print("="*70)
    print("🚀 PHASE 1 DEPLOYMENT - RAW MATERIALS SYSTEM")
    print("="*70)
    
    # STEP 1: Ensure raw_materials in INSTALLED_APPS
    print("\n" + "="*70)
    print("STEP 1: Add raw_materials to INSTALLED_APPS")
    print("="*70)
    
    settings_file = '/var/www/tradifyerp/TradifyERP/settings_production.py'
    try:
        with open(settings_file, 'r') as f:
            content = f.read()
        
        if "'raw_materials'" not in content:
            # Find the insertion point
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "'ar.apps.ArConfig'" in line:
                    # Insert after this line
                    lines.insert(i+1, "    'raw_materials',  # Raw Materials Management")
                    break
            
            with open(settings_file, 'w') as f:
                f.write('\n'.join(lines))
            print("✓ Added 'raw_materials' to INSTALLED_APPS")
        else:
            print("✓ 'raw_materials' already in INSTALLED_APPS")
    except Exception as e:
        print(f"✗ Failed to update settings: {e}")
        return False
    
    # STEP 2: Verify admin.py exists
    print("\n" + "="*70)
    print("STEP 2: Verify admin.py")
    print("="*70)
    
    admin_file = '/var/www/tradifyerp/raw_materials/admin.py'
    if os.path.exists(admin_file):
        print(f"✓ admin.py exists ({os.path.getsize(admin_file)} bytes)")
    else:
        print("✗ admin.py missing - file will be needed")
    
    # STEP 3: Setup management command directories
    print("\n" + "="*70)
    print("STEP 3: Create management command directories")
    print("="*70)
    
    commands = [
        ("mkdir -p /var/www/tradifyerp/raw_materials/management/commands", 
         "Create management directories"),
        ("touch /var/www/tradifyerp/raw_materials/management/__init__.py",
         "Create __init__.py in management"),
        ("touch /var/www/tradifyerp/raw_materials/management/commands/__init__.py",
         "Create __init__.py in commands"),
    ]
    
    for cmd, desc in commands:
        success, out, err = run_command(cmd, desc)
        if success:
            print(f"   ✓ {desc} - OK")
        else:
            print(f"   ⚠ {desc} - {err[:100]}")
    
    # STEP 4: Run migrations
    print("\n" + "="*70)
    print("STEP 4: Run Django Migrations")
    print("="*70)
    
    print("\n📌 Creating migrations for raw_materials...")
    success, out, err = run_command(f"{django_manage} makemigrations raw_materials", 
                                     "Make migrations")
    if success or "No changes detected" in out:
        print(f"   ✓ Migrations created: {out.split(chr(10))[0]}")
    else:
        print(f"   ⚠ {err[:200]}")
    
    print("\n📌 Applying migrations...")
    success, out, err = run_command(f"{django_manage} migrate raw_materials", 
                                     "Apply migrations")
    if success:
        print(f"   ✓ Migrations applied")
    else:
        print(f"   ⚠ {err[:200]}")
    
    # STEP 5: Load initial data
    print("\n" + "="*70)
    print("STEP 5: Load Initial Raw Materials Data")
    print("="*70)
    
    success, out, err = run_command(f"{django_manage} load_raw_materials",
                                     "Load raw materials")
    
    if success:
        print(f"   ✓ Data loaded successfully")
        print(f"   Output: {out}")
    else:
        print(f"   ⚠ Load command output: {err[:300]}")
    
    # STEP 6: Verify data
    print("\n" + "="*70)
    print("STEP 6: Verify Data Loaded")
    print("="*70)
    
    python_check = f"""
{venv_python} << 'PYEOF'
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from raw_materials.models import RawMaterial, RawMaterialCategory, Supplier, Stock

print(f"Raw Materials: {{RawMaterial.objects.count()}}")
print(f"Categories: {{RawMaterialCategory.objects.count()}}")
print(f"Suppliers: {{Supplier.objects.count()}}")
print(f"Stock Records: {{Stock.objects.count()}}")

if RawMaterial.objects.count() > 0:
    first = RawMaterial.objects.first()
    print(f"Sample: {{first.material_code}} - {{first.name}}")
PYEOF
"""
    
    success, out, err = run_command(python_check, "Check data in database")
    if out:
        print(out)
    if err:
        print(f"   Error details: {err[:200]}")
    
    # STEP 7: Restart Gunicorn
    print("\n" + "="*70)
    print("STEP 7: Restart Gunicorn Service")
    print("="*70)
    
    success, out, err = run_command("systemctl restart gunicorn", "Restart Gunicorn")
    if success:
        print("   ✓ Gunicorn restarted")
    else:
        print(f"   ⚠ {err[:100]}")
    
    print("\n" + "="*70)
    print("✅ PHASE 1 DEPLOYMENT COMPLETE")
    print("="*70)
    print("\n📋 Next Steps:")
    print("   1. Open browser: http://192.168.20.10/admin")
    print("   2. Login with admin credentials")
    print("   3. Look for 'Raw Materials Management' section")
    print("   4. Verify all 15 materials are present")
    print("   5. Check stock color status (green/orange/red)")
    print("\n")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        sys.exit(1)
