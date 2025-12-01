#!/usr/bin/env python
"""
Verify that all CRM list templates have correct context variable names
matching their corresponding ListView definitions.
"""

import os
import re
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.views.generic import ListView
from crm import views

# Mapping of template files to view classes
TEMPLATES_TO_CHECK = {
    'crm/territory_list.html': views.TerritoryListView,
    'crm/customergroup_list.html': views.CustomerGroupListView,
    'crm/contact_list.html': views.ContactListView,
    'crm/prospect_list.html': views.ProspectListView,
    'crm/salesperson_list.html': views.SalesPersonListView,
    'crm/leadsource_list.html': views.LeadSourceListView,
    'crm/contract_list.html': views.ContractListView,
    'crm/appointment_list.html': views.AppointmentListView,
    'crm/communication_list.html': views.CommunicationListView,
    'crm/emailcampaign_list.html': views.EmailCampaignListView,
    'crm/smscenter_list.html': views.SMSCenterListView,
    'crm/emailgroup_list.html': views.EmailGroupListView,
    'crm/maintenanceschedule_list.html': views.MaintenanceScheduleListView,
    'crm/maintenancevisit_list.html': views.MaintenanceVisitListView,
    'crm/warrantyclaim_list.html': views.WarrantyClaimListView,
}

def get_context_object_name(view_class):
    """Get the context_object_name from a ListView class."""
    if hasattr(view_class, 'context_object_name'):
        return view_class.context_object_name
    # Default is model name in lowercase
    return view_class.model._meta.model_name

def extract_context_vars_from_template(template_path):
    """Extract context variable names from template file."""
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        # Find {% if variable_name %} patterns
        matches = re.findall(r'{%\s*if\s+(\w+)\s*%}', content)
        return matches
    except FileNotFoundError:
        return []

def main():
    print("=" * 70)
    print("TEMPLATE CONTEXT VARIABLE VERIFICATION")
    print("=" * 70)
    
    template_dir = 'crm/templates'
    issues_found = False
    
    for template_name, view_class in TEMPLATES_TO_CHECK.items():
        expected_var = get_context_object_name(view_class)
        template_path = os.path.join(template_dir, template_name)
        
        used_vars = extract_context_vars_from_template(template_path)
        
        # Filter out common non-data context vars
        data_vars = [v for v in used_vars if v not in ['user', 'is_paginated', 'page_obj', 'is_active']]
        
        if not data_vars:
            status = "⚠️ WARNING"
            print(f"{status}: {template_name}")
            print(f"  → No context variables found (template may be empty)")
            issues_found = True
        elif expected_var not in used_vars:
            status = "❌ MISMATCH"
            print(f"{status}: {template_name}")
            print(f"  → Expected: '{expected_var}'")
            print(f"  → Found in template: {used_vars}")
            issues_found = True
        else:
            status = "✅ OK"
            print(f"{status}: {template_name}")
            print(f"  → Context variable: '{expected_var}'")
    
    print("\n" + "=" * 70)
    if issues_found:
        print("⚠️ ISSUES FOUND - Please review above")
    else:
        print("✅ ALL TEMPLATES CORRECTLY CONFIGURED")
    print("=" * 70)

if __name__ == '__main__':
    main()
