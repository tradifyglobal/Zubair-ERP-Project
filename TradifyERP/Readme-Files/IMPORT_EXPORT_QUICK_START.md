# Quick Start: Import/Export Data

## 🚀 5-Minute Guide to Import/Export

---

## For Users: How to Use Import/Export

### Importing Data (3 Steps)

#### Step 1: Download Template
1. Go to the list page (e.g., **Accounting** → **Customers**)
2. Click **"Template"** button in the toolbar
3. Save the CSV/Excel file to your computer

#### Step 2: Fill in Your Data
1. Open the template in Excel
2. Fill in each row with your data
3. Required fields must have values
4. Save the file

**Example:**
```
name          | email              | phone      | city
------------- | ------------------ | ---------- | --------
ABC Company   | abc@example.com    | 555-0100   | New York
XYZ Corp      | xyz@example.com    | 555-0200   | Chicago
```

#### Step 3: Upload and Import
1. Click **"Import"** button
2. Select your filled file
3. Click **"Import Data"**
4. Review the results

### Exporting Data (2 Steps)

#### Step 1: Filter (Optional)
Apply any filters you want in the list view

#### Step 2: Export
1. Click **"Export"** dropdown button
2. Choose format:
   - **CSV** - Opens in Excel
   - **Excel** - Formatted spreadsheet
   - **JSON** - For technical use
3. File downloads automatically

---

## For Developers: Add to New Model (10 Minutes)

### Step 1: Create Importer/Exporter (5 min)

Create `your_module/import_export_implementations.py`:

```python
from accounting.import_export_utils import BaseImporter, BaseExporter
from .models import YourModel

class YourModelImporter(BaseImporter):
    model_class = YourModel
    required_fields = ['name', 'code']
    optional_fields = ['description', 'status']
    unique_fields = ['code']

class YourModelExporter(BaseExporter):
    model_class = YourModel
    export_fields = ['code', 'name', 'description', 'created_at']
    export_headers = {
        'code': 'Code',
        'name': 'Name',
        'description': 'Description',
        'created_at': 'Created Date'
    }
```

### Step 2: Add URLs (2 min)

In `your_module/urls.py`:

```python
from accounting.import_export_views import BaseImportView, BaseExportView, ImportTemplateDownloadView
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
    
    # Template
    path('yourmodel/import-template/', ImportTemplateDownloadView.as_view(
        model_class=YourModel,
        template_fields=['code', 'name', 'description', 'status'],
        module_name='your_module'
    ), name='yourmodel_import_template'),
]
```

### Step 3: Add Buttons to Template (3 min)

In `templates/your_module/yourmodel_list.html`:

```django
{% load permission_tags %}

<!-- Add this above your table -->
<div class="card-header">
    <div class="d-flex justify-content-between align-items-center">
        <h5>Your Model List</h5>
        
        {% include 'accounting/components/import_export_toolbar.html' with 
           module_name='your_module'
           model_name='YourModel'
           import_url='your_module:yourmodel_import'
           export_url='your_module:yourmodel_export'
           template_url='your_module:yourmodel_import_template'
        %}
    </div>
</div>
```

**Done!** Import/Export is now available for your model.

---

## Common Questions

**Q: Who can import/export data?**  
A: Users with appropriate module permissions. Contact your administrator.

**Q: What file formats are supported?**  
A: Import: CSV, Excel (.xlsx, .xls). Export: CSV, Excel, JSON.

**Q: What happens with duplicate records?**  
A: You can choose to update them or skip them during import.

**Q: Can I export filtered data?**  
A: Yes! Apply filters first, then export.

**Q: How many records can I import at once?**  
A: Recommended: 1,000-5,000 records per file for best performance.

**Q: Where can I see errors if import fails?**  
A: Error messages appear on screen after import. First 5 errors shown.

---

## Quick Checklist

### Before Importing:
- [ ] Download the latest template
- [ ] Fill all required fields
- [ ] Use correct date format (YYYY-MM-DD)
- [ ] Check for duplicate values in unique fields
- [ ] Save as CSV or Excel format

### For Permission Issues:
- [ ] Check Module Permissions in User Management
- [ ] Ensure "Can Add" is checked (for import)
- [ ] Ensure "Can Export" is checked (for export)
- [ ] Contact administrator if needed

---

## Need More Help?

📖 **Full Documentation**: See `IMPORT_EXPORT_SYSTEM_GUIDE.md`  
💻 **Code Examples**: See `accounting/import_export_implementations.py`  
🔧 **Technical Details**: See `IMPORT_EXPORT_IMPLEMENTATION_SUMMARY.md`

---

**Last Updated**: November 22, 2025
