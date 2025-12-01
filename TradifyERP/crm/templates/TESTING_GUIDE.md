# CRM List Templates - Quick Reference & Testing Guide

## Accessing List Views

The following list views are now fully functional and can be accessed:

### Masters Module

1. **Territories**
   - URL: `/crm/territories/`
   - Template: `territory_list.html`
   - View: `TerritoryListView`
   - Context: `territories`

2. **Customer Groups**
   - URL: `/crm/customer-groups/`
   - Template: `customergroup_list.html`
   - View: `CustomerGroupListView`
   - Context: `customergroups`

3. **Contacts**
   - URL: `/crm/contacts/`
   - Template: `contact_list.html`
   - View: `ContactListView`
   - Context: `contacts`

4. **Prospects**
   - URL: `/crm/prospects/`
   - Template: `prospect_list.html`
   - View: `ProspectListView`
   - Context: `prospects`

5. **Sales People**
   - URL: `/crm/salespersons/`
   - Template: `salesperson_list.html`
   - View: `SalesPersonListView`
   - Context: `salespersons`

6. **Lead Sources**
   - URL: `/crm/lead-sources/`
   - Template: `leadsource_list.html`
   - View: `LeadSourceListView`
   - Context: `leadsources`

### Sales Pipeline Module

7. **Contracts**
   - URL: `/crm/contracts/`
   - Template: `contract_list.html`
   - View: `ContractListView`
   - Context: `contracts`

8. **Appointments**
   - URL: `/crm/appointments/`
   - Template: `appointment_list.html`
   - View: `AppointmentListView`
   - Context: `appointments`

9. **Communications**
   - URL: `/crm/communications/`
   - Template: `communication_list.html`
   - View: `CommunicationListView`
   - Context: `communications`

### Campaign Module

10. **Email Campaigns**
    - URL: `/crm/email-campaigns/`
    - Template: `emailcampaign_list.html`
    - View: `EmailCampaignListView`
    - Context: `emailcampaigns`

11. **SMS Campaigns**
    - URL: `/crm/sms-campaigns/`
    - Template: `smscenter_list.html`
    - View: `SMSCenterListView`
    - Context: `smscenters`

12. **Email Groups**
    - URL: `/crm/email-groups/`
    - Template: `emailgroup_list.html`
    - View: `EmailGroupListView`
    - Context: `emailgroups`

### Maintenance Module

13. **Maintenance Schedules**
    - URL: `/crm/maintenance-schedules/`
    - Template: `maintenanceschedule_list.html`
    - View: `MaintenanceScheduleListView`
    - Context: `maintenanceschedules`

14. **Maintenance Visits**
    - URL: `/crm/maintenance-visits/`
    - Template: `maintenancevisit_list.html`
    - View: `MaintenanceVisitListView`
    - Context: `maintenancevisits`

15. **Warranty Claims**
    - URL: `/crm/warranty-claims/`
    - Template: `warrantyclaim_list.html`
    - View: `WarrantyClaimListView`
    - Context: `warrantyclaims`

## Features Implemented

Each list template includes:

✅ **Bootstrap Table Styling**
   - Responsive design
   - Striped rows
   - Hover effects

✅ **Pagination**
   - First/Previous/Next/Last navigation
   - Current page indicator
   - Configurable items per page (20 default)

✅ **Action Buttons**
   - View (Info icon) - Opens detail page
   - Edit (Edit icon) - Opens update form
   - Delete (Trash icon) - Confirms deletion

✅ **Empty States**
   - User-friendly message when no records
   - Quick link to create new record

✅ **Column Headers**
   - Model-specific relevant fields
   - Status indicators where applicable
   - Date formatting for date fields

## Testing Checklist

- [ ] Login to admin account
- [ ] Navigate to each list URL above
- [ ] Verify table displays (empty or with sample data)
- [ ] Test "New [Model]" button creates new record
- [ ] Test "View" button opens detail page
- [ ] Test "Edit" button opens form page
- [ ] Test "Delete" button triggers deletion
- [ ] Test pagination (create 20+ records to test)

## Creating Test Data

To populate the CRM with test data, use Django admin:

1. Go to `/admin/`
2. Navigate to each model
3. Add test records
4. Return to list views to see populated tables

Or use Django shell:
```python
python manage.py shell
from crm.models import Territory, Customer, Contact
from django.contrib.auth.models import User
from datetime import datetime

# Create sample data
entity = Entity.objects.get_or_create(id=1)[0]
Territory.objects.create(
    entity=entity,
    territory_code='TER001',
    territory_name='North Region',
    annual_target=1000000
)
```

## Navigation Integration

To add these list views to your main navigation/menu, add links to:

```html
<a href="{% url 'crm:territories' %}">Territories</a>
<a href="{% url 'crm:customergroups' %}">Customer Groups</a>
<a href="{% url 'crm:contacts' %}">Contacts</a>
<!-- etc. -->
```

## Performance Notes

- All list views use pagination (20 items per page)
- Database queries should be optimized with `select_related()` and `prefetch_related()` for foreign keys
- Consider adding search filters and advanced filtering for better UX

## Error Handling

All templates include:
- Fallback display for missing related objects (`|default:"—"`)
- Safe date formatting with Django filters
- Proper escaping of user data (Django auto-escapes by default)

## Next Phase: Form & Detail Templates

To complete the CRUD implementation, still needed:
- 16 Form templates for Create/Update operations
- 16 Detail templates for record view pages
- 16 Delete confirmation templates
