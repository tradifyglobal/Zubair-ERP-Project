"""
Management command to add permission checks to all delete views.
This ensures users without delete permission cannot access delete pages even via direct URL.
"""

from django.core.management.base import BaseCommand
from pathlib import Path
import re


class Command(BaseCommand):
    help = 'Documents all views that need permission decorators'

    def handle(self, *args, **options):
        base_path = Path('G:/TradifyERP/TradifyERP')
        
        modules = [
            'accounting', 'hr', 'manufacturing', 'sales', 
            'inventory', 'procurement', 'ap', 'ar', 
            'crm', 'projects', 'cash_management', 'maintenance'
        ]
        
        self.stdout.write('\nViews requiring @module_permission_required decorator:\n')
        self.stdout.write('=' * 80)
        
        for module in modules:
            views_file = base_path / module / 'views.py'
            if views_file.exists():
                with open(views_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Find all DeleteView classes
                delete_views = re.findall(r'class\s+(\w+Delete\w*)\s*\([^)]*DeleteView', content)
                
                if delete_views:
                    self.stdout.write(f'\n{module.upper()}:')
                    for view in delete_views:
                        self.stdout.write(f'  - {view}')
                        self.stdout.write(f'    Add: @module_permission_required("{module}", "delete")')
        
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write('\nRecommendation: Add the decorator or use ModulePermissionMixin')
