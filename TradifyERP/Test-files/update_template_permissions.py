"""
Script to batch update all list templates with permission checks for action buttons.
This adds permission checks for Add, Edit, Delete, and View buttons based on module permissions.
"""

import os
import re
from pathlib import Path

# Module mapping for permission checks
MODULE_MAPPING = {
    'accounting': 'accounting',
    'hr': 'hr',
    'manufacturing': 'manufacturing',
    'sales': 'sales',
    'inventory': 'inventory',
    'procurement': 'procurement',
    'ap': 'ap',
    'ar': 'ar',
    'crm': 'crm',
    'projects': 'projects',
    'cash_management': 'cash_management',
    'maintenance': 'maintenance',
    'shareholder': 'accounting',  # Shareholder uses accounting permissions
}

def get_module_from_path(file_path):
    """Extract module name from file path."""
    parts = Path(file_path).parts
    
    # Check if it's in TradifyERP/templates/module_name/
    if 'templates' in parts:
        template_idx = parts.index('templates')
        if template_idx + 1 < len(parts):
            module = parts[template_idx + 1]
            return MODULE_MAPPING.get(module, module)
    
    # Check if it's in module/templates/module_name/
    for module in MODULE_MAPPING.keys():
        if module in parts:
            return MODULE_MAPPING[module]
    
    return None

def add_permission_tags_load(content):
    """Add {% load permission_tags %} after {% load static %} if not already present."""
    if '{% load permission_tags %}' in content:
        return content
    
    # Add after {% load static %}
    pattern = r'({% load static %})'
    replacement = r'\1\n{% load permission_tags %}'
    content = re.sub(pattern, replacement, content, count=1)
    
    return content

def wrap_add_button(content, module):
    """Wrap Add buttons with permission checks."""
    
    # Pattern to match various Add button styles:
    # - btn-primary, btn-success, btn-info
    # - mdi mdi-plus, fas fa-plus, feather icons
    # - "Add New", "Add Customer", etc.
    add_pattern = r'(<a\s+href="{%\s*url [^}]+ %}"\s+class="btn (?:btn-primary|btn-success|btn-info)[^"]*"[^>]*>\s*(?:<i [^>]*(?:fa-plus|mdi-plus|feather="plus")[^>]*></i>\s*)?Add[^<]*</a>)'
    
    def replace_add(match):
        original = match.group(1)
        # Skip if already wrapped with permission check
        if '{%' in content[max(0, match.start() - 100):match.start()] and 'has_action_permission' in content[max(0, match.start() - 100):match.start()]:
            return original
        perm_check = "{{% if user|has_action_permission:'{0}:add' %}}".format(module)
        disabled_btn = """{% else %}
                            <button class="btn btn-secondary" disabled title="You do not have permission to add records">
                                <i class="mdi mdi-plus"></i> Add (No Permission)
                            </button>
                            {% endif %}"""
        return perm_check + "\n                            " + original + "\n                            " + disabled_btn
    
    content = re.sub(add_pattern, replace_add, content, flags=re.IGNORECASE | re.DOTALL)
    
    return content

def wrap_action_buttons(content, module):
    """Wrap Edit and Delete buttons in table rows with permission checks."""
    
    # Pattern for action button groups in tables
    # Look for btn-warning (edit) and btn-danger (delete) buttons
    
    # Edit button pattern
    edit_pattern = r'(<a\s+href="{%\s*url [^}]+ [^}]+ %}"\s+class="btn btn-sm btn-warning"[^>]*title="Edit"[^>]*>\s*<i class="mdi mdi-pencil"></i>\s*</a>)'
    
    def replace_edit(match):
        original = match.group(1)
        perm_check = "{{% if user|has_action_permission:'{0}:edit' %}}".format(module)
        else_part = """{% else %}
                                                    <button class="btn btn-sm btn-secondary" disabled title="No edit permission">
                                                        <i class="mdi mdi-pencil"></i>
                                                    </button>
                                                    {% endif %}"""
        return perm_check + "\n                                                    " + original + "\n                                                    " + else_part
    
    content = re.sub(edit_pattern, replace_edit, content, flags=re.DOTALL)
    
    # Delete button pattern
    delete_pattern = r'(<a\s+href="{%\s*url [^}]+ [^}]+ %}"\s+class="btn btn-sm btn-danger"[^>]*title="Delete"[^>]*>\s*<i class="mdi mdi-delete"></i>\s*</a>)'
    
    def replace_delete(match):
        original = match.group(1)
        perm_check = "{{% if user|has_action_permission:'{0}:delete' %}}".format(module)
        else_part = """{% else %}
                                                    <button class="btn btn-sm btn-secondary" disabled title="No delete permission">
                                                        <i class="mdi mdi-delete"></i>
                                                    </button>
                                                    {% endif %}"""
        return perm_check + "\n                                                    " + original + "\n                                                    " + else_part
    
    content = re.sub(delete_pattern, replace_delete, content, flags=re.DOTALL)
    
    # View button - wrap only if not already wrapped
    view_pattern = r'(<a\s+href="{%\s*url [^}]+ [^}]+ %}"\s+class="btn btn-sm btn-info"[^>]*title="View"[^>]*>\s*<i class="mdi mdi-eye"></i>\s*</a>)'
    
    def replace_view(match):
        original = match.group(1)
        # Check if already wrapped
        if '{%' in original and 'has_action_permission' in original:
            return original
        perm_check = "{{% if user|has_action_permission:'{0}:view' %}}".format(module)
        endif = "{% endif %}"
        return perm_check + "\n                                                    " + original + "\n                                                    " + endif
    
    content = re.sub(view_pattern, replace_view, content, flags=re.DOTALL)
    
    return content

def update_template(file_path):
    """Update a single template file with permission checks."""
    module = get_module_from_path(file_path)
    
    if not module:
        print(f"[!] Skipping {file_path} - could not determine module")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Step 1: Add permission_tags load
        content = add_permission_tags_load(content)
        
        # Step 2: Wrap Add buttons
        content = wrap_add_button(content, module)
        
        # Step 3: Wrap action buttons
        content = wrap_action_buttons(content, module)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[+] Updated: {file_path} (module: {module})")
            return True
        else:
            print(f"[-] No changes: {file_path}")
            return False
            
    except Exception as e:
        print(f"[!] Error updating {file_path}: {e}")
        return False

def main():
    """Main function to update all list templates."""
    base_path = Path(r'G:\TradifyERP\TradifyERP')
    
    # Find all *_list.html files
    list_templates = []
    
    # Search in templates/ directory
    templates_dir = base_path / 'templates'
    if templates_dir.exists():
        list_templates.extend(templates_dir.rglob('*_list.html'))
    
    # Search in module/templates/ directories
    for module in MODULE_MAPPING.keys():
        module_templates = base_path / module / 'templates'
        if module_templates.exists():
            list_templates.extend(module_templates.rglob('*_list.html'))
    
    print(f"\n[*] Found {len(list_templates)} list templates to update\n")
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for template in list_templates:
        template_str = str(template)
        
        # Skip already processed stakeholder_list.html
        if 'stakeholder_list.html' in template_str:
            print(f"[-] Skipping (already updated): {template_str}")
            skipped_count += 1
            continue
        
        # Skip user management templates
        if 'user_management' in template_str:
            print(f"[-] Skipping (user management): {template_str}")
            skipped_count += 1
            continue
        
        result = update_template(template_str)
        if result:
            updated_count += 1
        elif result is False:
            error_count += 1
    
    print(f"\n" + "="*80)
    print(f"[*] Summary:")
    print(f"   [+] Updated: {updated_count} templates")
    print(f"   [-] Skipped: {skipped_count} templates")
    print(f"   [!] Errors: {error_count} templates")
    print(f"   [*] Total: {len(list_templates)} templates")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
