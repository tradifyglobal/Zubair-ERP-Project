# P2P GL Posting - Quick Reference Guide

## Access Dashboard

**Main P2P Dashboard**: `http://192.168.20.10/procurement/p2p/`

---

## Complete P2P Flow Example

### Step 1: Create Purchase Order

**URL**: `/procurement/po/create/`

```
Fields Required:
- Supplier: Select supplier
- Entity: Select entity  
- PO Number: AUTO or manual
- Expected Delivery Date
- Total Amount

Status: ISSUED
GL Impact: NONE (no GL entries at PO stage)
```

### Step 2: Create Goods Receipt

**URL**: `/procurement/receipts/create/`

```
Fields Required:
- Purchase Order: Link to PO above
- Entity: Same as PO
- Line Items: Raw materials received

Status: CREATED (initial)

Then: CHANGE STATUS TO "ACCEPTED"
→ Signal triggers GL posting
→ GL Entry: DR Inventory (1041) / CR GR/IR (2091)
```

### Step 3: Create Vendor Invoice

**URL**: `/ap/vendor-bill/create/`

```
Fields Required:
- Supplier: Same as PO
- Bill Number
- Invoice Amount
- Purchase Order: Link to PO
- Entity: Same as PO

Status: DRAFT

Then: CHANGE STATUS TO "MATCHED" (after 3-way match)
→ Signal triggers GL posting
→ GL Entry: DR GR/IR (2091) / CR AP (2010)
```

### Step 4: Create Vendor Payment

**URL**: `/ap/vendor-payment/create/`

```
Fields Required:
- Supplier: Same as PO
- Payment Number
- Amount Paid
- Purchase Orders: Link to PO
- Entity: Same as PO

Status: PENDING

Then: CHANGE STATUS TO "PAID"
→ Signal triggers GL posting  
→ GL Entry: DR AP (2010) / CR Bank (1010)
```

### Result: Complete P2P with GL Entries

```
PO:      No GL entries (commitment)
GRN:     GL Entry 1 - DR 1041 / CR 2091
Invoice: GL Entry 2 - DR 2091 / CR 2010
Payment: GL Entry 3 - DR 2010 / CR 1010

Total Effect:
DR 1041 (Inventory) = GRN amount
CR 1010 (Bank) = Payment amount
```

---

## Dashboard Navigation

### Main Dashboard (`/procurement/p2p/`)

**Shows**:
1. Pipeline cards (PO, GRN, Invoice, Payment counts)
2. GL posting status (posted vs pending)
3. Amount progression
4. Status breakdown tables
5. Recent documents

**Filter**:
- Entity selector at top
- Refreshes all data when changed

### PO Details (`/procurement/p2p/<po_id>/`)

**Shows**:
- PON details (amounts, dates)
- All linked GRNs with GL status
- All linked Invoices with GL status
- All linked Payments with GL status
- GL entries at each stage

### Comparison View (`/procurement/p2p-comparison/`)

**Shows**:
- All POs in table format
- Receipt/Invoice/Payment completion %
- GL posting completion status
- Discrepancy indicators

---

## Troubleshooting

### Problem: GL Entry Not Created After Accept/Match/Pay

**Causes**:
1. Signal not registered (check logs)
2. GL account doesn't exist (should auto-create)
3. Status change didn't save properly

**Solution**:
```bash
# Check logs
ssh zubair@192.168.20.10
sudo tail -f /var/log/gunicorn/error.log | grep "GL"

# or manually trigger GL posting in shell:
cd /var/www/tradifyerp
/var/www/tradifyerp/venv/bin/python manage.py shell

# Import and trigger
from procurement.models import GoodsReceipt
from procurement.gl_posting import P2PGLPosting

grn = GoodsReceipt.objects.filter(gl_entry__isnull=True, status='ACCEPTED').first()
if grn:
    gl_entry = P2PGLPosting.post_goods_receipt(grn)
    grn.gl_entry = gl_entry
    grn.save()
    print(f"Manual GL posting: {gl_entry.id}")
```

### Problem: Can't see documents on dashboard

**Check**:
1. Verify entity filter matches your documents' entity
2. Check if documents are in correct status
3. Refresh page (Ctrl+R)

### Problem: Duplicate GL entries

**Should not happen** - Signals check `if not instance.gl_entry` before posting
- If duplicates exist, they're from manual creation
- Check and remove duplicates from accounting app

---

## GL Account Numbers Reference

```
1010  Bank Account (Asset)
1041  Raw Material Inventory (Asset)  
2010  Accounts Payable (Liability)
2091  GR/IR Clearing (Liability)
```

## Document Status Flow

**Purchase Order**:
```
DRAFT → ISSUED → RECEIVED → CLOSED
(no GL entries)
```

**Goods Receipt**:
```
CREATED → ACCEPTED [GL POSTING] → CLOSED
         ✓ GL entry created
```

**Vendor Bill**:
```
DRAFT → APPROVED → MATCHED [GL POSTING] → PAID
                  ✓ GL entry created
```

**Vendor Payment**:
```
PENDING → AUTHORIZED → PAID [GL POSTING] → SETTLED
                      ✓ GL entry created
```

---

## Useful Commands

### Check Recent GL Entries

```bash
ssh zubair@192.168.20.10
cd /var/www/tradifyerp
/var/www/tradifyerp/venv/bin/python manage.py shell

from accounting.models import LedgerEntry
le = LedgerEntry.objects.order_by('-created_at').first()
print(f"Latest GL Entry: {le.id}")
print(f"Amount: {le.total_debit}")
print(f"Linked to: {le.goods_receipt or le.vendor_bill or le.vendor_payment}")
```

### Check If Signal Imported

```bash
# In Django shell
from procurement import signals
print("Signals imported successfully")
```

### List All GL Entries with Documents

```bash
# In Django shell
from accounting.models import LedgerEntry

grn_les = LedgerEntry.objects.filter(goods_receipt__isnull=False).count()
bill_les = LedgerEntry.objects.filter(vendor_bill__isnull=False).count()
pay_les = LedgerEntry.objects.filter(vendor_payment__isnull=False).count()

print(f"GRN GL Entries: {grn_les}")
print(f"Bill GL Entries: {bill_les}")
print(f"Payment GL Entries: {pay_les}")
```

---

## Configuration (All Done ✅)

### Required Files Deployed:
- ✅ `procurement/gl_posting.py`
- ✅ `procurement/signals.py`
- ✅ `procurement/apps.py`
- ✅ `ap/apps.py`

### Database Tables Ready:
- ✅ GoodsReceipt.gl_entry (FK to LedgerEntry)
- ✅ VendorBill.gl_entry (FK to LedgerEntry)
- ✅ VendorPayment.gl_entry (FK to LedgerEntry)

### Django Signals Registered:
- ✅ Procurement app loads signals.py on ready()
- ✅ AP app loads signals.py on ready()

### API Endpoints Ready:
- ✅ `/procurement/p2p/` - Dashboard
- ✅ `/procurement/p2p/<pk>/` - Details
- ✅ `/procurement/p2p-comparison/` - Comparison

---

## Performance Notes

- Dashboard loads ~5-10 documents per view
- Queries use aggregation for performance
- GL posting typically completes in <1 second
- No blocking on GL posting (happens after save)

---

## Security Notes

- ✅ All views use Django authentication by default
- ✅ CSRF protected via Django middleware
- ✅ Database FK constraints ensure referential integrity
- ✅ GL entries are immutable (created once, not edited)

---

## Support & Documentation

- **Full Guide**: `GL_POSTING_IMPLEMENTATION_GUIDE.md`
- **Deployment Summary**: `DEPLOYMENT_SUMMARY_GL_POSTING.md`
- **Test Scripts**: `test_gl_posting.py`, `verify_gl_posting.py`

---

**System Status**: ✅ LIVE AND READY  
**Last Update**: 2026-04-08  
**Version**: 1.0 (Production)
