"""
Sales-Accounts Integration Module

This module provides utilities for integrating sales transactions with the accounting module.
Handles GL posting, AR management, payment reconciliation, and tax calculations.

Key Functions:
- post_invoice_to_gl: Post invoice to General Ledger (revenue + tax)
- record_accounts_receivable: Create AR record when invoice is issued
- process_customer_payment: Record payment and update GL/AR
- post_sales_adjustment: Post discounts, returns, write-offs to GL
- reconcile_sales_to_accounts: Verify sales-accounts reconciliation
- generate_sales_financial_report: Create consolidated financial metrics
"""

from django.db import transaction, models
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
from accounting.models import LedgerEntry, Account, TaxRate, TaxTransaction
from .models import (
    Invoice, SalesOrder, AccountsReceivable, GeneralLedgerPosting,
    SalesPayment, SalesAdjustment, SalesFinancialReport, Customer
)


class GLPostingManager:
    """Manages General Ledger posting operations for sales transactions."""
    
    @staticmethod
    def post_invoice_revenue_to_gl(invoice):
        """
        Post invoice revenue to GL when invoice is issued.
        
        Creates two GL entries:
        1. DEBIT: Accounts Receivable (Asset)
        2. CREDIT: Revenue (Income)
        
        Returns:
            GeneralLedgerPosting: The created GL posting record
        """
        if invoice.is_posted_to_gl:
            raise ValueError(f"Invoice {invoice.invoice_number} already posted to GL")
        
        if invoice.status != 'ISSUED':
            raise ValueError(f"Invoice must be ISSUED status to post to GL, current: {invoice.status}")
        
        entity = invoice.entity
        
        try:
            # Find revenue account (typically 4000-series)
            revenue_account = Account.objects.get(
                entity=entity,
                account_type='INCOME',
                is_active=True
            )
        except Account.DoesNotExist:
            raise ValueError(f"Revenue account not found for entity {entity.code}")
        
        try:
            # Find AR account (typically 1200-series)
            ar_account = Account.objects.get(
                entity=entity,
                name__icontains='Accounts Receivable',
                account_type='ASSET',
                is_active=True
            )
        except Account.DoesNotExist:
            raise ValueError(f"Accounts Receivable account not found for entity {entity.code}")
        
        with transaction.atomic():
            # Create GL Posting record
            gl_posting = GeneralLedgerPosting.objects.create(
                entity=entity,
                invoice=invoice,
                posting_type='REVENUE',
                posting_date=invoice.invoice_date,
                description=f"Revenue from Invoice {invoice.invoice_number} - Customer {invoice.customer.customer_name}",
                debit_account=ar_account,
                credit_account=revenue_account,
                debit_amount=invoice.total_amount,
                credit_amount=invoice.total_amount,
                status='PENDING',
                created_by=invoice.issued_by
            )
            
            # Create GL Entry
            ledger_entry = LedgerEntry.objects.create(
                account=revenue_account,
                entity=entity,
                entry_date=invoice.invoice_date,
                entry_type='CREDIT',
                amount=invoice.subtotal,  # Subtotal without tax
                description=f"Revenue - Invoice {invoice.invoice_number}",
                reference_number=invoice.invoice_number,
                is_posted=True,
                workflow_status='AUTHORIZED'
            )
            
            # Link GL posting to GL entry
            gl_posting.gl_ledger_entry = ledger_entry
            gl_posting.status = 'POSTED'
            gl_posting.posted_at = timezone.now()
            gl_posting.save()
            
            # Update invoice
            invoice.gl_posting_id = ledger_entry
            invoice.is_posted_to_gl = True
            invoice.gl_posted_at = timezone.now()
            invoice.save()
            
            return gl_posting
    
    @staticmethod
    def post_invoice_tax_to_gl(invoice):
        """
        Post invoice tax liability to GL.
        
        Creates two GL entries:
        1. DEBIT: Accounts Receivable (Asset) - already done in revenue posting
        2. CREDIT: Tax Payable (Liability)
        
        Returns:
            GeneralLedgerPosting: The created tax GL posting
        """
        if invoice.tax_amount <= 0:
            return None  # No tax to post
        
        entity = invoice.entity
        
        try:
            # Find Tax Payable account (typically 2100-series)
            tax_account = Account.objects.get(
                entity=entity,
                name__icontains='Tax Payable',
                account_type='LIABILITY',
                is_active=True
            )
        except Account.DoesNotExist:
            raise ValueError(f"Tax Payable account not found for entity {entity.code}")
        
        try:
            ar_account = Account.objects.get(
                entity=entity,
                name__icontains='Accounts Receivable',
                account_type='ASSET',
                is_active=True
            )
        except Account.DoesNotExist:
            raise ValueError(f"Accounts Receivable account not found for entity {entity.code}")
        
        with transaction.atomic():
            # Create GL Posting record
            gl_posting = GeneralLedgerPosting.objects.create(
                entity=entity,
                invoice=invoice,
                posting_type='TAX',
                posting_date=invoice.invoice_date,
                description=f"Sales Tax - Invoice {invoice.invoice_number}",
                debit_account=ar_account,
                credit_account=tax_account,
                debit_amount=invoice.tax_amount,
                credit_amount=invoice.tax_amount,
                status='PENDING',
                created_by=invoice.issued_by
            )
            
            # Create GL Entry
            ledger_entry = LedgerEntry.objects.create(
                account=tax_account,
                entity=entity,
                entry_date=invoice.invoice_date,
                entry_type='CREDIT',
                amount=invoice.tax_amount,
                description=f"Tax Liability - Invoice {invoice.invoice_number}",
                reference_number=invoice.invoice_number,
                is_posted=True,
                workflow_status='AUTHORIZED'
            )
            
            # Link GL posting
            gl_posting.gl_ledger_entry = ledger_entry
            gl_posting.status = 'POSTED'
            gl_posting.posted_at = timezone.now()
            gl_posting.save()
            
            # Update invoice
            invoice.tax_gl_posting_id = ledger_entry
            invoice.save()
            
            # Record tax transaction
            tax_rate = self._get_applicable_tax_rate(entity, invoice.invoice_date)
            if tax_rate:
                TaxTransaction.objects.create(
                    entity=entity,
                    tax_rate=tax_rate,
                    transaction_date=invoice.invoice_date,
                    gross_amount=invoice.subtotal,
                    tax_amount=invoice.tax_amount,
                    net_amount=invoice.total_amount,
                    reference_number=invoice.invoice_number
                )
            
            return gl_posting
    
    @staticmethod
    def _get_applicable_tax_rate(entity, transaction_date):
        """Get the applicable tax rate for a transaction date."""
        tax_rate = TaxRate.objects.filter(
            entity=entity,
            is_active=True,
            effective_from__lte=transaction_date
        ).exclude(
            effective_to__lt=transaction_date
        ).first()
        return tax_rate


class AccountsReceivableManager:
    """Manages Accounts Receivable operations."""
    
    @staticmethod
    def create_ar_from_invoice(invoice):
        """
        Create AR record when invoice is issued.
        
        Args:
            invoice: Invoice object
            
        Returns:
            AccountsReceivable: The created AR record
        """
        if invoice.status != 'ISSUED':
            raise ValueError(f"Invoice must be ISSUED to create AR record")
        
        ar_record, created = AccountsReceivable.objects.get_or_create(
            invoice=invoice,
            defaults={
                'entity': invoice.entity,
                'customer': invoice.customer,
                'invoice_amount': invoice.total_amount,
                'amount_outstanding': invoice.total_amount,
                'invoice_date': invoice.invoice_date,
                'due_date': invoice.due_date,
                'status': 'OUTSTANDING'
            }
        )
        
        if created:
            # Link to GL posting if available
            if invoice.gl_posting_id:
                ar_record.ar_gl_posting_id = invoice.gl_posting_id
                ar_record.save()
        
        return ar_record
    
    @staticmethod
    def get_ar_aging_summary(entity, as_of_date=None):
        """
        Get AR aging summary for entity.
        
        Args:
            entity: Entity object
            as_of_date: Date for aging calculation (default: today)
            
        Returns:
            dict: Aging summary with counts and amounts by bucket
        """
        if not as_of_date:
            as_of_date = timezone.now().date()
        
        ar_records = AccountsReceivable.objects.filter(
            entity=entity,
            status__in=['OUTSTANDING', 'PARTIAL', 'OVERDUE']
        )
        
        summary = {
            'current': {'count': 0, 'amount': Decimal('0.00')},
            '30_60': {'count': 0, 'amount': Decimal('0.00')},
            '60_90': {'count': 0, 'amount': Decimal('0.00')},
            'over_90': {'count': 0, 'amount': Decimal('0.00')},
        }
        
        for ar in ar_records:
            days_outstanding = (as_of_date - ar.due_date).days
            
            if days_outstanding <= 30:
                bucket = 'current'
            elif days_outstanding <= 60:
                bucket = '30_60'
            elif days_outstanding <= 90:
                bucket = '60_90'
            else:
                bucket = 'over_90'
            
            summary[bucket]['count'] += 1
            summary[bucket]['amount'] += ar.amount_outstanding
        
        return summary
    
    @staticmethod
    def get_collection_forecast(entity, days_ahead=30):
        """
        Get expected collection forecast for next N days.
        
        Args:
            entity: Entity object
            days_ahead: Number of days to forecast (default: 30)
            
        Returns:
            dict: Daily collection forecast
        """
        from datetime import timedelta
        
        today = timezone.now().date()
        forecast = {}
        
        for i in range(days_ahead):
            date = today + timedelta(days=i)
            ar_due = AccountsReceivable.objects.filter(
                entity=entity,
                due_date=date,
                status__in=['OUTSTANDING', 'OVERDUE']
            ).aggregate(total=models.Sum('amount_outstanding'))
            
            forecast[date.isoformat()] = ar_due['total'] or Decimal('0.00')
        
        return forecast


class PaymentProcessor:
    """Handles customer payment processing and reconciliation."""
    
    @staticmethod
    def process_payment(invoice, amount, payment_date, payment_method, reference_number, user):
        """
        Process customer payment for invoice.
        
        Creates:
        1. SalesPayment record
        2. GL entries for cash receipt and AR reduction
        3. Updates AR record
        4. Updates invoice status
        
        Args:
            invoice: Invoice object
            amount: Payment amount
            payment_date: Date of payment
            payment_method: Payment method (CASH, CHECK, BANK_TRANSFER, etc.)
            reference_number: Reference ID (check #, transaction ID, etc.)
            user: User recording the payment
            
        Returns:
            SalesPayment: The created payment record
        """
        if amount <= 0:
            raise ValueError("Payment amount must be greater than 0")
        
        if invoice.status == 'CANCELLED':
            raise ValueError("Cannot process payment on cancelled invoice")
        
        entity = invoice.entity
        
        with transaction.atomic():
            # Create payment record
            payment = SalesPayment.objects.create(
                entity=entity,
                invoice=invoice,
                customer=invoice.customer,
                payment_date=payment_date,
                amount=amount,
                payment_method=payment_method,
                reference_number=reference_number,
                status='PENDING',
                recorded_by=user
            )
            
            # Post cash receipt to GL
            PaymentProcessor._post_cash_receipt_to_gl(invoice, payment, amount, user)
            
            # Update AR record
            ar_record = AccountsReceivable.objects.get(invoice=invoice)
            ar_record.amount_received += amount
            ar_record.amount_outstanding -= amount
            ar_record.last_payment_date = payment_date
            
            # Update AR status
            if ar_record.amount_outstanding <= 0:
                ar_record.status = 'PAID'
            elif ar_record.amount_received > 0:
                ar_record.status = 'PARTIAL'
            else:
                ar_record.status = 'OUTSTANDING'
            
            ar_record.save()
            
            # Update invoice payment tracking
            invoice.amount_paid += amount
            
            if invoice.amount_paid >= invoice.total_amount:
                invoice.status = 'PAID'
            elif invoice.amount_paid > 0:
                invoice.status = 'PARTIAL'
            
            invoice.save()
            
            # Mark payment as reconciled
            payment.status = 'RECONCILED'
            payment.save()
        
        return payment
    
    @staticmethod
    def _post_cash_receipt_to_gl(invoice, payment, amount, user):
        """Post cash receipt GL entries."""
        entity = invoice.entity
        
        try:
            # Find cash account
            cash_account = Account.objects.get(
                entity=entity,
                name__icontains='Cash',
                account_type='ASSET',
                is_active=True
            )
        except Account.DoesNotExist:
            raise ValueError(f"Cash account not found for entity {entity.code}")
        
        try:
            # Find AR account
            ar_account = Account.objects.get(
                entity=entity,
                name__icontains='Accounts Receivable',
                account_type='ASSET',
                is_active=True
            )
        except Account.DoesNotExist:
            raise ValueError(f"Accounts Receivable account not found for entity {entity.code}")
        
        # Create GL entries
        # DEBIT: Cash, CREDIT: AR
        ledger_entry = LedgerEntry.objects.create(
            account=cash_account,
            entity=entity,
            entry_date=payment.payment_date,
            entry_type='DEBIT',
            amount=amount,
            description=f"Cash Receipt - Invoice {invoice.invoice_number}",
            reference_number=f"{payment.reference_number}",
            is_posted=True,
            workflow_status='AUTHORIZED'
        )
        
        payment.cash_gl_posting_id = ledger_entry
        payment.save()


class AdjustmentProcessor:
    """Handles sales adjustments (discounts, returns, write-offs)."""
    
    @staticmethod
    def post_adjustment_to_gl(adjustment):
        """
        Post sales adjustment to GL.
        
        Args:
            adjustment: SalesAdjustment object
            
        Returns:
            LedgerEntry: The created GL entry
        """
        if adjustment.status != 'APPROVED':
            raise ValueError("Adjustment must be APPROVED before posting to GL")
        
        entity = adjustment.entity
        invoice = adjustment.invoice
        
        # Determine accounts based on adjustment type
        if adjustment.adjustment_type == 'DISCOUNT':
            # DEBIT: Discount Expense, CREDIT: AR or Revenue
            try:
                debit_account = Account.objects.get(
                    entity=entity,
                    name__icontains='Discount',
                    account_type='EXPENSE',
                    is_active=True
                )
            except Account.DoesNotExist:
                raise ValueError(f"Discount account not found for entity {entity.code}")
            
            try:
                credit_account = Account.objects.get(
                    entity=entity,
                    name__icontains='Accounts Receivable',
                    account_type='ASSET',
                    is_active=True
                )
            except Account.DoesNotExist:
                raise ValueError(f"AR account not found for entity {entity.code}")
        
        elif adjustment.adjustment_type in ['RETURN', 'CREDIT_NOTE']:
            # DEBIT: Sales Return/Refund, CREDIT: AR or Revenue
            try:
                debit_account = Account.objects.get(
                    entity=entity,
                    name__icontains='Sales Return',
                    account_type='EXPENSE',
                    is_active=True
                )
            except Account.DoesNotExist:
                raise ValueError(f"Sales Return account not found for entity {entity.code}")
            
            try:
                credit_account = Account.objects.get(
                    entity=entity,
                    name__icontains='Accounts Receivable',
                    account_type='ASSET',
                    is_active=True
                )
            except Account.DoesNotExist:
                raise ValueError(f"AR account not found for entity {entity.code}")
        
        elif adjustment.adjustment_type == 'WRITE_OFF':
            # DEBIT: Bad Debt Expense, CREDIT: AR
            try:
                debit_account = Account.objects.get(
                    entity=entity,
                    name__icontains='Bad Debt',
                    account_type='EXPENSE',
                    is_active=True
                )
            except Account.DoesNotExist:
                raise ValueError(f"Bad Debt account not found for entity {entity.code}")
            
            try:
                credit_account = Account.objects.get(
                    entity=entity,
                    name__icontains='Accounts Receivable',
                    account_type='ASSET',
                    is_active=True
                )
            except Account.DoesNotExist:
                raise ValueError(f"AR account not found for entity {entity.code}")
        
        else:
            raise ValueError(f"Unknown adjustment type: {adjustment.adjustment_type}")
        
        with transaction.atomic():
            # Create GL entry
            ledger_entry = LedgerEntry.objects.create(
                account=debit_account,
                entity=entity,
                entry_date=adjustment.adjustment_date,
                entry_type='DEBIT',
                amount=adjustment.amount,
                description=f"{adjustment.adjustment_type} - Invoice {invoice.invoice_number}: {adjustment.reason}",
                reference_number=invoice.invoice_number,
                is_posted=True,
                workflow_status='AUTHORIZED'
            )
            
            adjustment.adjustment_gl_posting_id = ledger_entry
            adjustment.status = 'POSTED'
            adjustment.save()
            
            # Update invoice amounts
            if adjustment.adjustment_type in ['DISCOUNT', 'RETURN', 'CREDIT_NOTE']:
                invoice.total_amount -= adjustment.amount
                invoice.amount_outstanding = max(0, invoice.total_amount - invoice.amount_paid)
            
            invoice.save()
        
        return ledger_entry


class FinancialReportGenerator:
    """Generates consolidated sales financial reports."""
    
    @staticmethod
    def generate_report(entity, report_type, period_start, period_end, user):
        """
        Generate sales financial report for period.
        
        Args:
            entity: Entity object
            report_type: Report type (DAILY, WEEKLY, MONTHLY, QUARTERLY, ANNUAL)
            period_start: Period start date
            period_end: Period end date
            user: User generating report
            
        Returns:
            SalesFinancialReport: The created report
        """
        from django.db.models import Sum, Count
        
        with transaction.atomic():
            # Get all invoices in period
            invoices = Invoice.objects.filter(
                entity=entity,
                invoice_date__gte=period_start,
                invoice_date__lte=period_end,
                status__in=['ISSUED', 'PAID', 'PARTIAL', 'OVERDUE']
            )
            
            # Calculate metrics
            revenue_stats = invoices.aggregate(
                gross_revenue=Sum('subtotal'),
                total_tax=Sum('tax_amount'),
                total_paid=Sum('amount_paid')
            )
            
            adjustments = SalesAdjustment.objects.filter(
                entity=entity,
                adjustment_date__gte=period_start,
                adjustment_date__lte=period_end,
                status='POSTED'
            )
            
            adjustment_stats = adjustments.aggregate(
                total_discounts=Sum(
                    'amount',
                    filter=models.Q(adjustment_type='DISCOUNT')
                ),
                total_returns=Sum(
                    'amount',
                    filter=models.Q(adjustment_type__in=['RETURN', 'CREDIT_NOTE'])
                ),
                total_writeoffs=Sum(
                    'amount',
                    filter=models.Q(adjustment_type='WRITE_OFF')
                )
            )
            
            # Get AR metrics
            ar_stats = AccountsReceivable.objects.filter(
                entity=entity,
                invoice_date__gte=period_start,
                invoice_date__lte=period_end
            ).aggregate(
                total_invoiced=Sum('invoice_amount'),
                total_received=Sum('amount_received'),
                total_outstanding=Sum('amount_outstanding')
            )
            
            overdue_stats = AccountsReceivable.objects.filter(
                entity=entity,
                status__in=['OVERDUE', 'OUTSTANDING'],
                due_date__lt=period_end
            ).aggregate(
                overdue_amount=Sum('amount_outstanding')
            )
            
            # Get customer metrics
            customer_stats = invoices.aggregate(
                active_customers=Count('customer', distinct=True)
            )
            
            new_customers = Customer.objects.filter(
                entity=entity,
                created_at__gte=period_start,
                created_at__lte=period_end
            ).count()
            
            # Calculate derived metrics
            gross_revenue = revenue_stats['gross_revenue'] or Decimal('0.00')
            total_discounts = adjustment_stats['total_discounts'] or Decimal('0.00')
            total_returns = adjustment_stats['total_returns'] or Decimal('0.00')
            net_revenue = gross_revenue - total_discounts - total_returns
            
            gross_profit = net_revenue  # Simplified; would need COGS from manufacturing
            gross_profit_margin = (gross_profit / net_revenue * 100) if net_revenue > 0 else Decimal('0.00')
            
            # Create report
            report = SalesFinancialReport.objects.create(
                entity=entity,
                report_type=report_type,
                period_start=period_start,
                period_end=period_end,
                gross_revenue=gross_revenue,
                total_discounts=total_discounts,
                total_returns=total_returns,
                net_revenue=net_revenue,
                total_tax_collected=revenue_stats['total_tax'] or Decimal('0.00'),
                total_invoiced=ar_stats['total_invoiced'] or Decimal('0.00'),
                total_received=ar_stats['total_received'] or Decimal('0.00'),
                total_outstanding=ar_stats['total_outstanding'] or Decimal('0.00'),
                overdue_amount=overdue_stats['overdue_amount'] or Decimal('0.00'),
                gross_profit=gross_profit,
                gross_profit_margin=gross_profit_margin,
                total_active_customers=customer_stats['active_customers'] or 0,
                new_customers=new_customers,
                generated_by=user
            )
            
            return report
