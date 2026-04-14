#!/usr/bin/env python
"""Quick GL Posting System Verification"""

from procurement.models import GoodsReceipt, PurchaseOrder
from ap.models import VendorBill, VendorPayment
from accounting.models import LedgerEntry
from procurement.gl_posting import P2PGLPosting

print("\n" + "="*70)
print("GL POSTING SYSTEM VERIFICATION")
print("="*70 + "\n")

# Test 1: Check signal imports
try:
    from procurement import signals
    print("[✓] Signals module successfully imported")
except Exception as e:
    print(f"[✗] Failed to import signals: {e}")

# Test 2: Check GL posting utility
try:
    print("[✓] GL Posting utility available")
except Exception as e:
    print(f"[✗] Failed to import GL posting utility: {e}")

# Test 3: Document counts
po_count = PurchaseOrder.objects.count()
grn_count = GoodsReceipt.objects.count()
bill_count = VendorBill.objects.count()
payment_count = VendorPayment.objects.count()
le_count = LedgerEntry.objects.count()

print(f"\n[*] Document Counts:")
print(f"  - Purchase Orders: {po_count}")
print(f"  - Goods Receipts: {grn_count}")
print(f"  - Vendor Bills: {bill_count}")
print(f"  - Vendor Payments: {payment_count}")
print(f"  - GL Entries (total): {le_count}")

# Test 4: GL entry links
grn_with_gl = GoodsReceipt.objects.filter(gl_entry__isnull=False).count()
bill_with_gl = VendorBill.objects.filter(gl_entry__isnull=False).count()
payment_with_gl = VendorPayment.objects.filter(gl_entry__isnull=False).count()

print(f"\n[*] GL Entry Status:")
print(f"  - GRNs with GL entries: {grn_with_gl}/{grn_count}")
print(f"  - Bills with GL entries: {bill_with_gl}/{bill_count}")
print(f"  - Payments with GL entries: {payment_with_gl}/{payment_count}")

# Test 5: Show recent GRN with GL
if grn_count > 0:
    grn = GoodsReceipt.objects.order_by('-created_at').first()
    print(f"\n[*] Recent GRN:")
    print(f"  - Number: {grn.receipt_number}")
    print(f"  - Status: {grn.status}")
    print(f"  - GL Entry: {grn.gl_entry.id if grn.gl_entry else 'None'}")

# Test 6: Show recent Bills with GL
if bill_count > 0:
    bill = VendorBill.objects.order_by('-created_at').first()
    print(f"\n[*] Recent Bill:")
    print(f"  - Number: {bill.bill_number}")
    print(f"  - Status: {bill.status}")
    print(f"  - GL Entry: {bill.gl_entry.id if bill.gl_entry else 'None'}")

print("\n" + "="*70)
print("VERIFICATION COMPLETE")
print("="*70 + "\n")
