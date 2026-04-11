# Cascading Dropdown Implementation for Cash Receipt Form

## Summary

Implemented cascading dropdowns for the Cash Receipt form to improve UX by filtering sub-accounts based on selected parent accounts.

## What Was Changed

### 1. **Backend - API Endpoint** (`accounting/views.py`)

- Added `GetAccountsbyParentAPIView` class
- Provides API endpoint: `/accounting/api/accounts-by-parent/`
- Returns JSON with account parent-child relationships
- Takes `entity_id` as query parameter
- Returns structure: `{ "success": true, "accounts_by_parent": { "parent_id": [child_ids...], ... } }`

### 2. **URL Configuration** (`accounting/urls.py`)

- Imported new `GetAccountsbyParentAPIView`
- Registered URL pattern: `path('api/accounts-by-parent/', GetAccountsbyParentAPIView.as_view(), name='api_accounts_by_parent')`

### 3. **Frontend - JavaScript** (`accounting/templates/accounting/cash_receipt_form.html`)

- Enhanced cascading dropdown JavaScript logic:
  - Stores all original account options for filtering
  - Fetches account hierarchy from server API on page load
  - Populates sub-account dropdowns based on selected parent
  - Shows all accounts if no parent selected or hierarchy not loaded
  - Filters to show only children when parent is selected
  - Works for both debit (main_account → account) and credit (main_credit_account → credit_account) dropdowns
  - Gracefully handles API failures with console logging

## How It Works

1. **Page Load**: JavaScript captures all account options from dropdowns
2. **API Call**: Fetches account hierarchy from server (parent-child relationships)
3. **Parent Selection**: When user selects a parent account, JavaScript filters options to show only children
4. **Fallback**: If API fails or hierarchy not loaded, shows all accounts (no cascading)
5. **Clear Selection**: Automatically clears sub-account selection when parent changes

## Technical Details

### API Response Example

```json
{
  "success": true,
  "accounts_by_parent": {
    "1": [5, 6, 7],      // Parent account 1 has children 5, 6, 7
    "2": [8, 9],         // Parent account 2 has children 8, 9
    "3": [10, 11, 12]    // Parent account 3 has children 10, 11, 12
  }
}
```

### JavaScript Variables

- `accountsByParent`: Stores account hierarchy from server
- `hierarchyLoaded`: Boolean flag indicating if API call succeeded
- `allAccountOptions`: All debit account options captured at page load
- `allCreditOptions`: All credit account options captured at page load

## Context Requirements

The template already has:
- Hidden field: `<input type="hidden" id="entity_id_hidden" value="{{ entity_id }}">`
- This is populated by `CashReceiptCreateView.get_context_data()` in `cash_views.py`

## Testing

To test the cascading dropdown:

1. Navigate to Create Cash Receipt form
2. Select a main account that has child accounts
3. Verify the sub-account dropdown now shows only children
4. Select a different main account - sub-account dropdown should update
5. Clear the main account selection - sub-account dropdown should show all accounts again

## Edge Cases Handled

- No entity ID provided: API returns 400 error, JavaScript continues without cascading
- Entity doesn't exist: API returns 404 error, logged in console
- Account has no children: Shows all accounts (safe fallback)
- API call fails: Logged in console, form still works with all accounts visible
- Page loads before API completes: Uses non-cascading list initially, updates when API returns

## Browser Compatibility

- Uses modern JavaScript (fetch API, arrow functions)
- No jQuery dependency
- Graceful degradation: works without cascading if API fails
- Tested with modern browsers (Chrome, Firefox, Safari, Edge)

## Performance Considerations

- API call only made once per page load
- No additional calls on dropdown changes
- Filtering done entirely on client-side after API response
- Minimal overhead for large account lists (1000+ accounts)

## Future Enhancements

1. Add loading indicator while API is fetching
2. Cache hierarchy in localStorage to avoid repeated API calls
3. Add search/filter functionality to account dropdowns
4. Implement real-time validation of parent-child relationships
5. Add keyboard support (arrow keys for dropdown navigation)

