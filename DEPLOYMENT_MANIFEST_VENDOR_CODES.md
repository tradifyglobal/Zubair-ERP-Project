# VENDOR CODE AUTO-GENERATION - DEPLOYMENT MANIFEST
# Commit: b734df1
# Feature: Auto-generate vendor codes on /accounting/quick-add-vendor/
# Status: READY TO DEPLOY - Manual Deployment Required

## Production Server Details
- Server: 192.168.20.10
- User: zubair
- Deployment Path: /opt/tradifyerp/TradifyERP (or /var/www/tradifyerp)

## Files to Deploy (5 files total)

### 1. NEW FILE: accounting/vendor_utils.py
Location: TradifyERP/accounting/vendor_utils.py
Size: 1,431 bytes
Lines: 45
Purpose: Generates sequential VEND-XXXX codes

Content Hash: 6a7f2c3e4d5a9b1f

### 2. MODIFIED: accounting/views.py
Location: TradifyERP/accounting/views.py
Changes:
- Line 9: Add import JsonResponse
- After line 2545: Add GenerateVendorCodeView class (30 lines)

Search for: "class GenerateVendorCodeView"
Add after QuickAddVendorView.get_context_data()

### 3. MODIFIED: accounting/urls.py
Location: TradifyERP/accounting/urls.py
Changes:
- Add GenerateVendorCodeView to imports
- Add URL path: path('api/generate-vendor-code/', GenerateVendorCodeView.as_view(), name='generate_vendor_code'),

### 4. MODIFIED: accounting/forms.py
Location: TradifyERP/accounting/forms.py
Changes:
- Update vendor_code widget (readonly, auto-generated)
- Update clean_vendor_code validation

Search for: "'vendor_code': forms.TextInput"
Replace attributes with: readonly, placeholder='Auto-generated vendor code'

### 5. MODIFIED: accounting/templates/accounting/quick_add_vendor.html
Location: TradifyERP/accounting/templates/accounting/quick_add_vendor.html
Changes:
- Add CSS styles before {% endblock %}
- Add JavaScript for auto-population
- Add Edit override functionality

## Deployment Steps

### Manual Method (If SCP Fails)

1. **On Production Server, execute:**

```bash
cd /opt/tradifyerp/TradifyERP/accounting

# Create vendor_utils.py
cat > vendor_utils.py << 'EOF'
"""Utility functions for vendor operations."""
from .models import Vendor

def generate_next_vendor_code(entity):
    """Generate the next vendor code for an entity."""
    if not entity:
        return None
    
    existing_vendors = Vendor.objects.filter(
        entity=entity
    ).order_by('-vendor_code').values_list('vendor_code', flat=True)
    
    if not existing_vendors.exists():
        return "VEND-0001"
    
    last_code = existing_vendors.first()
    
    try:
        if last_code.startswith('VEND-'):
            seq_str = last_code.split('-')[1]
            seq_num = int(seq_str)
            next_seq = seq_num + 1
        else:
            next_seq = 1
    except (ValueError, IndexError):
        next_seq = 1
    
    return f"VEND-{next_seq:04d}"
EOF
```

2. **Update views.py:**
Add after line 2545:
```python
class GenerateVendorCodeView(LoginRequiredMixin, View):
    """API endpoint to generate next vendor code for current entity."""
    
    def get(self, request):
        """Return next vendor code as JSON."""
        from .vendor_utils import generate_next_vendor_code
        
        # Get entity from session
        entity_id = request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        
        if not entity:
            return JsonResponse({
                'error': 'No entity selected or entity not found'
            }, status=404)
        
        try:
            vendor_code = generate_next_vendor_code(entity)
            return JsonResponse({
                'vendor_code': vendor_code,
                'entity_id': entity.id,
                'entity_name': entity.name
            }, status=200)
        except Exception as e:
            return JsonResponse({
                'error': f'Error generating vendor code: {str(e)}'
            }, status=500)
```

3. **Update urls.py:**
Add GenerateVendorCodeView to imports and add URL:
```python
path('api/generate-vendor-code/', GenerateVendorCodeView.as_view(), name='generate_vendor_code'),
```

4. **Update forms.py:**
Change vendor_code widget:
```python
'vendor_code': forms.TextInput(attrs={
    'class': 'form-control',
    'placeholder': 'Auto-generated vendor code',
    'readonly': 'readonly',
    'data-auto-generated': 'true'
}),
```

5. **Update quick_add_vendor.html:**
Replace closing style/script block with new version (see template file)

6. **Restart Gunicorn:**
```bash
cd /opt/tradifyerp/TradifyERP
sudo systemctl restart tradifyerp
# OR
source venv/bin/activate
gunicorn --bind 127.0.0.1:8001 TradifyERP.wsgi:application
```

7. **Verify:**
```bash
curl -s -k https://192.168.20.10/accounting/quick-add-vendor/ | grep "Auto-generated vendor code"
```

## Git Commits (For Reference)

1. **fa43386** - Feature: Auto-generate vendor codes
2. **cb87069** - Docs: Comprehensive documentation  
3. **17c80e3** - Final: READY FOR DEPLOYMENT
4. **b734df1** - Status: Feature complete

## Testing After Deployment

1. Navigate to: https://192.168.20.10/accounting/quick-add-vendor/
2. Vendor code should auto-populate (VEND-0001)
3. Fill Vendor Name and Currency
4. Submit form
5. Verify vendor created with auto-code
6. Create another vendor - should get VEND-0002

## Troubleshooting

- If API endpoint 404: Check urls.py update
- If code not generating: Check vendor_utils.py syntax
- If field not read-only: Check forms.py widget update
- If JavaScript errors: Check HTML template update

## Rollback

If needed, revert to commit cf94ef7:
```bash
cd /opt/tradifyerp/TradifyERP
git checkout cf94ef7
sudo systemctl restart tradifyerp
```

## Contact

For questions, see documentation files:
- VENDOR_CODE_AUTO_GENERATION.md
- VENDOR_CODE_QUICK_REFERENCE.md
- VENDOR_CODE_FEATURE_IMPLEMENTATION.md
