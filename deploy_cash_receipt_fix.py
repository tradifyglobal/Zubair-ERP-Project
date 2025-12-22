#!/usr/bin/env python3
"""
Deploy cash receipt stakeholder field fix to production
"""
import subprocess
import sys
import paramiko
import os

def run_command(cmd, description=""):
    """Run a command and return output."""
    if description:
        print(f"\n{'='*60}")
        print(f"  {description}")
        print('='*60)
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"ERROR: {result.stderr}", file=sys.stderr)
    return result

def deploy_to_production():
    """Deploy the fix to production server."""
    
    print("🚀 Starting deployment of cash receipt fix...\n")
    
    # Define files to deploy
    files_to_deploy = [
        {
            'local': r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP\accounting\cash_forms.py',
            'remote': '/var/www/tradifyerp/accounting/cash_forms.py',
            'description': 'Updated cash forms with stakeholder field'
        },
        {
            'local': r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP\accounting\cash_workflow_views.py',
            'remote': '/var/www/tradifyerp/accounting/cash_workflow_views.py',
            'description': 'Cash workflow views (no changes needed)'
        },
    ]
    
    # Deploy each file
    for file_info in files_to_deploy:
        print(f"\n📦 Deploying: {file_info['description']}")
        print(f"   Local:  {file_info['local']}")
        print(f"   Remote: {file_info['remote']}")
        
        # Copy file to production
        cmd = f'scp "{file_info["local"]}" zubair@192.168.2.69:/tmp/deploy_{os.path.basename(file_info["remote"])}'
        result = run_command(cmd, f"Uploading {os.path.basename(file_info['remote'])}")
        
        if result.returncode != 0:
            print(f"❌ Failed to upload {file_info['remote']}")
            return False
        
        # Move to correct location on remote
        remote_cmd = f"sudo mv /tmp/deploy_{os.path.basename(file_info['remote'])} {file_info['remote']} && sudo chown www-data:www-data {file_info['remote']}"
        cmd = f'ssh zubair@192.168.2.69 "{remote_cmd}"'
        result = run_command(cmd, f"Moving {os.path.basename(file_info['remote'])} to production location")
        
        if result.returncode != 0:
            print(f"❌ Failed to move {file_info['remote']} to production")
            return False
        
        print(f"✅ Deployed {os.path.basename(file_info['remote'])}")
    
    # Restart Django
    print("\n🔄 Restarting Django application...")
    cmd = 'ssh zubair@192.168.2.69 "sudo systemctl restart gunicorn"'
    result = run_command(cmd, "Restarting gunicorn")
    
    if result.returncode != 0:
        print("❌ Failed to restart gunicorn")
        return False
    
    print("✅ Gunicorn restarted successfully")
    
    # Clear cache
    print("\n🧹 Clearing Django cache...")
    cmd = 'ssh zubair@192.168.2.69 "cd /var/www/tradifyerp && python manage.py shell -c \\"from django.core.cache import cache; cache.clear()\\""'
    run_command(cmd, "Clearing cache (non-critical)")
    
    print("\n" + "="*60)
    print("✅ DEPLOYMENT COMPLETE!")
    print("="*60)
    print("\n📋 Summary:")
    print("  ✓ Deployed updated cash_forms.py")
    print("  ✓ Restarted Django application")
    print("\n🎯 Changes made:")
    print("  • Added 'stakeholder' field to CashReceiptLineForm.fields")
    print("  • Added stakeholder widget configuration")
    print("  • Added stakeholder label")
    print("\n📝 Next steps:")
    print("  1. Test the cash receipt form in production")
    print("  2. Create a cash receipt with a stakeholder selected")
    print("  3. Authorize it and verify CapitalContribution is created")
    print("  4. Check the Shareholder report to see the investment")
    
    return True

if __name__ == '__main__':
    success = deploy_to_production()
    sys.exit(0 if success else 1)
