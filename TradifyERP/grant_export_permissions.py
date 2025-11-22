"""
Grant export permissions to all users for testing import/export functionality.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounting.models import ModulePermission

User = get_user_model()

def grant_export_permissions():
    """Grant export and import permissions to all users."""
    
    modules = ['accounting', 'sales', 'hr', 'inventory', 'procurement', 
               'crm', 'manufacturing', 'cash', 'projects', 'ar', 'ap']
    
    users = User.objects.all()
    
    for user in users:
        print(f"\nGranting permissions to: {user.username}")
        
        for module in modules:
            # Get or create permission record
            permission, created = ModulePermission.objects.get_or_create(
                user=user,
                module=module,
                defaults={
                    'can_view': True,
                    'can_add': True,
                    'can_edit': True,
                    'can_delete': True,
                    'can_export': True,
                    'is_active': True,
                }
            )
            
            # Update existing permission to enable export
            if not created:
                permission.can_export = True
                permission.can_add = True  # Needed for import
                permission.can_view = True  # Needed for both
                permission.is_active = True
                permission.save()
                print(f"  ✓ Updated {module} - can_export=True, can_add=True")
            else:
                print(f"  ✓ Created {module} - Full permissions granted")
    
    print("\n✅ All permissions granted successfully!")
    print("\nYou can now:")
    print("  - Import data using the Import button")
    print("  - Download templates using the Template button")
    print("  - Export data in CSV, Excel, or JSON formats")

if __name__ == '__main__':
    grant_export_permissions()
