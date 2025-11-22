"""
Management command to update all Add buttons to use permission_button tag.
This will show permission denied alerts instead of hiding buttons.
"""

from django.core.management.base import BaseCommand
import re
import os
import glob


class Command(BaseCommand):
    help = 'Update all Add buttons to use permission_button tag for better UX'

    def handle(self, *args, **options):
        # Module mapping
        modules = {
            'accounting': 'G:\\TradifyERP\\TradifyERP\\accounting\\templates\\accounting\\',
            'hr': 'G:\\TradifyERP\\TradifyERP\\hr\\templates\\hr\\',
            'manufacturing': 'G:\\TradifyERP\\TradifyERP\\manufacturing\\templates\\manufacturing\\',
            'sales': 'G:\\TradifyERP\\TradifyERP\\sales\\templates\\sales\\',
            'inventory': 'G:\\TradifyERP\\TradifyERP\\inventory\\templates\\inventory\\',
            'procurement': 'G:\\TradifyERP\\TradifyERP\\procurement\\templates\\procurement\\',
            'ap': 'G:\\TradifyERP\\TradifyERP\\ap\\templates\\ap\\',
            'ar': 'G:\\TradifyERP\\TradifyERP\\ar\\templates\\ar\\',
            'crm': 'G:\\TradifyERP\\TradifyERP\\crm\\templates\\crm\\',
            'projects': 'G:\\TradifyERP\\TradifyERP\\projects\\templates\\projects\\',
            'cash_management': 'G:\\TradifyERP\\TradifyERP\\cash_management\\templates\\cash_management\\',
            'maintenance': 'G:\\TradifyERP\\TradifyERP\\maintenance\\templates\\maintenance\\',
        }
        
        updated_count = 0
        
        for module_name, template_dir in modules.items():
            if not os.path.exists(template_dir):
                self.stdout.write(self.style.WARNING(f'Directory not found: {template_dir}'))
                continue
            
            # Find all *_list.html files
            list_files = glob.glob(os.path.join(template_dir, '*_list.html'))
            
            for filepath in list_files:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Pattern to match the if/else block with Add button
                # Example:
                # {% if user|has_action_permission:'module:add' %}
                # <a href="{% url 'module:create' %}" class="btn btn-success">
                #     <i class="..."></i> Add ...
                # </a>
                # {% else %}
                # <button ... disabled ...>
                # {% endif %}
                
                pattern = r'{%\s*if\s+user\|has_action_permission:\'([^:]+):add\'\s*%}[^{]*<a\s+href="{%\s*url\s+\'([^\']+)\'\s*%}"\s+class="([^"]*btn[^"]*)">[\s\S]*?<i\s+class="([^"]+)"><\/i>\s*([^<]+)<\/a>[^{]*{%\s*else\s*%}[\s\S]*?{%\s*endif\s*%}'
                
                def replace_button(match):
                    module = match.group(1)
                    url_name = match.group(2)
                    btn_class = match.group(3)
                    icon_class = match.group(4)
                    text = match.group(5).strip()
                    
                    return f"{{% permission_button user '{module}:add' '{url_name}' '{btn_class}' '{icon_class}' '{text}' %}}"
                
                content = re.sub(pattern, replace_button, content)
                
                # Only write if changed
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f'✓ Updated {os.path.basename(filepath)}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Updated {updated_count} templates with permission_button tag!'))
        self.stdout.write(self.style.SUCCESS('Users without add permission will now see an alert message.'))
