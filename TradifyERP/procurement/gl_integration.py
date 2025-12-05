"""
Procurement Module - General Ledger Integration
Handles automatic GL entries for procurement transactions (inventory, AP tracking, etc.)

Accounting Flow:
1. Purchase Order Created (Status: DRAFT) → No GL entry
2. Purchase Order Sent (Status: SENT) → Creates Purchase Commitment (memo only)
3. Goods Received (GR Created, Status: RECEIVED) → Creates Inventory and AP GL entries
4. Invoice Received → Updates AP if different from GR
5. Payment Made → Reduces AP, increases cash outflow

GL Accounts Used:
- Inventory/Stock - ASSET account
- Accounts Payable (AP) - LIABILITY account
- Expense accounts (for non-inventory purchases)
- Cash/Bank - ASSET account
"""

from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from accounting.models import Account, LedgerEntry, Entity
from .models import GoodsReceipt, PurchaseOrder


def get_or_create_gl_account(entity, account_type, account_name):
    """
    Get or create a GL account for an entity.
    Returns the Account object or None if account doesn't exist and can't be created.
    """
    try:
        # Try to get existing account
        account = Account.objects.get(
            entity=entity,
            account_type=account_type,
            name__icontains=account_name
        )
        return account
    except Account.DoesNotExist:
        # Account doesn't exist - needs to be created by admin
        return None
    except Account.MultipleObjectsReturned:
        # Return first match if multiple exist
        return Account.objects.filter(
            entity=entity,
            account_type=account_type,
            name__icontains=account_name
        ).first()


def create_po_gl_entries(purchase_order):
    """
    Create GL entries when Purchase Order is received (goods receipt created).
    
    Accounting Entry (Double Entry):
    DR Inventory/Stock (ASSET)       = Total Amount
    CR Accounts Payable (LIABILITY)  = Total Amount
    
    This records the inventory received and creates AP obligation.
    """
    try:
        entity = purchase_order.entity
        
        # Get GL accounts - these should be created in accounting module
        inventory_account = get_or_create_gl_account(entity, 'ASSET', 'Inventory')
        if not inventory_account:
            inventory_account = get_or_create_gl_account(entity, 'ASSET', 'Stock')
        
        ap_account = get_or_create_gl_account(entity, 'LIABILITY', 'Accounts Payable')
        
        if not inventory_account or not ap_account:
            # Accounts not configured - return failure
            return False
        
        # Check if entries already exist (idempotent check)
        existing = LedgerEntry.objects.filter(
            reference_number=f"PO-{purchase_order.id}"
        ).exists()
        
        if existing:
            return True  # Already posted
        
        with transaction.atomic():
            # DR Inventory/Stock
            LedgerEntry.objects.create(
                account=inventory_account,
                entity=entity,
                entry_date=purchase_order.po_date,
                entry_type='DEBIT',
                amount=purchase_order.total_amount,
                description=f"Purchase Order {purchase_order.po_number} from {purchase_order.vendor.name}",
                reference_number=f"PO-{purchase_order.id}",
                is_posted=True
            )
            
            # CR Accounts Payable
            LedgerEntry.objects.create(
                account=ap_account,
                entity=entity,
                entry_date=purchase_order.po_date,
                entry_type='CREDIT',
                amount=purchase_order.total_amount,
                description=f"Accounts Payable - Purchase Order {purchase_order.po_number}",
                reference_number=f"PO-{purchase_order.id}",
                is_posted=True
            )
        
        return True
    
    except Exception as e:
        print(f"Error creating GL entries for PO {purchase_order.po_number}: {str(e)}")
        return False


def create_gr_gl_entries(goods_receipt):
    """
    Create GL entries when Goods Receipt is confirmed (RECEIVED status).
    
    Accounting Entry (Double Entry):
    DR Inventory/Stock (ASSET)       = Total Amount
    CR Accounts Payable (LIABILITY)  = Total Amount
    
    This records the inventory received and creates AP obligation.
    """
    try:
        po = goods_receipt.purchase_order
        entity = po.entity
        
        # Get GL accounts
        inventory_account = get_or_create_gl_account(entity, 'ASSET', 'Inventory')
        if not inventory_account:
            inventory_account = get_or_create_gl_account(entity, 'ASSET', 'Stock')
        
        ap_account = get_or_create_gl_account(entity, 'LIABILITY', 'Accounts Payable')
        
        if not inventory_account or not ap_account:
            return False
        
        # Check if entries already exist (idempotent check)
        existing = LedgerEntry.objects.filter(
            reference_number=f"GR-{goods_receipt.id}"
        ).exists()
        
        if existing:
            return True  # Already posted
        
        with transaction.atomic():
            # Calculate GR amount
            gr_amount = sum(line.quantity * line.unit_price for line in goods_receipt.goodsreceiptlineitem_set.all())
            
            # DR Inventory/Stock
            LedgerEntry.objects.create(
                account=inventory_account,
                entity=entity,
                entry_date=goods_receipt.receipt_date,
                entry_type='DEBIT',
                amount=gr_amount,
                description=f"Goods Receipt {goods_receipt.id} from PO {po.po_number}",
                reference_number=f"GR-{goods_receipt.id}",
                is_posted=True
            )
            
            # CR Accounts Payable
            LedgerEntry.objects.create(
                account=ap_account,
                entity=entity,
                entry_date=goods_receipt.receipt_date,
                entry_type='CREDIT',
                amount=gr_amount,
                description=f"AP - Goods Receipt for PO {po.po_number}",
                reference_number=f"GR-{goods_receipt.id}",
                is_posted=True
            )
        
        return True
    
    except Exception as e:
        print(f"Error creating GL entries for GR {goods_receipt.id}: {str(e)}")
        return False


def create_po_payment_gl_entries(purchase_order, amount_paid):
    """
    Create GL entries when Purchase Order payment is made.
    
    Accounting Entry (Double Entry):
    DR Accounts Payable (LIABILITY)  = Amount Paid
    CR Cash/Bank (ASSET)             = Amount Paid
    
    This reduces AP and decreases cash when payment is made.
    """
    try:
        entity = purchase_order.entity
        
        # Get GL accounts
        ap_account = get_or_create_gl_account(entity, 'LIABILITY', 'Accounts Payable')
        cash_account = get_or_create_gl_account(entity, 'ASSET', 'Cash')
        if not cash_account:
            cash_account = get_or_create_gl_account(entity, 'ASSET', 'Bank')
        
        if not ap_account or not cash_account:
            return False
        
        # Create payment reference
        payment_ref = f"PAY-PO-{purchase_order.id}-{purchase_order.updated_at.timestamp()}"
        
        # Check if payment already recorded
        existing = LedgerEntry.objects.filter(
            reference_number=payment_ref
        ).exists()
        
        if existing:
            return True
        
        with transaction.atomic():
            # DR Accounts Payable
            LedgerEntry.objects.create(
                account=ap_account,
                entity=entity,
                entry_date=purchase_order.updated_at.date(),
                entry_type='DEBIT',
                amount=amount_paid,
                description=f"Payment for Purchase Order {purchase_order.po_number}",
                reference_number=payment_ref,
                is_posted=True
            )
            
            # CR Cash/Bank
            LedgerEntry.objects.create(
                account=cash_account,
                entity=entity,
                entry_date=purchase_order.updated_at.date(),
                entry_type='CREDIT',
                amount=amount_paid,
                description=f"Cash Payment - PO {purchase_order.po_number}",
                reference_number=payment_ref,
                is_posted=True
            )
        
        return True
    
    except Exception as e:
        print(f"Error creating payment GL entries for PO {purchase_order.po_number}: {str(e)}")
        return False


def reverse_po_gl_entries(purchase_order):
    """
    Reverse GL entries when purchase order is CANCELLED.
    Creates opposite entries to nullify the original transaction.
    """
    try:
        entity = purchase_order.entity
        
        # Get GL accounts
        inventory_account = get_or_create_gl_account(entity, 'ASSET', 'Inventory')
        if not inventory_account:
            inventory_account = get_or_create_gl_account(entity, 'ASSET', 'Stock')
        
        ap_account = get_or_create_gl_account(entity, 'LIABILITY', 'Accounts Payable')
        
        if not inventory_account or not ap_account:
            return False
        
        # Check if reversals already exist
        existing = LedgerEntry.objects.filter(
            reference_number=f"REV-PO-{purchase_order.id}"
        ).exists()
        
        if existing:
            return True
        
        with transaction.atomic():
            # CR Inventory/Stock (reverse debit)
            LedgerEntry.objects.create(
                account=inventory_account,
                entity=entity,
                entry_date=purchase_order.updated_at.date(),
                entry_type='CREDIT',
                amount=purchase_order.total_amount,
                description=f"Reversal - PO {purchase_order.po_number} Cancelled",
                reference_number=f"REV-PO-{purchase_order.id}",
                is_posted=True
            )
            
            # DR Accounts Payable (reverse credit)
            LedgerEntry.objects.create(
                account=ap_account,
                entity=entity,
                entry_date=purchase_order.updated_at.date(),
                entry_type='DEBIT',
                amount=purchase_order.total_amount,
                description=f"Reversal - AP for Cancelled PO {purchase_order.po_number}",
                reference_number=f"REV-PO-{purchase_order.id}",
                is_posted=True
            )
        
        return True
    
    except Exception as e:
        print(f"Error reversing GL entries for PO {purchase_order.po_number}: {str(e)}")
        return False
