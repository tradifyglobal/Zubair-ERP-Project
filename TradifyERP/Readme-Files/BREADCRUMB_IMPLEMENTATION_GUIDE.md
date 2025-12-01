# Breadcrumb Navigation Implementation Guide

## Overview
A breadcrumb system has been implemented across all modules and pages. Each detail page now displays:

**Format:** `Module -> Category -> Item`  
**Example:** `Manufacturing -> Performance -> Test Distributor`

## For Existing Views

### Step 1: Import the BreadcrumbMixin
```python
from utils.breadcrumbs import BreadcrumbMixin
```

### Step 2: Add Mixin to Your DetailView
```python
class YourDetailView(LoginRequiredMixin, BreadcrumbMixin, DetailView):
    model = YourModel
    template_name = 'app/yourmodel_detail.html'
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Module Name', 'url': reverse('module:dashboard')},
            {'title': 'Category/List', 'url': reverse('module:list_view')},
            {'title': str(self.object)}  # Displays the object's __str__ or custom title
        ]
```

### Step 3: Update Your Template
Replace the hardcoded breadcrumb section with:
```html
<!-- Before (Hardcoded) -->
<div class="page-title-box d-sm-flex align-items-center justify-content-between">
    <h4 class="mb-sm-0 font-size-18">{{ object.name }}</h4>
    <div class="page-title-right">
        <ol class="breadcrumb m-0">
            <li class="breadcrumb-item"><a href="...">Module</a></li>
            ...
        </ol>
    </div>
</div>

<!-- After (Using include) -->
{% include 'partials/breadcrumb.html' %}
```

## Implemented Examples

### Manufacturing Module
- ✅ **DistributorPerformance**: `Manufacturing -> Performance -> {Distributor Name}`
- ✅ **WarrantyRegistration**: `Manufacturing -> Warranties -> {Warranty Number}`

## How It Works

1. **BreadcrumbMixin** - Adds `get_breadcrumbs()` method to views
2. **Context Processor** - Makes breadcrumbs available in all templates
3. **Breadcrumb Include** - Renders breadcrumbs in `partials/breadcrumb.html`

## Breadcrumb Structure

Each breadcrumb item is a dictionary with:
- `title` (required): The text to display
- `url` (optional): Link URL. If omitted, the item is not clickable

```python
def get_breadcrumbs(self):
    return [
        {'title': 'Dashboard', 'url': reverse('dashboard')},  # Clickable
        {'title': 'Users', 'url': reverse('user_list')},      # Clickable
        {'title': 'John Doe'}                                   # Not clickable (last item)
    ]
```

## URL Format

When viewing detail pages, breadcrumbs will appear as:

```
Dashboard -> Module -> Category -> Item Name
```

Example URLs and their breadcrumbs:
- `/manufacturing/performance/1/` 
  → Manufacturing → Performance → Test Distributor

- `/manufacturing/warranties/5/`
  → Manufacturing → Warranties → WRT-20251123-12345

## Adding to Other Modules

To add breadcrumbs to any module:

1. Import `BreadcrumbMixin` in your views.py
2. Add it to your DetailView classes
3. Implement `get_breadcrumbs()` method
4. Update templates to use `{% include 'partials/breadcrumb.html' %}`

## Styling

Breadcrumbs use Bootstrap 5 classes:
- `breadcrumb` - Main container
- `breadcrumb-item` - Individual items
- `breadcrumb-item active` - Current (last) item

CSS is already in base.html and handles responsive display.

---

**Status**: ✅ Ready to implement across all modules  
**Files Modified**:
- `utils/breadcrumbs.py` - Mixin
- `templates/partials/breadcrumb.html` - Include template
- `TradifyERP/context_processors.py` - Context processor
- `TradifyERP/settings.py` - Template settings
- `manufacturing/views.py` - View implementations
- Manufacturing detail templates - Use include
