"""
Management command to automatically add permission decorators to all DeleteView classes.
"""

from django.core.management.base import BaseCommand
import re
import os


class Command(BaseCommand):
    help = 'Add @module_permission_required decorators to all DeleteView classes'

    def handle(self, *args, **options):
        modules = {
            'manufacturing': 'G:\\TradifyERP\\TradifyERP\\manufacturing\\views.py',
            'sales': 'G:\\TradifyERP\\TradifyERP\\sales\\views.py',
            'maintenance': 'G:\\TradifyERP\\TradifyERP\\maintenance\\views.py',
        }
        
        for module_name, filepath in modules.items():
            if not os.path.exists(filepath):
                self.stdout.write(self.style.WARNING(f'File not found: {filepath}'))
                continue
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Check if the import already exists
            if 'from accounting.permission_utils import module_permission_required' not in content:
                # Add import after other imports (look for Django imports)
                import_pattern = r'(from django\.views\.generic import[^\n]+\n)'
                if re.search(import_pattern, content):
                    content = re.sub(
                        import_pattern,
                        r'\1from accounting.permission_utils import module_permission_required\n',
                        content,
                        count=1
                    )
                else:
                    # Add after the first import
                    first_import = re.search(r'(^from [^\n]+\n)', content, re.MULTILINE)
                    if first_import:
                        pos = first_import.end()
                        content = content[:pos] + 'from accounting.permission_utils import module_permission_required\n' + content[pos:]
            
            # Find all DeleteView classes and add decorator if not present
            delete_view_pattern = r'(^class\s+(\w+Delete\w*)\s*\([^)]*DeleteView[^)]*\):)'
            
            def add_decorator(match):
                full_match = match.group(0)
                class_name = match.group(2)
                
                # Look back to see if decorator already exists
                start_pos = match.start()
                # Get previous 200 characters to check for existing decorator
                context_before = content[max(0, start_pos - 200):start_pos]
                
                if f'@method_decorator(module_permission_required("{module_name}", "delete"), name=\'dispatch\')' in context_before:
                    # Decorator already exists
                    return full_match
                
                # Add decorator with method_decorator for CBVs
                return f'@method_decorator(module_permission_required("{module_name}", "delete"), name=\'dispatch\')\n{full_match}'
            
            content = re.sub(delete_view_pattern, add_decorator, content, flags=re.MULTILINE)
            
            # Only write if content changed
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.stdout.write(self.style.SUCCESS(f'✓ Updated {module_name}/views.py'))
            else:
                self.stdout.write(self.style.WARNING(f'- No changes needed for {module_name}/views.py'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ All delete views protected with permission decorators!'))
