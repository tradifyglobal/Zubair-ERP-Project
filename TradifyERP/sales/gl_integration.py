"""
Sales Module - General Ledger Integration
Handles automatic GL entries for sales transactions (revenue recognition, AR tracking, etc.)

Accounting Flow:
1. Invoice Created (Status: DRAFT) → No GL entry
2. Invoice Issued (Status: ISSUED) → Creates AR and Revenue GL entries
3. Invoice Paid (Amount Paid) → Creates Cash GL entry, reduces AR
4. Invoice Overdue → No GL entry (status tracking only)

GL Accounts Used:
- Accounts Receivable (AR) - ASSET account
- Sales Revenue - INCOME account
- Sales Tax Payable - LIABILITY account
- Cash/Bank - ASSET account
"""

from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from accounting.models import Account, LedgerEntry, Entity
from .models import Invoice, SalesOrder


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


def create_invoice_gl_entries(invoice):
    """
    Create GL entries when invoice is ISSUED.
    
    Accounting Entry (Double Entry):
    DR Accounts Receivable (ASSET)     = Total Amount
    CR Sales Revenue (INCOME)          = Subtotal
    CR Sales Tax Payable (LIABILITY)   = Tax Amount
    
    This recognizes the revenue and creates AR obligation.
    """
    if invoice.status != 'ISSUED':
        return False
    
    try:
        entity = invoice.entity
        
        # Get GL accounts - these should be created in accounting module
        ar_account = get_or_create_gl_account(entity, 'ASSET', 'Accounts Receivable')
        revenue_account = get_or_create_gl_account(entity, 'INCOME', 'Sales Revenue')
        tax_account = get_or_create_gl_account(entity, 'LIABILITY', 'Sales Tax Payable')
        
        if not ar_account or not revenue_account:
            # Accounts not configured - return failure
            return False
        
        # Check if entries already exist (idempotent check)
        existing = LedgerEntry.objects.filter(
            reference_number=f"INV-{invoice.id}"
        ).exists()
        
        if existing:
            return True  # Already posted
        
        with transaction.atomic():
            # DR Accounts Receivable
            LedgerEntry.objects.create(
                account=ar_account,
                entity=entity,
                entry_date=invoice.invoice_date,
                entry_type='DEBIT',
                amount=invoice.total_amount,
                description=f"Invoice {invoice.invoice_number} from {invoice.customer.customer_name}",
                reference_number=f"INV-{invoice.id}",
                is_posted=True
            )
            
            # CR Sales Revenue
            LedgerEntry.objects.create(
                account=revenue_account,
                entity=entity,
                entry_date=invoice.invoice_date,
                entry_type='CREDIT',
                amount=invoice.subtotal,
                description=f"Sales Revenue - Invoice {invoice.invoice_number}",
                reference_number=f"INV-{invoice.id}",
                is_posted=True
            )
            
            # CR Sales Tax Payable (if tax exists)
            if invoice.tax_amount > 0 and tax_account:
                LedgerEntry.objects.create(
                    account=tax_account,
                    entity=entity,
                    entry_date=invoice.invoice_date,
                    entry_type='CREDIT',
                    amount=invoice.tax_amount,
                    description=f"Sales Tax - Invoice {invoice.invoice_number}",
                    reference_number=f"INV-{invoice.id}",
                    is_posted=True
                )
        
        return True
    
    except Exception as e:
        print(f"Error creating GL entries for invoice {invoice.invoice_number}: {str(e)}")
        return False


def create_payment_gl_entries(invoice, amount_paid):
    """
    Create GL entries when invoice payment is received.
    
    Accounting Entry (Double Entry):
    DR Cash/Bank (ASSET)              = Amount Paid
    CR Accounts Receivable (ASSET)    = Amount Paid
    
    This reduces AR and increases cash when payment is received.
    """
    try:
        entity = invoice.entity
        
        # Get GL accounts
        ar_account = get_or_create_gl_account(entity, 'ASSET', 'Accounts Receivable')
        cash_account = get_or_create_gl_account(entity, 'ASSET', 'Cash')
        
        if not ar_account or not cash_account:
            return False
        
        # Create payment reference
        payment_ref = f"PAY-INV-{invoice.id}-{invoice.updated_at.timestamp()}"
        
        # Check if payment already recorded
        existing = LedgerEntry.objects.filter(
            reference_number=payment_ref
        ).exists()
        
        if existing:
            return True
        
        with transaction.atomic():
            # DR Cash/Bank
            LedgerEntry.objects.create(
                account=cash_account,
                entity=entity,
                entry_date=invoice.updated_at.date(),
                entry_type='DEBIT',
                amount=amount_paid,
                description=f"Payment received for Invoice {invoice.invoice_number}",
                reference_number=payment_ref,
                is_posted=True
            )
            
            # CR Accounts Receivable
            LedgerEntry.objects.create(
                account=ar_account,
                entity=entity,
                entry_date=invoice.updated_at.date(),
                entry_type='CREDIT',
                amount=amount_paid,
                description=f"AR Reduction - Payment for Invoice {invoice.invoice_number}",
                reference_number=payment_ref,
                is_posted=True
            )
        
        return True
    
    except Exception as e:
        print(f"Error creating payment GL entries for invoice {invoice.invoice_number}: {str(e)}")
        return False


def reverse_invoice_gl_entries(invoice):
    """
    Reverse GL entries when invoice is CANCELLED.
    Creates opposite entries to nullify the original revenue recognition.
    """
    try:
        entity = invoice.entity
        
        # Get GL accounts
        ar_account = get_or_create_gl_account(entity, 'ASSET', 'Accounts Receivable')
        revenue_account = get_or_create_gl_account(entity, 'INCOME', 'Sales Revenue')
        tax_account = get_or_create_gl_account(entity, 'LIABILITY', 'Sales Tax Payable')
        
        if not ar_account or not revenue_account:
            return False
        
        # Create reversal reference
        reversal_ref = f"REV-INV-{invoice.id}"
        
        # Check if reversal already exists
        existing = LedgerEntry.objects.filter(
            reference_number=reversal_ref
        ).exists()
        
        if existing:
            return True
        
        with transaction.atomic():
            # CR Accounts Receivable (reverse of debit)
            LedgerEntry.objects.create(
                account=ar_account,
                entity=entity,
                entry_date=invoice.updated_at.date(),
                entry_type='CREDIT',
                amount=invoice.total_amount,
                description=f"Reversal - Invoice {invoice.invoice_number} cancelled",
                reference_number=reversal_ref,
                is_posted=True
            )
            
            # DR Sales Revenue (reverse of credit)
            LedgerEntry.objects.create(
                account=revenue_account,
                entity=entity,
                entry_date=invoice.updated_at.date(),
                entry_type='DEBIT',
                amount=invoice.subtotal,
                description=f"Revenue Reversal - Invoice {invoice.invoice_number}",
                reference_number=reversal_ref,
                is_posted=True
            )
            
            # DR Sales Tax Payable (reverse of credit)
            if invoice.tax_amount > 0 and tax_account:
                LedgerEntry.objects.create(
                    account=tax_account,
                    entity=entity,
                    entry_date=invoice.updated_at.date(),
                    entry_type='DEBIT',
                    amount=invoice.tax_amount,
                    description=f"Tax Reversal - Invoice {invoice.invoice_number}",
                    reference_number=reversal_ref,
                    is_posted=True
                )
        
        return True
    
    except Exception as e:
        print(f"Error reversing GL entries for invoice {invoice.invoice_number}: {str(e)}")
        return False


def get_sales_metrics_from_gl(entity, period_start, period_end):
    """
    Calculate sales metrics from GL entries for P&L reporting.
    Returns total revenue, tax, and net sales for the period.
    """
    try:
        revenue_account = get_or_create_gl_account(entity, 'INCOME', 'Sales Revenue')
        tax_account = get_or_create_gl_account(entity, 'LIABILITY', 'Sales Tax Payable')
        
        if not revenue_account:
            return {
                'total_revenue': Decimal('0.00'),
                'total_tax': Decimal('0.00'),
                'net_sales': Decimal('0.00'),
            }
        
        # Get all revenue GL entries for period
        revenue_entries = LedgerEntry.objects.filter(
            account=revenue_account,
            entity=entity,
            entry_date__gte=period_start,
            entry_date__lte=period_end,
            is_posted=True
        )
        
        total_revenue = Decimal('0.00')
        for entry in revenue_entries:
            # Revenue accounts credit increases income
            if entry.entry_type == 'CREDIT':
                total_revenue += entry.amount
            else:  # Debit reverses it
                total_revenue -= entry.amount
        
        # Get tax entries for period
        total_tax = Decimal('0.00')
        if tax_account:
            tax_entries = LedgerEntry.objects.filter(
                account=tax_account,
                entity=entity,
                entry_date__gte=period_start,
                entry_date__lte=period_end,
                is_posted=True
            )
            for entry in tax_entries:
                # Tax payable account credit = liability increase
                if entry.entry_type == 'CREDIT':
                    total_tax += entry.amount
                else:  # Debit reduces liability
                    total_tax -= entry.amount
        
        return {
            'total_revenue': max(total_revenue, Decimal('0.00')),
            'total_tax': max(total_tax, Decimal('0.00')),
            'net_sales': max(total_revenue - total_tax, Decimal('0.00')),
        }
    
    except Exception as e:
        print(f"Error calculating sales metrics from GL: {str(e)}")
        return {
            'total_revenue': Decimal('0.00'),
            'total_tax': Decimal('0.00'),
            'net_sales': Decimal('0.00'),
        }


def get_ar_balance(entity):
    """
    Calculate current Accounts Receivable balance from GL.
    """
    try:
        ar_account = get_or_create_gl_account(entity, 'ASSET', 'Accounts Receivable')
        
        if not ar_account:
            return Decimal('0.00')
        
        # AR is an asset account, so Debit balance is normal
        debits = LedgerEntry.objects.filter(
            account=ar_account,
            entity=entity,
            entry_type='DEBIT',
            is_posted=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        credits = LedgerEntry.objects.filter(
            account=ar_account,
            entity=entity,
            entry_type='CREDIT',
            is_posted=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        ar_balance = debits - credits
        return max(ar_balance, Decimal('0.00'))
    
    except Exception as e:
        print(f"Error calculating AR balance: {str(e)}")
        return Decimal('0.00')
