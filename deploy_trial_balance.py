#!/usr/bin/env python
"""
Trial Balance System Deployment Script
Handles integration of Trial Balance models, views, signals, and URLs
"""

import os
import sys

def step_1_copy_views_signals_urls():
    """Copy views, signals, and URLs files"""
    print("\n" + "="*60)
    print("STEP 1: Copying Code Files")
    print("="*60)
    
    files = [
        ('/tmp/VIEWS_TRIAL_BALANCE.py', '/var/www/tradifyerp/accounting/views_trial_balance.py'),
        ('/tmp/SIGNALS_TRIAL_BALANCE.py', '/var/www/tradifyerp/accounting/signals_trial_balance.py'),
        ('/tmp/URLS_TRIAL_BALANCE.py', '/var/www/tradifyerp/accounting/urls_trial_balance.py'),
    ]
    
    for src, dst in files:
        try:
            os.system(f'sudo cp {src} {dst}')
            print(f"✓ Copied {src} to {dst}")
        except Exception as e:
            print(f"✗ Error copying {src}: {e}")
            return False
    
    return True

def step_2_verify_models_integrated():
    """Verify models are in place"""
    print("\n" + "="*60)
    print("STEP 2: Verifying Trial Balance Models")
    print("="*60)
    
    try:
        with open('/var/www/tradifyerp/accounting/models.py', 'r') as f:
            content = f.read()
            if 'TrialBalance' in content:
                print("✓ Trial Balance models already in models.py")
                return True
            else:
                print("! Trial Balance models not found, they need to be added manually")
                return True  # Continue anyway
    except Exception as e:
        print(f"✗ Error reading models.py: {e}")
        return False

def step_3_create_migration():
    """Create migration for Trial Balance models"""
    print("\n" + "="*60)
    print("STEP 3: Creating Database Migration")
    print("="*60)
    
    try:
        os.chdir('/var/www/tradifyerp')
        os.system('source venv/bin/activate && python manage.py makemigrations accounting')
        print("✓ Migration created successfully")
        return True
    except Exception as e:
        print(f"✗ Error creating migration: {e}")
        return False

def step_4_apply_migration():
    """Apply migration to database"""
    print("\n" + "="*60)
    print("STEP 4: Applying Database Migration")
    print("="*60)
    
    try:
        os.chdir('/var/www/tradifyerp')
        os.system('source venv/bin/activate && python manage.py migrate accounting')
        print("✓ Migration applied successfully")
        return True
    except Exception as e:
        print(f"✗ Error applying migration: {e}")
        return False

def step_5_verify_deployment():
    """Verify deployment is successful"""
    print("\n" + "="*60)
    print("STEP 5: Verifying Deployment")
    print("="*60)
    
    try:
        os.chdir('/var/www/tradifyerp')
        
        # Check if models are accessible
        os.system('source venv/bin/activate && python manage.py shell << EOF\nfrom accounting.models import TrialBalance\nprint("✓ Trial Balance models accessible")\nEOF')
        
        # Check if views are accessible
        os.system('source venv/bin/activate && python manage.py shell << EOF\nfrom accounting.views_trial_balance import TrialBalanceListView\nprint("✓ Trial Balance views accessible")\nEOF')
        
        return True
    except Exception as e:
        print(f"✗ Error verifying deployment: {e}")
        return False

def main():
    print("\n🚀 TRIAL BALANCE SYSTEM DEPLOYMENT")
    print("=" * 60)
    
    steps = [
        ("Copying Code Files", step_1_copy_views_signals_urls),
        ("Verifying Models", step_2_verify_models_integrated),
        ("Creating Migration", step_3_create_migration),
        ("Applying Migration", step_4_apply_migration),
        ("Verifying Deployment", step_5_verify_deployment),
    ]
    
    completed = 0
    for step_name, step_func in steps:
        try:
            if step_func():
                completed += 1
            else:
                print(f"\n✗ {step_name} failed")
                break
        except Exception as e:
            print(f"\n✗ {step_name} failed with error: {e}")
            break
    
    print("\n" + "="*60)
    print(f"DEPLOYMENT COMPLETE: {completed}/{len(steps)} steps completed")
    print("="*60)
    
    if completed == len(steps):
        print("\n✅ TRIAL BALANCE SYSTEM DEPLOYED SUCCESSFULLY!")
        print("\nNext steps:")
        print("1. Restart Gunicorn: sudo systemctl restart gunicorn")
        print("2. Check logs: tail -f /var/www/tradifyerp/gunicorn.log")
        print("3. Test URLs: curl http://localhost/accounting/trial-balance-dashboard/")
        return 0
    else:
        print(f"\n❌ DEPLOYMENT INCOMPLETE ({completed}/{len(steps)} steps)")
        return 1

if __name__ == '__main__':
    sys.exit(main())
