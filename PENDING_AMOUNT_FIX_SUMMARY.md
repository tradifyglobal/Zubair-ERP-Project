# Pending Amount Calculation Fix - Summary

## Issue
The pending amount badge on the Capital Contributions list page was showing an incorrect total (₹27,063.00) instead of the correct amount based on table data.

## Root Cause
The code was summing the `amount` field (amount in source/original currency) instead of `amount_company_currency` (amount converted to company currency). The table displays converted amounts, creating an inconsistency between what users see in the table vs. the badge.

### Example Data
- Table showed 5 pending contributions with converted amounts:
  - ₹312,500.00
  - ₹500,000.00
  - ₹500,000.00
  - ₹218,750.00
  - ₹160,187.50
  - **Expected Total: ₹1,691,437.50**

- Badge was showing: ₹27,063.00 (sum of source currency amounts)

## Solution
Changed line 357 in `TradifyERP/shareholder/views.py`:

```python
# Before (INCORRECT)
context['pending_total'] = base_queryset.filter(status='PENDING').aggregate(total=Sum('amount'))['total'] or 0

# After (CORRECT)
context['pending_total'] = base_queryset.filter(status='PENDING').aggregate(total=Sum('amount_company_currency'))['total'] or 0
```

### Why This Fix Works
1. **Field Consistency**: Uses the same `amount_company_currency` field that the table displays
2. **Currency Alignment**: All amounts shown to users are in company currency (₹)
3. **Logic Consistency**: Now both `pending_total` and `completed_total` use `amount_company_currency`

## Files Modified
- `TradifyERP/shareholder/views.py` - Line 357

## Deployment Status
✅ **Committed and Pushed to GitHub**
- Commit: `c04f269` - "Fix: Change pending amount calculation to use amount_company_currency for consistency with display"
- Branch: `changes`
- Status: Ready to pull and deploy to production

## Deployment Instructions

### Option 1: Direct Pull from GitHub (Recommended for Production)
```bash
cd /var/www/tradifyerp
git pull origin changes
sudo systemctl restart gunicorn_tradifyerp
```

### Option 2: Manual File Update
Copy the updated file from GitHub or local directory:
```bash
scp /path/to/TradifyERP/shareholder/views.py root@<server_ip>:/var/www/tradifyerp/TradifyERP/shareholder/views.py
sudo systemctl restart gunicorn_tradifyerp
```

## Testing
After deployment, verify by:
1. Navigating to Capital Contributions list page
2. Creating new PENDING capital contributions if needed
3. Checking that the pending amount badge now matches the sum of "Converted Amount" column
4. Verifying the pending total reflects amounts in company currency (₹)

## Database Note
No database migrations required. This is purely a calculation fix in the view logic.

## Related Files
- Model: `TradifyERP/accounting/models.py` - CapitalContribution model (lines 805-1000)
- Template: Uses `context['pending_total']` for display
- Fields Involved:
  - `amount` - Original currency amount
  - `amount_company_currency` - Converted to company currency
  - `currency` - Source currency
  - `exchange_rate` - Conversion rate used

## Verification Checklist
- [ ] Code change verified in views.py line 357
- [ ] Commit pushed to GitHub
- [ ] File deployed to production server
- [ ] Gunicorn restarted
- [ ] Capital contributions list page loads without errors
- [ ] Pending amount badge shows correct total
- [ ] Table and badge amounts are now consistent
