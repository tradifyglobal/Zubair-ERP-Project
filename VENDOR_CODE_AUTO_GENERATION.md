# Vendor Code Auto-Generation Feature

## Overview
Implemented automatic vendor code generation on the `/accounting/quick-add-vendor/` page. The system now auto-generates sequential vendor codes (VEND-0001, VEND-0002, etc.) when creating new vendors, reducing manual data entry.

## Changes Made

### 1. **New File: `accounting/vendor_utils.py`**
   - **Purpose:** Utility functions for vendor operations
   - **Function:** `generate_next_vendor_code(entity)`
     - Generates the next vendor code in VEND-XXXX format
     - Queries existing vendors for the entity
     - Returns zero-padded sequence number (VEND-0001, VEND-0002, etc.)
     - Handles edge cases (no vendors, non-standard format codes)

### 2. **Modified: `accounting/views.py`**
   - **Added Import:** `from django.http import JsonResponse` (line 9)
   - **New View:** `GenerateVendorCodeView` (after QuickAddVendorView)
     - Inherits from `LoginRequiredMixin` and `View`
     - GET method returns JSON with auto-generated vendor code
     - Response format: `{"vendor_code": "VEND-0001", "entity_id": X, "entity_name": "..."}`
     - Error handling for missing entity

### 3. **Modified: `accounting/urls.py`**
   - **Added Import:** `GenerateVendorCodeView` to imports
   - **Added URL Path:** `path('api/generate-vendor-code/', GenerateVendorCodeView.as_view(), name='generate_vendor_code')`
   - Location: AJAX API Endpoints section

### 4. **Modified: `accounting/forms.py` - QuickAddVendorForm**
   - **vendor_code Widget Changes:**
     - Removed `'required': 'required'` attribute
     - Added `'readonly': 'readonly'` attribute
     - Added `'data-auto-generated': 'true'` data attribute
     - Updated placeholder: "Auto-generated vendor code"
   - **clean_vendor_code() Method:**
     - Now validates that vendor_code is not empty
     - Still validates uniqueness per entity

### 5. **Modified: `accounting/templates/accounting/quick_add_vendor.html`**
   - **JavaScript Implementation:**
     - Auto-runs on DOMContentLoaded
     - Checks if editing existing vendor (skips if vendor_code already populated)
     - Disables field during API fetch (shows "Generating...")
     - Calls `/accounting/api/generate-vendor-code/` endpoint
     - Populates field with returned code
     - Makes field read-only after population
     - Shows "Auto-generated" indicator with edit option
   - **Edit Toggle Function:**
     - User can click "Edit" to override auto-generated code
     - Removes read-only attribute to allow manual entry
     - Field auto-focuses and selects text for easy replacement
   - **CSS Styling:**
     - Added styles for loading state
     - Added styles for override information display
     - Maintains Bootstrap form-control styling

## User Workflow

1. User navigates to `/accounting/quick-add-vendor/`
2. Page loads and JavaScript executes
3. Vendor code field shows "Generating..." while fetching code
4. API returns next sequential code (e.g., VEND-0042)
5. Field populates with code and becomes read-only
6. "Auto-generated: VEND-0042 | Edit" indicator shows below field
7. User fills in other required fields (Name, Currency)
8. User can click "Edit" if they want to use a different code
9. Upon form submission, validation ensures code is unique per entity

## Features

✅ **Auto-Generation:** Sequential VEND-XXXX format
✅ **Entity-Scoped:** Each entity has independent sequence
✅ **Uniqueness:** Maintains existing unique constraint (entity, vendor_code)
✅ **Override Option:** Users can edit if needed
✅ **Read-Only Safety:** Prevents accidental modification
✅ **Loading State:** Visual feedback while generating
✅ **Error Handling:** Graceful fallback if API fails
✅ **Backward Compatible:** Works with existing vendor data
✅ **Edit Mode:** Removes generation when updating existing vendor

## Technical Details

### Code Generation Algorithm
```
1. Query Vendor.objects for the entity ordered by vendor_code DESC
2. Extract sequence number from last vendor code (VEND-0042 → 42)
3. Increment by 1 (42 → 43)
4. Zero-pad to 4 digits with 'VEND-' prefix → VEND-0043
5. If no vendors exist, start with VEND-0001
6. If format is non-standard, start fresh with VEND-0001
```

### API Endpoint
- **URL:** `GET /accounting/api/generate-vendor-code/`
- **Method:** GET
- **Authentication:** LoginRequiredMixin (requires logged-in user)
- **Entity Source:** Django session (`selected_entity_id`)
- **Response (Success):**
  ```json
  {
    "vendor_code": "VEND-0042",
    "entity_id": 7,
    "entity_name": "Zubair Enterprises"
  }
  ```
- **Response (Error - No Entity):**
  ```json
  {
    "error": "No entity selected or entity not found"
  }
  ```
  Status: 404

- **Response (Error - Exception):**
  ```json
  {
    "error": "Error generating vendor code: <error details>"
  }
  ```
  Status: 500

### JavaScript Behavior
1. **On Load:**
   - Check if vendor_code field exists
   - Check if editing (field already has value)
   - If new vendor: disable field, show "Generating..."
   - Fetch code from API

2. **On Success:**
   - Populate field with code
   - Make field read-only
   - Show auto-generated indicator with Edit link

3. **On Failure:**
   - Disable read-only to allow manual entry
   - Show error in placeholder
   - Log error to console

4. **On Edit Click:**
   - Remove read-only attribute
   - Focus field and select all text
   - User can type new code

## Files Modified

1. ✅ `TradifyERP/accounting/vendor_utils.py` - NEW
2. ✅ `TradifyERP/accounting/views.py` - Modified
3. ✅ `TradifyERP/accounting/urls.py` - Modified
4. ✅ `TradifyERP/accounting/forms.py` - Modified
5. ✅ `TradifyERP/accounting/templates/accounting/quick_add_vendor.html` - Modified

## Testing Recommendations

1. **Test Auto-Generation:**
   - Navigate to `/accounting/quick-add-vendor/`
   - Verify code auto-generates on page load
   - Check code format (VEND-XXXX)

2. **Test Entity Isolation:**
   - Create vendors in different entities
   - Verify each entity has independent sequence

3. **Test Override:**
   - Click "Edit" link
   - Enter different vendor code
   - Submit and verify custom code is saved

4. **Test Uniqueness:**
   - Try to submit with duplicate code
   - Verify error message

5. **Test Edit Mode:**
   - Edit existing vendor
   - Verify field is NOT read-only (allows editing)

6. **Test Error Handling:**
   - Check browser console for API errors
   - Verify fallback to manual entry on API failure

## Deployment Notes

1. **Database:** No migrations required (no model changes)
2. **Static Files:** No static file changes
3. **Settings:** No settings changes required
4. **Cache:** Can clear cache if needed (optional)
5. **Server Restart:** Gunicorn restart recommended for code changes

## Rollback Plan

If issues occur:
1. Restore `vendor_utils.py` (delete file)
2. Revert `views.py` changes
3. Revert `urls.py` changes
4. Revert `forms.py` changes
5. Revert `quick_add_vendor.html` changes
6. Restart Gunicorn

Git commands:
```bash
git log --oneline | grep -i "vendor code"
git reset --hard <commit-before-changes>
git push origin <branch> --force
```

## Performance Impact

- **Minimal:** One database query per page load to generate code
- **Query:** Simple query with ordering and limit
- **Cache Opportunity:** Could cache last vendor code if needed
- **No N+1 Problems:** Single query per form load

## Security Considerations

- ✅ LoginRequiredMixin on API endpoint
- ✅ Uses session entity (no entity switching bypass)
- ✅ No user input in generation logic
- ✅ Read-only field prevents accidental modification
- ✅ Form validation still required (unique constraint check)

## Future Enhancements

- Configurable vendor code format (settings)
- Vendor code prefix per vendor type
- Bulk vendor import with auto-code generation
- Code format validation (regex pattern)
- Code history/audit log
