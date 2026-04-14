# Pending in Foreign Bank - Automatic Data Sync Documentation

## Overview
The **"Pending in Foreign Bank"** column in the **Shareholder Investment Report** is automatically populated with pending international transfer amounts from the **International Capital Report**.

## Data Flow Diagram

```
International Capital Report
         ↓
InternationalTransferTracking.destination_amount (₹ INR Amount)
         ↓
ShareholderInvestmentReportView (aggregates by stakeholder)
         ↓
Shareholder Investment Report
"Pending in Foreign Bank" Column
```

## Implementation Details

### 1. **Source Data: International Transfer Tracking**
- **Model**: `InternationalTransferTracking` (accounting/models.py:1249-1315)
- **Key Field**: `destination_amount` (DecimalField, max_digits=15, decimal_places=2)
  - This is the "₹ INR Amount" column shown in the international capital report
  - Represents the amount received in destination currency (INR) after conversion
  - Example: If $1,000 USD converted at 83 INR/USD, destination_amount = ₹83,000

### 2. **Aggregation Logic: ShareholderInvestmentReportView**
- **File**: TradifyERP/shareholder/views.py (lines 741-758, 801-817, 836-853)
- **Query Operation**:
  ```python
  InternationalTransferTracking.objects.filter(
      capital_contribution__entity=entity,
      transfer_status__in=['PENDING_ABROAD', 'IN_TRANSIT', 'RECEIVED_LOCALLY', 'CONVERTED']
  ).select_related('capital_contribution__stakeholder').values_list(
      'capital_contribution__stakeholder_id',
      'destination_amount'
  )
  ```

### 3. **Mapping Process**
For each international transfer:
1. Filter by entity (multi-tenant)
2. Include only non-final statuses:
   - ✅ PENDING_ABROAD
   - ✅ IN_TRANSIT
   - ✅ RECEIVED_LOCALLY
   - ✅ CONVERTED
   - ❌ POSTED_TO_GL (excluded - transfer completed)
   - ❌ CANCELLED (excluded - transfer voided)

3. Aggregate destination_amount by stakeholder_id
4. Pass to template as `pending_in_foreign_bank` in investment_data

### 4. **Display: Investment Report Template**
- **File**: TradifyERP/templates/shareholder/investment_report.html (lines 62-67)
- **Display Format**:
  ```html
  <td>
    {% if investment.pending_in_foreign_bank > 0 %}
      <span class="badge badge-warning">
        ₹ {{ investment.pending_in_foreign_bank|floatformat:2 }}
      </span>
    {% else %}
      —
    {% endif %}
  </td>
  ```

## Status Codes Explained

| Status | Meaning | Included? | Notes |
|--------|---------|-----------|-------|
| PENDING_ABROAD | Money awaiting transfer | ✅ Yes | Pending in source bank |
| IN_TRANSIT | Money in transfer | ✅ Yes | Awaiting receipt in destination |
| RECEIVED_LOCALLY | Money received in India | ✅ Yes | Awaiting conversion/posting |
| CONVERTED | Converted to company currency | ✅ Yes | Awaiting GL posting |
| POSTED_TO_GL | Posted to accounts | ❌ No | Transfer complete - no longer "pending" |
| CANCELLED | Transfer voided | ❌ No | Transfer cancelled - no pending amount |

## Verification API

### Endpoint
```
GET /shareholder/api/international-transfers/sync/
```

### Authentication
- Required: Yes (LoginRequiredMixin)
- Permission: `accounting.view_stakeholder`

### Response Example
```json
{
  "success": true,
  "entity": "Entity Name",
  "sync_status": "ACTIVE - Data auto-syncs from international capital report",
  "statistics": {
    "total_pending_inr": 2500000,
    "total_stakeholders_with_pending": 3,
    "total_transfers_pending": 7,
    "transfer_statuses_included": [
      "PENDING_ABROAD",
      "IN_TRANSIT",
      "RECEIVED_LOCALLY",
      "CONVERTED"
    ],
    "transfer_statuses_excluded": ["POSTED_TO_GL", "CANCELLED"]
  },
  "pending_by_stakeholder": [
    {
      "stakeholder_id": 1,
      "stakeholder_name": "John Smith",
      "total_pending_inr": 1500000,
      "transfer_count": 3
    }
  ],
  "transfer_details": [
    {
      "stakeholder": "John Smith",
      "status": "IN_TRANSIT",
      "source_amount": 15000,
      "destination_amount_inr": 1245000,
      "exchange_rate": 83
    }
  ]
}
```

## How It Works

### Daily Workflow
1. **Shareholder sends international transfer** (e.g., capital contribution)
   - Amount: $15,000 USD
   - Exchange rate: 83 INR/USD

2. **Transfer recorded in International Capital Report**
   - Creates `InternationalTransferTracking` record
   - Sets `destination_amount` = $15,000 × 83 = ₹1,245,000
   - Sets `transfer_status` = "PENDING_ABROAD"

3. **Money transfers and status updates**
   - Status changes: PENDING_ABROAD → IN_TRANSIT → RECEIVED_LOCALLY → CONVERTED
   - `destination_amount` remains ₹1,245,000

4. **Investment Report Auto-Updates**
   - When shareholder opens Investment Report page
   - ShareholderInvestmentReportView queries all pending transfers
   - Sums by stakeholder: John Smith has ₹1,245,000 pending
   - Displays in "Pending in Foreign Bank" column

5. **GL Posting and Completion**
   - Accounts team posts transfer to General Ledger
   - Status changes to: POSTED_TO_GL
   - Amount is NO LONGER "pending" - removed from report

## Important Notes

### ⚠️ What is NOT Included
- ❌ Transfers with status "POSTED_TO_GL" (already completed)
- ❌ Transfers with status "CANCELLED" (voided transfers)
- ❌ Transfers from other entities (multi-tenant filtering)

### ✅ What IS Included
- ✅ All in-flight transfer statuses (PENDING_ABROAD to CONVERTED)
- ✅ Destination amount in INR (after conversion)
- ✅ Only for approved capital contributions
- ✅ Real-time aggregation (no caching)

## Configuration Options

### Filter by Transfer Status
To change which statuses are included, modify ShareholderInvestmentReportView.get_context_data():

```python
transfer_status__in=['PENDING_ABROAD', 'IN_TRANSIT', 'RECEIVED_LOCALLY', 'CONVERTED']
```

Current Include List:
- PENDING_ABROAD
- IN_TRANSIT
- RECEIVED_LOCALLY
- CONVERTED

Current Exclude List:
- POSTED_TO_GL
- CANCELLED

### Decimal Precision
- Database precision: 15 digits, 2 decimal places
- Template display: 2 decimal places (floatformat:2)
- Example: ₹1,245,000.00

## Troubleshooting

### Issue: "No investment data available" message
**Cause**: No investment limits or capital contributions exist
**Solution**: 
1. Create InvestmentLimit record for shareholder
2. OR create CapitalContribution record with APPROVED status

### Issue: Pending amounts not showing
**Cause**: International transfers exist but status not in include list
**Solution**:
1. Check InternationalTransferTracking.transfer_status in database
2. Verify status is one of: PENDING_ABROAD, IN_TRANSIT, RECEIVED_LOCALLY, CONVERTED
3. If status is POSTED_TO_GL, transfer is complete (correct behavior)

### Issue: Amount shows but should be zero
**Cause**: Transfer status updated but view cached
**Solution**:
1. Refresh browser page (Ctrl+F5)
2. Clear Django cache: `python manage.py clear_cache`

## Database Schema

### Key Tables

**InternationalTransferTracking**
```sql
- id: PK
- capital_contribution_id: FK to CapitalContribution
- destination_amount: DECIMAL(15,2) ← Used for "Pending in Foreign Bank"
- transfer_status: VARCHAR ← Filters which transfers are pending
- source_amount: DECIMAL(15,2)
- exchange_rate_used: DECIMAL(15,6)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

**CapitalContribution**
```sql
- id: PK
- stakeholder_id: FK to Stakeholder
- entity_id: FK to Entity
- international_transfer_id: OneToOne to InternationalTransferTracking
- amount: DECIMAL(15,2)
- amount_company_currency: DECIMAL(15,2)
- workflow_status: VARCHAR
```

**Stakeholder**
```sql
- id: PK
- entity_id: FK to Entity
- first_name: VARCHAR
- last_name: VARCHAR
- email: VARCHAR
```

## Recent Changes

### v1.1 (Released: 2026-04-08)
- ✅ Optimized query using `values_list()` for better performance
- ✅ Added InternationalTransferDataSyncAPIView for monitoring
- ✅ Improved aggregation logic with Decimal handling
- ✅ Added API endpoint: `/shareholder/api/international-transfers/sync/`
- ✅ Added comprehensive this documentation

## Code References

### Files Modified
1. `TradifyERP/shareholder/views.py` (Lines 741-758, 801-817, 836-853)
   - ShareholderInvestmentReportView.get_context_data()
   
2. `TradifyERP/shareholder/urls.py` (Added API route)
   - `path('api/international-transfers/sync/', ...)`

3. `TradifyERP/templates/shareholder/investment_report.html` (Lines 62-67)
   - Display template for "Pending in Foreign Bank" column

### Related Models
- `accounting.models.InternationalTransferTracking` (Source of pending amounts)
- `accounting.models.CapitalContribution` (Links transfer to stakeholder)
- `accounting.models.Stakeholder` (Aggregation key)
- `accounting.models.Entity` (Multi-tenant filtering)

## Testing Checklist

- [ ] Navigate to `/shareholder/investment-report/`
- [ ] See "Pending in Foreign Bank" column in investment summary table
- [ ] Verify amounts match international capital report's ₹ INR Amount column
- [ ] Test with multiple shareholders - each should show correct pending total
- [ ] Verify API endpoint: GET `/shareholder/api/international-transfers/sync/`
- [ ] Check API returns statistics matching visible data
- [ ] Update transfer status to POSTED_TO_GL and verify amount disappears from report
- [ ] Create new international transfer and verify updates immediately

## Support

For issues or questions:
1. Check API endpoint: `/shareholder/api/international-transfers/sync/`
2. Review database: `SELECT * FROM accounting_internationaltransfertracking`
3. Verify stakeholder mapping: `SELECT * FROM accounting_capitalcontribution WHERE stakeholder_id = ?`
4. Check template rendering: `/shareholder/investment-report/`

---

**Last Updated**: 2026-04-08  
**Status**: ACTIVE & OPERATIONAL  
**Auto-Sync**: ENABLED  
