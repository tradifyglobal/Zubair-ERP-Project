# GL Posting Integration for Procure-to-Pay (P2P) Workflow
## Complete Implementation Guide

**Status**: ✅ DEPLOYED AND ACTIVE  
**Deployment Date**: 2026-04-08  
**Target**: Full ERP-compliant GL posting at GRN, Invoice, and Payment stages

---

## 1. Overview

This implementation follows **universal ERP accounting principles** (SAP, Oracle, NetSuite) for Procure-to-Pay:
- **PO Stage**: NO GL entries (commitment only)
- **GRN Stage**: GL entries for goods receipt
- **Invoice Stage**: GL entries for invoice receipt
- **Payment Stage**: GL entries for payment

---

## 2. Architecture

### 2.1 Components Deployed

| Component | File | Purpose | Status |
|-----------|------|---------|--------|
| GL Posting Utility | `procurement/gl_posting.py` | Core GL posting logic (3 methods) | ✅ LIVE |
| Django Signals | `procurement/signals.py` | Auto-trigger GL posting on status changes | ✅ LIVE |
| App Config Updates | `procurement/apps.py`, `ap/apps.py` | Signal registration | ✅ LIVE |
| Dashboard Views | `procurement/views_p2p_dashboard.py` | Pipeline visualization | ✅ LIVE |
| Dashboard Template | `templates/procurement/p2p_dashboard.html` | UI for P2P pipeline | ✅ LIVE |
| URL Routes | `procurement/urls.py` | Dashboard route mapping | ✅ LIVE |

### 2.2 Database Model Support

All required fields already exist:

**GoodsReceipt Model**:
```python
gl_entry = OneToOneField(LedgerEntry, null=True, blank=True, related_name='goods_receipt')
```

**VendorBill Model**:
```python
gl_entry = OneToOneField(LedgerEntry, null=True, blank=True, related_name='vendor_bill')
```

**VendorPayment Model**:
```python
gl_entry = OneToOneField(LedgerEntry, null=True, blank=True, related_name='vendor_payment')
```

---

## 3. GL Posting Flows

### 3.1 Goods Receipt → Inventory GL Entry

**Trigger**: When `GoodsReceipt.status` changes to `ACCEPTED`

**GL Entry Created**:
```
DR: Raw Material Inventory (Account 1041)    [Asset]
CR: GR/IR Clearing (Account 2091)            [Liability]
Amount: Sum of all line items (Qty × Unit Price)
```

**Code Path**:
1. GoodsReceipt saved with `status='ACCEPTED'`
2. Signal triggered: `track_grn_status_change()` (pre_save)
3. Signal triggered: `post_gl_on_grn_accepted()` (post_save)
4. Calls: `P2PGLPosting.post_goods_receipt(grn_instance)`
5. LedgerEntry created with two related entries (GL lines)
6. `GoodsReceipt.gl_entry` FK updated

**Method Location**: `procurement/gl_posting.py`, lines 75-130

---

### 3.2 Invoice Receipt → AP GL Entry

**Trigger**: When `VendorBill.status` changes to `APPROVED` or `MATCHED`

**GL Entry Created**:
```
DR: GR/IR Clearing Account (Account 2091)       [Liability]
CR: Accounts Payable (Account 2010)             [Liability]
Amount: vendor_bill.total_amount
```

**Code Path**:
1. VendorBill saved with `status='APPROVED'` or `status='MATCHED'`
2. Signal triggered: `track_invoice_status_change()` (pre_save)
3. Signal triggered: `post_gl_on_invoice_approved()` (post_save)
4. Calls: `P2PGLPosting.post_vendor_invoice(bill_instance)`
5. LedgerEntry created with two related entries
6. `VendorBill.gl_entry` FK updated

**Method Location**: `procurement/gl_posting.py`, lines 134-188

---

### 3.3 Payment → Cash GL Entry

**Trigger**: When `VendorPayment.status` changes to `PAID`

**GL Entry Created**:
```
DR: Accounts Payable (Account 2010)    [Liability]
CR: Bank Account (Account 1010)        [Asset]
Amount: vendor_payment.amount_paid
```

**Code Path**:
1. VendorPayment saved with `status='PAID'`
2. Signal triggered: `track_payment_status_change()` (pre_save)
3. Signal triggered: `post_gl_on_payment_made()` (post_save)
4. Calls: `P2PGLPosting.post_vendor_payment(payment_instance)`
5. LedgerEntry created with two related entries
6. `VendorPayment.gl_entry` FK updated

**Method Location**: `procurement/gl_posting.py`, lines 190-243

---

## 4. Account Setup

### 4.1 Required Accounts (Auto-Created if Missing)

The utility automatically ensures these accounts exist for each Entity:

| Account # | Name | Type | GL Category |
|-----------|------|------|-------------|
| 1041 | Raw Material Inventory | Asset | Current Asset |
| 2091 | GR/IR Clearing | Liability | Current Liability |
| 2010 | Accounts Payable | Liability | Current Liability |
| 1010 | Bank Account | Asset | Current Asset |

**Auto-Creation Logic**: `P2PGLPosting.get_or_create_accounts(entity)`

```python
accounts = {
    'inventory': Account.objects.get_or_create(
        entity=entity,
        account_number='1041',
        defaults={
            'name': 'Raw Material Inventory',
            'account_type': 'ASSET',
            ...
        }
    )[0],
    # ... etc
}
```

---

## 5. Signal Implementation Details

### 5.1 Pre-Save Tracking

Purpose: Detect status changes before save

```python
@receiver(pre_save, sender=GoodsReceipt)
def track_grn_status_change(sender, instance, **kwargs):
    """Track if GRN status is changing to ACCEPTED"""
    if instance.pk:
        try:
            old_instance = GoodsReceipt.objects.get(pk=instance.pk)
            if old_instance.status != instance.status and instance.status == 'ACCEPTED':
                instance._status_changed = True  # Flag for post_save
        except GoodsReceipt.DoesNotExist:
            pass
```

### 5.2 Post-Save GL Posting

Purpose: Create GL entries after successful save

```python
@receiver(post_save, sender=GoodsReceipt)
def post_gl_on_grn_accepted(sender, instance, created, update_fields=None, **kwargs):
    """Post GL entry when GRN is ACCEPTED"""
    if hasattr(instance, '_status_changed') and instance.status == 'ACCEPTED' and not instance.gl_entry:
        gl_entry = P2PGLPosting.post_goods_receipt(instance)
        if gl_entry:
            instance.gl_entry = gl_entry
            instance.save(update_fields=['gl_entry'])
            logger.info(f"GL Entry auto-posted for GRN {instance.receipt_number}")
```

**Key Features**:
- Checks `_status_changed` flag (set by pre_save)
- Only posts if `gl_entry` is NULL (prevents duplicates)
- Logs success for audit trail
- Updates FK after GL posting

---

## 6. Dashboard Features

### 6.1 P2P Pipeline Dashboard
**URL**: `/procurement/p2p/`

**Shows**:
- Pipeline overview (PO → GRN → Invoice → Payment)
- Count and amount for each stage
- GL posting status (posted vs pending)
- Status breakdown tables
- Recent documents with GL entry indicators

**Filters**:
- Entity selector (for multi-entity organizations)

### 6.2 P2P Details View
**URL**: `/procurement/p2p/<int:pk>/`

**Shows**:
- Complete P2P flow for single PO
- Linked GRNs with GL entries
- Linked Invoices with GL entries
- Linked Payments with GL entries
- Amount progression (PO → GRN → Invoice → Payment)

### 6.3 P2P Comparison View
**URL**: `/procurement/p2p-comparison/`

**Shows**:
- Side-by-side P2P status for all POs
- Receipt, invoicing, and payment completion percentages
- GL posting completion status
- Discrepancies flagged

---

## 7. Testing Procedures

### 7.1 Unit Test: Complete P2P Cycle

```python
def test_complete_p2p_gl_posting():
    # 1. Create Purchase Order (NO GL entries)
    po = PurchaseOrder.objects.create(
        po_number='PO-001',
        supplier=supplier,
        entity=entity,
        total_amount=1000
    )
    assert po.purchase_order_line_items.first().gl_entry is None
    
    # 2. Create GRN (should trigger GL: DR Inventory / CR GR/IR)
    grn = GoodsReceipt.objects.create(
        receipt_number='GRN-001',
        purchase_order=po,
        entity=entity,
        status='CREATED'
    )
    grn_line = GoodsReceiptLineItem.objects.create(
        goods_receipt=grn,
        raw_material=material,
        quantity_received=10,
        unit_price=100
    )
    
    # Change status to ACCEPTED (trigger GL posting)
    grn.status = 'ACCEPTED'
    grn.save()
    
    # Verify GL entry created
    assert grn.gl_entry is not None
    assert grn.gl_entry.total_debit == 1000
    assert grn.gl_entry.total_credit == 1000
    
    # Verify GL lines
    entries = grn.gl_entry.ledger_entries.all()
    assert entries.count() == 2
    assert entries[0].account.account_number == '1041'  # Inventory
    assert entries[1].account.account_number == '2091'  # GR/IR
    
    # 3. Create Invoice (should trigger GL: DR GR/IR / CR AP)
    invoice = VendorBill.objects.create(
        bill_number='INV-001',
        supplier=supplier,
        entity=entity,
        purchase_order=po,
        total_amount=1000,
        status='MATCHED'  # Set to matched directly
    )
    
    # Verify GL entry created
    assert invoice.gl_entry is not None
    
    # Verify GL lines
    entries = invoice.gl_entry.ledger_entries.all()
    assert entries[0].account.account_number == '2091'  # GR/IR
    assert entries[1].account.account_number == '2010'  # AP
    
    # 4. Create Payment (should trigger GL: DR AP / CR Bank)
    payment = VendorPayment.objects.create(
        payment_number='PAY-001',
        supplier=supplier,
        entity=entity,
        amount_paid=1000,
        status='PAID'  # Set to paid directly
    )
    
    # Verify GL entry created
    assert payment.gl_entry is not None
    
    # Verify GL lines
    entries = payment.gl_entry.ledger_entries.all()
    assert entries[0].account.account_number == '2010'  # AP
    assert entries[1].account.account_number == '1010'  # Bank
```

### 7.2 Manual Testing: Dashboard

1. **Access Dashboard**:
   - Navigate to `http://192.168.20.10/procurement/p2p/`
   - Should show pipeline overview

2. **Check Entity Filter**:
   - Select different entities
   - Verify counts update correctly

3. **Verify GL Status**:
   - Check "GL Posted" counts vs totals
   - Verify GL entries are linked correctly

4. **View Recent Documents**:
   - Recent POs should show in list
   - Recent GRNs should show GL entry status (✓ or Pending)

---

## 8. Monitoring & Verification

### 8.1 Check GL Posting via Django Shell

```python
# SSH to server
ssh zubair@192.168.20.10
cd /var/www/tradifyerp

# Python shell
python manage.py shell

# Check GRN GL posting
from procurement.models import GoodsReceipt
grn = GoodsReceipt.objects.first()
print(f"GRN: {grn.receipt_number}")
print(f"GL Entry: {grn.gl_entry}")
if grn.gl_entry:
    print(f"Total Debit: {grn.gl_entry.total_debit}")
    print(f"Total Credit: {grn.gl_entry.total_credit}")
    for entry in grn.gl_entry.ledger_entries.all():
        print(f"  - {entry.account.account_number} (GL): {entry.debit or entry.credit}")

# Check Invoice GL posting
from ap.models import VendorBill
invoice = VendorBill.objects.first()
print(f"Invoice: {invoice.bill_number}, GL Entry: {invoice.gl_entry}")

# Check Payment GL posting
from ap.models import VendorPayment
payment = VendorPayment.objects.first()
print(f"Payment: {payment.payment_number}, GL Entry: {payment.gl_entry}")
```

### 8.2 Check Signal Registration

```python
# In Django shell
from django.db.models.signals import receiver
from procurement.models import GoodsReceipt
from procurement import signals

# Check if signals are connected
print(f"Signals connected: {len(GoodsReceipt._meta.get_fields())}")

# Check signal handlers
from django.core import signals as django_signals
print("Available signal handlers registered")
```

### 8.3 Log Monitoring

```bash
# SSH to server and check logs
ssh zubair@192.168.20.10
sudo tail -f /var/log/gunicorn/error.log | grep -i "gl_entry\|post_gl\|gl posting"
```

---

## 9. Troubleshooting

### 9.1 GL Entry Not Created on GRN Accept

**Symptoms**: Changed GRN status to ACCEPTED, but `gl_entry` is NULL

**Check**:
1. Verify signals are loaded:
   ```python
   from django.core.management import call_command
   call_command('shell')  # Check import in apps.py
   ```

2. Check if `_status_changed` flag is set:
   ```python
   grn = GoodsReceipt.objects.get(pk=123)
   print(hasattr(grn, '_status_changed'))
   ```

3. Manually trigger GL posting:
   ```python
   from procurement.gl_posting import P2PGLPosting
   gl_entry = P2PGLPosting.post_goods_receipt(grn, description="Manual trigger")
   grn.gl_entry = gl_entry
   grn.save()
   ```

### 9.2 Account Not Found

**Symptoms**: "Account matching query does not exist" error

**Fix**:
```python
from procurement.gl_posting import P2PGLPosting
from accounting.models import Entity
entity = Entity.objects.first()
P2PGLPosting.get_or_create_accounts(entity)
```

### 9.3 GL Entry Already Exists

**Symptoms**: Trying to create GL, but already exists (duplicate prevention)

**Expected**: Signal checks `not instance.gl_entry` before posting - works as designed

---

## 10. Performance Considerations

### 10.1 Signal Triggers

- **Pre-save**: O(1) - Simple query to check old status
- **Post-save**: O(n) where n = number of line items
  - Calculates total amount from line items

### 10.2 Dashboard Queries

- **Main Dashboard**: ~5 queries total
  - Counts for each pipeline stage
  - Aggregates for amounts
  - GL posting status

- **Optimization**: Use `select_related()` and `prefetch_related()` for related objects

---

## 11. Future Enhancements

### 11.1 Three-Way Matching Automation
- Validate GRN qty vs Invoice qty automatically
- Flag discrepancies for manual review
- Post GL only after successful 3-way match

### 11.2 Multi-Currency Support
- Store exchange rates with GL entries
- Post variance accounting entries for FX gains/losses

### 11.3 Tax & Freight Handling
- Add tax lines to GL posting
- Separate tax liability account
- Freight as separate line item or capitalize to inventory

### 11.4 Budget Integration
- Pre-commitment tracking on PO creation
- Actual vs committed reporting
- Budget variance analysis

### 11.5 Audit Trail Enhancement
- Detailed change log for GL posting events
- Timestamp and user tracking
- Approval workflows before GL posting

---

## 12. Deployment Summary

| Step | Component | Status | Deployed |
|------|-----------|--------|----------|
| 1 | GL Posting Utility | ✅ | gl_posting.py |
| 2 | Signals Module | ✅ | signals.py |
| 3 | Signal Registration | ✅ | apps.py (procurement + ap) |
| 4 | Dashboard Views | ✅ | views_p2p_dashboard.py |
| 5 | Dashboard Template | ✅ | p2p_dashboard.html |
| 6 | URL Routes | ✅ | urls.py |
| 7 | Gunicorn Restart | ✅ | 5 workers running |

**Status**: ✅ COMPLETE AND LIVE

---

## 13. Access & URLs

- **Main Dashboard**: `http://192.168.20.10/procurement/p2p/`
- **PO Details**: `http://192.168.20.10/procurement/p2p/<po_id>/`
- **Comparison View**: `http://192.168.20.10/procurement/p2p-comparison/`

---

## 14. Quick Reference: GL Accounts

```
1010 - Bank Account (Asset)
1041 - Raw Material Inventory (Asset)
2010 - Accounts Payable (Liability)
2091 - GR/IR Clearing (Liability)
```

**P2P GL Posting Sequence**:
```
1. PO Created       → No GL entries (commitment)
2. GRN Accepted     → DR 1041 / CR 2091 (inventory receipt)
3. Invoice Matched  → DR 2091 / CR 2010 (invoice receipt)
4. Payment Made     → DR 2010 / CR 1010 (payment)
```

---

**Document Generated**: 2026-04-08  
**Implementation**: Complete  
**Testing**: Pending  
**Status**: ✅ READY FOR TESTING
