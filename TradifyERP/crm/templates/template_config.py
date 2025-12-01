"""
Template Generator for CRM Models
This script generates list, form, detail, and delete confirmation templates
for all CRM models using established patterns.
"""

template_config = {
    'customergroup': {
        'name': 'Customer Group',
        'list_fields': [
            ('group_code', 'Group Code'),
            ('group_name', 'Group Name'),
            ('is_active', 'Status'),
        ],
        'detail_fields': [
            ('group_code', 'Group Code'),
            ('group_name', 'Group Name'),
            ('description', 'Description'),
            ('is_active', 'Status'),
        ],
        'form_fields': [
            ('group_code', 'col-md-6'),
            ('group_name', 'col-md-6'),
            ('description', 'col-md-12'),
            ('is_active', 'col-md-12'),
        ]
    },
    'contact': {
        'name': 'Contact',
        'list_fields': [
            ('contact_name', 'Contact Name'),
            ('customer', 'Customer'),
            ('email', 'Email'),
            ('phone', 'Phone'),
        ],
        'detail_fields': [
            ('contact_name', 'Contact Name'),
            ('customer', 'Customer'),
            ('designation', 'Designation'),
            ('company', 'Company'),
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('mobile', 'Mobile'),
            ('address', 'Address'),
        ],
        'form_fields': [
            ('contact_name', 'col-md-6'),
            ('customer', 'col-md-6'),
            ('designation', 'col-md-6'),
            ('company', 'col-md-6'),
            ('email', 'col-md-6'),
            ('phone', 'col-md-6'),
            ('mobile', 'col-md-6'),
            ('is_primary_contact', 'col-md-6'),
            ('address', 'col-md-12'),
        ]
    },
    'prospect': {
        'name': 'Prospect',
        'list_fields': [
            ('prospect_name', 'Prospect Name'),
            ('status', 'Status'),
            ('probability', 'Probability'),
            ('estimated_value', 'Estimated Value'),
        ],
        'detail_fields': [
            ('prospect_name', 'Prospect Name'),
            ('status', 'Status'),
            ('probability', 'Probability'),
            ('estimated_value', 'Estimated Value'),
            ('expected_closing_date', 'Expected Closing'),
            ('notes', 'Notes'),
        ],
        'form_fields': [
            ('prospect_name', 'col-md-6'),
            ('status', 'col-md-6'),
            ('probability', 'col-md-6'),
            ('estimated_value', 'col-md-6'),
            ('expected_closing_date', 'col-md-6'),
            ('notes', 'col-md-12'),
        ]
    },
    'salesperson': {
        'name': 'Sales Person',
        'list_fields': [
            ('salesperson_name', 'Sales Person'),
            ('user', 'User'),
            ('territory', 'Territory'),
            ('manager', 'Manager'),
        ],
        'detail_fields': [
            ('salesperson_name', 'Sales Person'),
            ('user', 'User'),
            ('territory', 'Territory'),
            ('manager', 'Manager'),
            ('commission_percentage', 'Commission %'),
        ],
        'form_fields': [
            ('salesperson_name', 'col-md-6'),
            ('user', 'col-md-6'),
            ('territory', 'col-md-6'),
            ('manager', 'col-md-6'),
            ('commission_percentage', 'col-md-6'),
        ]
    },
    'leadsource': {
        'name': 'Lead Source',
        'list_fields': [
            ('source_code', 'Source Code'),
            ('source_name', 'Source Name'),
            ('is_active', 'Status'),
        ],
        'detail_fields': [
            ('source_code', 'Source Code'),
            ('source_name', 'Source Name'),
            ('description', 'Description'),
            ('is_active', 'Status'),
        ],
        'form_fields': [
            ('source_code', 'col-md-6'),
            ('source_name', 'col-md-6'),
            ('description', 'col-md-12'),
            ('is_active', 'col-md-12'),
        ]
    },
    'contract': {
        'name': 'Contract',
        'list_fields': [
            ('contract_number', 'Contract #'),
            ('customer', 'Customer'),
            ('contract_value', 'Value'),
            ('status', 'Status'),
        ],
        'detail_fields': [
            ('contract_number', 'Contract Number'),
            ('customer', 'Customer'),
            ('contract_value', 'Contract Value'),
            ('start_date', 'Start Date'),
            ('end_date', 'End Date'),
            ('status', 'Status'),
            ('renewal_date', 'Renewal Date'),
        ],
        'form_fields': [
            ('contract_number', 'col-md-6'),
            ('customer', 'col-md-6'),
            ('contract_value', 'col-md-6'),
            ('start_date', 'col-md-6'),
            ('end_date', 'col-md-6'),
            ('renewal_date', 'col-md-6'),
            ('status', 'col-md-6'),
            ('terms_and_conditions', 'col-md-12'),
        ]
    },
    'appointment': {
        'name': 'Appointment',
        'list_fields': [
            ('subject', 'Subject'),
            ('contact', 'Contact'),
            ('appointment_date', 'Date'),
            ('duration_minutes', 'Duration'),
        ],
        'detail_fields': [
            ('subject', 'Subject'),
            ('contact', 'Contact'),
            ('appointment_date', 'Appointment Date'),
            ('duration_minutes', 'Duration'),
            ('location', 'Location'),
            ('notes', 'Notes'),
        ],
        'form_fields': [
            ('subject', 'col-md-12'),
            ('contact', 'col-md-6'),
            ('appointment_date', 'col-md-6'),
            ('duration_minutes', 'col-md-6'),
            ('location', 'col-md-6'),
            ('notes', 'col-md-12'),
        ]
    },
    'communication': {
        'name': 'Communication',
        'list_fields': [
            ('communication_type', 'Type'),
            ('contact', 'Contact'),
            ('subject', 'Subject'),
            ('communication_date', 'Date'),
        ],
        'detail_fields': [
            ('communication_type', 'Type'),
            ('contact', 'Contact'),
            ('subject', 'Subject'),
            ('communication_date', 'Date'),
            ('notes', 'Notes'),
            ('follow_up_date', 'Follow-up Date'),
        ],
        'form_fields': [
            ('communication_type', 'col-md-6'),
            ('contact', 'col-md-6'),
            ('subject', 'col-md-12'),
            ('communication_date', 'col-md-6'),
            ('follow_up_date', 'col-md-6'),
            ('notes', 'col-md-12'),
        ]
    },
    'emailcampaign': {
        'name': 'Email Campaign',
        'list_fields': [
            ('campaign_name', 'Campaign Name'),
            ('status', 'Status'),
            ('created_at', 'Created'),
        ],
        'detail_fields': [
            ('campaign_name', 'Campaign Name'),
            ('subject', 'Subject'),
            ('status', 'Status'),
            ('opens', 'Opens'),
            ('clicks', 'Clicks'),
        ],
        'form_fields': [
            ('campaign_name', 'col-md-12'),
            ('subject', 'col-md-12'),
            ('status', 'col-md-6'),
            ('opens', 'col-md-6'),
            ('clicks', 'col-md-6'),
        ]
    },
    'smscenter': {
        'name': 'SMS Center',
        'list_fields': [
            ('sms_text', 'SMS Text'),
            ('status', 'Status'),
            ('created_at', 'Created'),
        ],
        'detail_fields': [
            ('sms_text', 'SMS Text'),
            ('status', 'Status'),
            ('delivery_count', 'Delivered'),
            ('failed_count', 'Failed'),
        ],
        'form_fields': [
            ('sms_text', 'col-md-12'),
            ('status', 'col-md-6'),
        ]
    },
    'emailgroup': {
        'name': 'Email Group',
        'list_fields': [
            ('group_name', 'Group Name'),
            ('created_at', 'Created'),
        ],
        'detail_fields': [
            ('group_name', 'Group Name'),
            ('description', 'Description'),
        ],
        'form_fields': [
            ('group_name', 'col-md-12'),
            ('description', 'col-md-12'),
        ]
    },
    'maintenanceschedule': {
        'name': 'Maintenance Schedule',
        'list_fields': [
            ('schedule_name', 'Schedule Name'),
            ('frequency', 'Frequency'),
            ('customer', 'Customer'),
        ],
        'detail_fields': [
            ('schedule_name', 'Schedule Name'),
            ('frequency', 'Frequency'),
            ('customer', 'Customer'),
            ('service_description', 'Service Description'),
        ],
        'form_fields': [
            ('schedule_name', 'col-md-6'),
            ('frequency', 'col-md-6'),
            ('customer', 'col-md-6'),
            ('service_description', 'col-md-12'),
        ]
    },
    'maintenancevisit': {
        'name': 'Maintenance Visit',
        'list_fields': [
            ('visit_date', 'Visit Date'),
            ('customer', 'Customer'),
            ('status', 'Status'),
            ('cost', 'Cost'),
        ],
        'detail_fields': [
            ('visit_date', 'Visit Date'),
            ('customer', 'Customer'),
            ('status', 'Status'),
            ('cost', 'Cost'),
            ('parts_used', 'Parts Used'),
        ],
        'form_fields': [
            ('visit_date', 'col-md-6'),
            ('customer', 'col-md-6'),
            ('status', 'col-md-6'),
            ('cost', 'col-md-6'),
            ('parts_used', 'col-md-12'),
        ]
    },
    'warrantyclaim': {
        'name': 'Warranty Claim',
        'list_fields': [
            ('claim_number', 'Claim #'),
            ('customer', 'Customer'),
            ('status', 'Status'),
            ('claim_date', 'Claim Date'),
        ],
        'detail_fields': [
            ('claim_number', 'Claim Number'),
            ('customer', 'Customer'),
            ('status', 'Status'),
            ('claim_date', 'Claim Date'),
            ('claim_description', 'Description'),
        ],
        'form_fields': [
            ('claim_number', 'col-md-6'),
            ('customer', 'col-md-6'),
            ('status', 'col-md-6'),
            ('claim_date', 'col-md-6'),
            ('claim_description', 'col-md-12'),
        ]
    },
}

if __name__ == '__main__':
    print("Template configuration loaded for:")
    for model_name in sorted(template_config.keys()):
        print(f"  - {template_config[model_name]['name']}")
    print(f"\nTotal models: {len(template_config)}")
