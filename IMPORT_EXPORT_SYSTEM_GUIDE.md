# Import/Export System - Complete Guide

## Overview

The TradifyERP Import/Export system allows users to import and export data across all modules with permission-based access control. This system is built on top of the `ModulePermission` framework to ensure users can only import/export data they have permission to access.

---

## Table of Contents

1. [Features](#features)
2. [Permission Requirements](#permission-requirements)
3. [User Guide](#user-guide)
4. [Developer Guide](#developer-guide)
5. [Supported Modules](#supported-modules)
6. [Troubleshooting](#troubleshooting)

---

## Features

### For Users
- **Import Data**: Upload CSV or Excel files to bulk import records
- **Export Data**: Download data in CSV, Excel, or JSON formats
- **Permission-Based**: Only access import/export based on your module permissions
- **Validation**: Automatic data validation during import
- **Duplicate Detection**: Skip or update existing records
- **Templates**: Download import templates with field descriptions
- **Bulk Operations**: Process hundreds or thousands of records at once

### For Developers
- **Base Classes**: Reusable `BaseImporter` and `BaseExporter` classes
- **Easy Integration**: Add import/export to any model with minimal code
- **Customizable**: Override methods for custom validation and formatting
- **Type-Safe**: Full type hints for better IDE support
- **Error Handling**: Comprehensive error collection and reporting

---

## Permission Requirements

### Import Permission
To import data into a module, users need:
- **Module Access**: `can_view = True` for the module
- **Add Permission**: `can_add = True` for the module

### Export Permission
To export data from a module, users need:
- **Module Access**: `can_view = True` for the module
- **Export Permission**: `can_export = True` for the module

### Setting Permissions

**For Administrators:**

1. Go to **User Management** → **User List**
2. Click **Edit** on the user you want to modify
3. Scroll to **Module Permissions**
4. Check the appropriate boxes:
   - ✓ **Can Export** - Allows user to export data
   - ✓ **Can Add** - Allows user to import data

**Programmatically:**

```python
from accounting.module_permissions import ModulePermission

# Grant export permission
ModulePermission.objects.update_or_create(
    user=user,
    module='accounting',
    defaults={
        'can_view': True,
        'can_export': True,
        'is_active': True
    }
)

# Grant import permission
ModulePermission.objects.update_or_create(
    user=user,
    module='sales',
    defaults={
        'can_view': True,
        'can_add': True,
        'is_active': True
    }
)
```

---

## User Guide

### How to Import Data

#### Step 1: Download Import Template

1. Navigate to the module list view (e.g., **Accounting** → **Customers**)
2. Click the **Import/Export** button in the toolbar
3. Click **Download Template** for the data type you want to import
4. An Excel/CSV file will download with the correct field structure

#### Step 2: Fill in Your Data

1. Open the template file in Excel or a spreadsheet application
2. Fill in your data:
   - **Required fields** must be filled (marked in the template)
   - **Optional fields** can be left blank
   - **Date fields** should use format: `YYYY-MM-DD` (e.g., `2025-01-15`)
   - **Boolean fields** use: `True`, `False`, `1`, `0`, `Yes`, `No`
3. Save the file (keep as CSV or XLSX format)

**Example Customer Import:**

```csv
name,email,phone,address,city,state,country,postal_code,is_active
Acme Corp,contact@acme.com,555-0100,123 Main St,New York,NY,USA,10001,True
TechCo,info@techco.com,555-0200,456 Oak Ave,San Francisco,CA,USA,94102,True
GlobalInc,sales@global.com,555-0300,789 Pine Rd,Chicago,IL,USA,60601,True
```

#### Step 3: Upload and Import

1. Go back to the module list view
2. Click **Import** button
3. Select your filled template file
4. Choose import options:
   - ☐ **Update Existing Records**: Check this to update existing records with matching data
   - ☐ Leave unchecked to skip duplicates
5. Click **Import Data**
6. Review the results:
   - ✓ Created: New records added
   - ✓ Updated: Existing records modified
   - ✓ Skipped: Duplicate records ignored
   - ⚠ Errors: Any validation issues

### How to Export Data

#### Quick Export (from List View)

1. Navigate to the module list view
2. Click the **Export** dropdown button
3. Select your preferred format:
   - **CSV** - For Excel and data analysis
   - **Excel** - For formatted spreadsheets
   - **JSON** - For technical/API use
4. File downloads automatically

#### Filtered Export

1. Apply filters to the list view (date range, status, etc.)
2. Click **Export**
3. Only filtered records will be exported

---

## Developer Guide

### Adding Import/Export to a New Model

#### Step 1: Create Importer Class

Create a file `your_module/import_export_implementations.py`:

```python
from accounting.import_export_utils import BaseImporter, BaseExporter
from .models import YourModel

class YourModelImporter(BaseImporter):
    """Importer for YourModel"""
    
    model_class = YourModel
    required_fields = ['field1', 'field2']  # Must be present
    optional_fields = ['field3', 'field4']  # Can be blank
    unique_fields = ['field1']  # Used to detect duplicates
    
    def clean_row_data(self, row_data):
        """Custom data cleaning"""
        cleaned_data = super().clean_row_data(row_data)
        
        # Example: Convert string to integer
        if 'quantity' in cleaned_data:
            cleaned_data['quantity'] = int(cleaned_data['quantity'])
        
        # Example: Handle foreign key
        if 'category_name' in cleaned_data:
            category = Category.objects.get(name=cleaned_data['category_name'])
            cleaned_data['category'] = category
            cleaned_data.pop('category_name')
        
        return cleaned_data
```

#### Step 2: Create Exporter Class

```python
class YourModelExporter(BaseExporter):
    """Exporter for YourModel"""
    
    model_class = YourModel
    export_fields = [
        'id', 'name', 'description',
        'category__name',  # Related field
        'created_at'
    ]
    export_headers = {
        'id': 'ID',
        'name': 'Product Name',
        'category__name': 'Category',
        'created_at': 'Created Date'
    }
    
    def get_field_value(self, obj, field):
        """Custom field value extraction"""
        if field == 'special_field':
            return f"Custom: {obj.special_field}"
        return super().get_field_value(obj, field)
```

#### Step 3: Add URL Patterns

In `your_module/urls.py`:

```python
from django.urls import path
from accounting.import_export_views import (
    BaseImportView, BaseExportView, ImportTemplateDownloadView
)
from .import_export_implementations import YourModelImporter, YourModelExporter
from .models import YourModel

urlpatterns = [
    # ... existing patterns ...
    
    # Import
    path('yourmodel/import/', BaseImportView.as_view(
        importer_class=YourModelImporter,
        module_name='your_module',
        success_url='/your_module/yourmodel/'
    ), name='yourmodel_import'),
    
    # Export
    path('yourmodel/export/', BaseExportView.as_view(
        exporter_class=YourModelExporter,
        module_name='your_module'
    ), name='yourmodel_export'),
    
    # Template Download
    path('yourmodel/import-template/', ImportTemplateDownloadView.as_view(
        model_class=YourModel,
        template_fields=['field1', 'field2', 'field3'],
        module_name='your_module'
    ), name='yourmodel_import_template'),
]
```

#### Step 4: Add Buttons to Template

In `your_module/templates/yourmodel_list.html`:

```django
{% load permission_tags %}

<div class="card-header">
    <div class="d-flex justify-content-between align-items-center">
        <h5>Your Model List</h5>
        
        <div class="btn-group">
            {% if request.user|has_action_permission:'your_module:add' %}
            <a href="{% url 'your_module:yourmodel_import' %}" class="btn btn-info">
                <i class="mdi mdi-upload"></i> Import
            </a>
            <a href="{% url 'your_module:yourmodel_import_template' %}" class="btn btn-outline-info">
                <i class="mdi mdi-download"></i> Template
            </a>
            {% endif %}
            
            {% if request.user|has_action_permission:'your_module:export' %}
            <div class="btn-group">
                <button type="button" class="btn btn-success dropdown-toggle" data-bs-toggle="dropdown">
                    <i class="mdi mdi-download"></i> Export
                </button>
                <ul class="dropdown-menu">
                    <li><a class="dropdown-item" href="{% url 'your_module:yourmodel_export' %}?format=csv">
                        <i class="mdi mdi-file-delimited"></i> CSV
                    </a></li>
                    <li><a class="dropdown-item" href="{% url 'your_module:yourmodel_export' %}?format=excel">
                        <i class="mdi mdi-file-excel"></i> Excel
                    </a></li>
                    <li><a class="dropdown-item" href="{% url 'your_module:yourmodel_export' %}?format=json">
                        <i class="mdi mdi-code-braces"></i> JSON
                    </a></li>
                </ul>
            </div>
            {% endif %}
        </div>
    </div>
</div>
```

---

## Supported Modules

### Accounting Module

**Import & Export Available:**
- ✓ Accounts
- ✓ Customers
- ✓ Vendors

**Export Only:**
- ✓ Journal Entries
- ✓ Ledger Entries

**Access URLs:**
- Import Dashboard: `/accounting/import-export/`
- Account Import: `/accounting/accounts/import/`
- Customer Export: `/accounting/customers/export/?format=excel`

### Sales Module

**Import & Export Available:**
- ✓ Customers
- ✓ Products
- ✓ Price Lists

**Export Only:**
- ✓ Sales Orders
- ✓ Invoices

### HR Module

**Import & Export Available:**
- ✓ Employees
- ✓ Departments

**Export Only:**
- ✓ Payroll Records
- ✓ Attendance

### Inventory Module

**Import & Export Available:**
- ✓ Products
- ✓ Warehouses
- ✓ Stock Adjustments

### Procurement Module

**Import & Export Available:**
- ✓ Suppliers
- ✓ Purchase Orders

### CRM Module

**Import & Export Available:**
- ✓ Leads
- ✓ Opportunities
- ✓ Contacts

---

## Troubleshooting

### Common Import Errors

#### "Missing required fields"
**Problem**: Template missing required columns
**Solution**: Download the latest template and ensure all required columns are present

#### "Duplicate record skipped"
**Problem**: Record with same unique identifier already exists
**Solution**: 
- Check "Update Existing Records" to update instead of skip
- Or remove duplicates from your file

#### "Invalid date format"
**Problem**: Date not in correct format
**Solution**: Use `YYYY-MM-DD` format (e.g., `2025-01-15`)

#### "Permission denied"
**Problem**: User doesn't have import/export permission
**Solution**: Contact administrator to grant permissions

### Common Export Errors

#### "No data to export"
**Problem**: No records match current filters
**Solution**: Clear filters or adjust filter criteria

#### "Excel export failed"
**Problem**: `openpyxl` library not installed
**Solution**: Install with `pip install openpyxl` or use CSV format

### Performance Tips

**For Large Imports:**
- Split files into batches of 1000-5000 records
- Import during off-peak hours
- Use "Update Existing" sparingly (slower)

**For Large Exports:**
- Apply filters to reduce record count
- Use CSV format (faster than Excel)
- Export in chunks if needed

---

## Advanced Features

### Custom Field Mapping

Override `clean_row_data()` to transform fields:

```python
def clean_row_data(self, row_data):
    cleaned_data = super().clean_row_data(row_data)
    
    # Map old field names to new
    if 'old_name' in row_data:
        cleaned_data['new_name'] = row_data['old_name']
    
    # Calculate derived fields
    if 'price' in cleaned_data and 'quantity' in cleaned_data:
        cleaned_data['total'] = cleaned_data['price'] * cleaned_data['quantity']
    
    return cleaned_data
```

### Related Object Handling

```python
def clean_row_data(self, row_data):
    cleaned_data = super().clean_row_data(row_data)
    
    # Get or create related object
    if 'category_name' in row_data:
        category, _ = Category.objects.get_or_create(
            name=row_data['category_name']
        )
        cleaned_data['category'] = category
    
    return cleaned_data
```

### Conditional Exports

```python
def get_queryset(self, filters=None):
    queryset = super().get_queryset(filters)
    
    # Only export active records
    queryset = queryset.filter(is_active=True)
    
    # Apply user-specific filtering
    if not self.user.is_superuser:
        queryset = queryset.filter(created_by=self.user)
    
    return queryset
```

---

## API Reference

### BaseImporter

**Attributes:**
- `model_class`: Model to import into
- `required_fields`: List of required field names
- `optional_fields`: List of optional field names
- `unique_fields`: Fields used for duplicate detection

**Methods:**
- `import_data(file, update_existing=False)`: Main import method
- `clean_row_data(row_data)`: Override for custom validation
- `check_duplicate(cleaned_data)`: Check if record exists

### BaseExporter

**Attributes:**
- `model_class`: Model to export from
- `export_fields`: List of fields to include
- `export_headers`: Dict mapping fields to display headers

**Methods:**
- `export_csv(queryset, filename)`: Export as CSV
- `export_excel(queryset, filename)`: Export as Excel
- `export_json(queryset, filename)`: Export as JSON
- `get_queryset(filters)`: Override for custom filtering

---

## Support

For issues or questions:
1. Check this documentation
2. Review example implementations in `accounting/import_export_implementations.py`
3. Contact your system administrator
4. Submit a support ticket

---

**Last Updated**: November 22, 2025  
**Version**: 1.0.0
