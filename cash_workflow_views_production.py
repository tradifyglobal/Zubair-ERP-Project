"""
Workflow views for Cash Management Module
Handles approval, authorization, and rejection of cash transactions
"""
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import View, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.contrib import messages
from decimal import Decimal
from .models import (
    CashReceiptLine, CashPaymentLine, BankReceiptLine, BankPaymentLine, Account, LedgerEntry, AuditLog
)
from .mixins import SessionEntityMixin


class CashReceiptApprovalView(LoginRequiredMixin, SessionEntityMixin, View):
    """Approve cash receipt (DRAFT -> PENDING_APPROVAL -> APPROVED)."""
    
    def post(self, request, pk):
        receipt = get_object_or_404(CashReceiptLine, pk=pk, entity=request.entity)
        
        if receipt.workflow_status not in ['DRAFT', 'PENDING_APPROVAL']:
            messages.error(request, 'Can only approve Draft or Pending Approval receipts')
            return redirect('accounting:cash_receipt_list')
        
        with transaction.atomic():
            # Auto-assign stakeholder if missing before approving
            if not receipt.stakeholder_id and receipt.account:
                stakeholder = self._find_stakeholder_for_account(receipt.account)
                if stakeholder:
                    receipt.stakeholder = stakeholder
            
            receipt.workflow_status = 'APPROVED'
            receipt.status = 'DRAFT'
            receipt.save()
            
            AuditLog.objects.create(
                user=request.user,
                action='approve_cash_receipt',
                model_name='CashReceiptLine',
                object_id=receipt.id,
                entity=request.entity,
                description=f"Approved cash receipt: {receipt.description}"
            )
            
            messages.success(request, 'Cash receipt approved! Ready for authorization.')
        
        return redirect('accounting:cash_receipt_list')
    
    def _find_stakeholder_for_account(self, account):
        """Find stakeholder that matches the account name pattern."""
        from accounting.models import Stakeholder
        
        if not account or not account.name:
            return None
            
        account_name = account.name.strip()
        
        # Extract stakeholder name from account name patterns like:
        # "Dr. Irfan Mohammed - Capital" -> "Dr. Irfan Mohammed"
        # "Nasir Ali Ali Mohammed - Capital" -> "Nasir Ali Ali Mohammed"
        if ' - Capital' in account_name:
            stakeholder_name = account_name.replace(' - Capital', '').strip()
        else:
            return None
        
        # Try to find matching stakeholder by name
        stakeholders = Stakeholder.objects.filter(entity=account.entity)
        
        # 1. First, try exact match by full name
        for stakeholder in stakeholders:
            if stakeholder.full_name == stakeholder_name:
                return stakeholder
        
        # 2. Try fuzzy matching for name variations
        extracted_words = set(stakeholder_name.lower().split())
        best_match = None
        best_score = 0
        
        for stakeholder in stakeholders:
            stakeholder_words = set(stakeholder.full_name.lower().split())
            
            # Calculate word overlap
            overlap = len(extracted_words.intersection(stakeholder_words))
            total_words = max(len(extracted_words), len(stakeholder_words))
            
            if total_words > 0:
                score = overlap / total_words
                
                # Require at least 60% word match and minimum 2 matching words
                if score >= 0.6 and overlap >= 2 and score > best_score:
                    best_match = stakeholder
                    best_score = score
        
        if best_match:
            return best_match
        
        # 3. Fallback: try partial matching by first/last name
        name_parts = stakeholder_name.split()
        if len(name_parts) >= 2:
            first_part = name_parts[0]
            last_part = name_parts[-1]
            
            for stakeholder in stakeholders:
                if (stakeholder.first_name and stakeholder.last_name and 
                    first_part.lower() in stakeholder.first_name.lower() and 
                    last_part.lower() in stakeholder.last_name.lower()):
                    return stakeholder
        
        return None


class CashReceiptAuthorizationView(LoginRequiredMixin, SessionEntityMixin, View):
    """Authorize cash receipt (APPROVED -> AUTHORIZED) and create GL entries."""
    
    def post(self, request, pk):
        receipt = get_object_or_404(CashReceiptLine, pk=pk, entity=request.entity)
        
        if receipt.workflow_status != 'APPROVED':
            messages.error(request, 'Receipt must be approved before authorization')
            return redirect('accounting:cash_receipt_list')
        
        with transaction.atomic():
            try:
                # Get cash account first
                if receipt.credit_account:
                    cash_account = receipt.credit_account
                else:
                    cash_account = Account.objects.get(
                        entity=request.entity,
                        account_number='100001'  # Cash account
                    )
                
                # Create DEBIT entry to cash account (asset increases)
                LedgerEntry.objects.create(
                    entity=request.entity,
                    account=cash_account,
                    entry_type='DEBIT',
                    amount=receipt.debit_amount,
                    description=f"Cash Receipt: {receipt.description}",
                    entry_date=receipt.date,
                    reference_number=f'CASH-RECEIPT-{receipt.id}',
                    is_posted=True,
                    workflow_status='AUTHORIZED'
                )
                
                # Create CREDIT entry to the selected account (e.g., 3000-16 Shareholder Capital - equity increases)
                LedgerEntry.objects.create(
                    entity=request.entity,
                    account=receipt.account,
                    entry_type='CREDIT',
                    amount=receipt.credit_amount,
                    description=f"Cash Receipt: {receipt.description}",
                    entry_date=receipt.date,
                    reference_number=f'CASH-RECEIPT-{receipt.id}',
                    is_posted=True,
                    workflow_status='AUTHORIZED'
                )
                
                # Update receipt status
                receipt.workflow_status = 'AUTHORIZED'
                receipt.status = 'POSTED'
                receipt.save()
                
                # Capital contribution will be auto-created by signal when status changes to AUTHORIZED
                
                AuditLog.objects.create(
                    user=request.user,
                    action='authorize_cash_receipt',
                    model_name='CashReceiptLine',
                    object_id=receipt.id,
                    entity=request.entity,
                    description=f"Authorized and posted cash receipt: {receipt.description}"
                )
                
                messages.success(request, 'Cash receipt authorized and posted to GL!')
            except Account.DoesNotExist:
                messages.error(request, 'Cash account (100001) not found in system!')
            except Exception as e:
                messages.error(request, f'Error authorizing receipt: {str(e)}')
        
        return redirect('accounting:cash_receipt_list')


class CashReceiptRejectView(LoginRequiredMixin, SessionEntityMixin, View):
    """Reject cash receipt."""
    
    def post(self, request, pk):
        receipt = get_object_or_404(CashReceiptLine, pk=pk, entity=request.entity)
        
        if receipt.workflow_status in ['AUTHORIZED', 'POSTED']:
            messages.error(request, 'Cannot reject authorized or posted receipts')
            return redirect('accounting:cash_receipt_list')
        
        with transaction.atomic():
            receipt.workflow_status = 'REJECTED'
            receipt.status = 'DRAFT'
            receipt.save()
            
            AuditLog.objects.create(
                user=request.user,
                action='reject_cash_receipt',
                model_name='CashReceiptLine',
                object_id=receipt.id,
                entity=request.entity,
                description=f"Rejected cash receipt: {receipt.description}"
            )
            
            messages.success(request, 'Cash receipt rejected.')
        
        return redirect('accounting:cash_receipt_list')


class CashPaymentApprovalView(LoginRequiredMixin, SessionEntityMixin, View):
    """Approve cash payment."""
    
    def post(self, request, pk):
        payment = get_object_or_404(CashPaymentLine, pk=pk, entity=request.entity)
        
        if payment.workflow_status not in ['DRAFT', 'PENDING_APPROVAL']:
            messages.error(request, 'Can only approve Draft or Pending Approval payments')
            return redirect('accounting:cash_payment_list')
        
        with transaction.atomic():
            payment.workflow_status = 'APPROVED'
            payment.status = 'DRAFT'
            payment.save()
            
            AuditLog.objects.create(
                user=request.user,
                action='approve_cash_payment',
                model_name='CashPaymentLine',
                object_id=payment.id,
                entity=request.entity,
                description=f"Approved cash payment: {payment.description}"
            )
            
            messages.success(request, 'Cash payment approved! Ready for authorization.')
        
        return redirect('accounting:cash_payment_list')


class CashPaymentAuthorizationView(LoginRequiredMixin, SessionEntityMixin, View):
    """Authorize cash payment and create GL entries."""
    
    def post(self, request, pk):
        payment = get_object_or_404(CashPaymentLine, pk=pk, entity=request.entity)
        
        if payment.workflow_status != 'APPROVED':
            messages.error(request, 'Payment must be approved before authorization')
            return redirect('accounting:cash_payment_list')
        
        with transaction.atomic():
            try:
                # Use provided credit_account or fallback to cash account 100001
                if payment.credit_account:
                    cash_account = payment.credit_account
                else:
                    cash_account = Account.objects.get(
                        entity=request.entity,
                        account_number='100001'  # Cash account
                    )
                
                # Create DEBIT entry to expense/capital account (expense/withdrawal increases)
                LedgerEntry.objects.create(
                    entity=request.entity,
                    account=payment.account,
                    entry_type='DEBIT',
                    amount=payment.debit_amount,
                    description=f"Cash Payment: {payment.description}",
                    entry_date=payment.date,
                    reference_number=f'CASH-PAYMENT-{payment.id}',
                    is_posted=True,
                    workflow_status='AUTHORIZED'
                )
                
                # Create CREDIT entry to cash account (asset decreases)
                LedgerEntry.objects.create(
                    entity=request.entity,
                    account=cash_account,
                    entry_type='CREDIT',
                    amount=payment.credit_amount,
                    description=f"Cash Payment: {payment.description}",
                    entry_date=payment.date,
                    reference_number=f'CASH-PAYMENT-{payment.id}',
                    is_posted=True,
                    workflow_status='AUTHORIZED'
                )
                
                # Update payment status
                payment.workflow_status = 'AUTHORIZED'
                payment.status = 'POSTED'
                payment.save()
                
                AuditLog.objects.create(
                    user=request.user,
                    action='authorize_cash_payment',
                    model_name='CashPaymentLine',
                    object_id=payment.id,
                    entity=request.entity,
                    description=f"Authorized and posted cash payment: {payment.description}"
                )
                
                messages.success(request, 'Cash payment authorized and posted to GL!')
            except Account.DoesNotExist:
                messages.error(request, 'Cash account (100001) not found in system!')
            except Exception as e:
                messages.error(request, f'Error authorizing payment: {str(e)}')
        
        return redirect('accounting:cash_payment_list')


class CashPaymentRejectView(LoginRequiredMixin, SessionEntityMixin, View):
    """Reject cash payment."""
    
    def post(self, request, pk):
        payment = get_object_or_404(CashPaymentLine, pk=pk, entity=request.entity)
        
        if payment.workflow_status in ['AUTHORIZED', 'POSTED']:
            messages.error(request, 'Cannot reject authorized or posted payments')
            return redirect('accounting:cash_payment_list')
        
        with transaction.atomic():
            payment.workflow_status = 'REJECTED'
            payment.status = 'DRAFT'
            payment.save()
            
            AuditLog.objects.create(
                user=request.user,
                action='reject_cash_payment',
                model_name='CashPaymentLine',
                object_id=payment.id,
                entity=request.entity,
                description=f"Rejected cash payment: {payment.description}"
            )
            
            messages.success(request, 'Cash payment rejected.')
        
        return redirect('accounting:cash_payment_list')


# ============ BANK RECEIPT WORKFLOW VIEWS ============

class BankReceiptApprovalView(LoginRequiredMixin, SessionEntityMixin, View):
    """Approve bank receipt."""
    
    def post(self, request, pk):
        receipt = get_object_or_404(BankReceiptLine, pk=pk, entity=request.entity)
        
        if receipt.workflow_status not in ['DRAFT', 'PENDING_APPROVAL']:
            messages.error(request, 'Can only approve Draft or Pending Approval receipts')
            return redirect('accounting:bank_receipt_list')
        
        with transaction.atomic():
            receipt.workflow_status = 'APPROVED'
            receipt.save()
            
            AuditLog.objects.create(
                user=request.user,
                action='approve_bank_receipt',
                model_name='BankReceiptLine',
                object_id=receipt.id,
                entity=request.entity,
                description=f"Approved bank receipt: {receipt.description}"
            )
            
            messages.success(request, 'Bank receipt approved! Ready for authorization.')
        
        return redirect('accounting:bank_receipt_list')


class BankReceiptAuthorizationView(LoginRequiredMixin, SessionEntityMixin, View):
    """Authorize bank receipt and create GL entries."""
    
    def post(self, request, pk):
        receipt = get_object_or_404(BankReceiptLine, pk=pk, entity=request.entity)
        
        if receipt.workflow_status != 'APPROVED':
            messages.error(request, 'Receipt must be approved before authorization')
            return redirect('accounting:bank_receipt_list')
        
        with transaction.atomic():
            try:
                # Use provided credit_account or fallback to cash account 100001
                if receipt.credit_account:
                    bank_account = receipt.credit_account
                else:
                    bank_account = Account.objects.get(
                        entity=request.entity,
                        account_number='100001'  # Cash account
                    )
                
                # Create DEBIT entry to bank/cash account (increasing cash)
                LedgerEntry.objects.create(
                    entity=request.entity,
                    account=bank_account,  # DEBIT the bank/cash account
                    entry_type='DEBIT',
                    amount=receipt.debit_amount,
                    description=f"Bank Receipt: {receipt.description}",
                    entry_date=receipt.date,
                    reference_number=f'BANK-RECEIPT-{receipt.id}',
                    is_posted=True,
                    workflow_status='AUTHORIZED'
                )
                
                # Create CREDIT entry to contributor's capital account (increasing equity)
                LedgerEntry.objects.create(
                    entity=request.entity,
                    account=receipt.account,  # CREDIT the contributor's capital account
                    entry_type='CREDIT',
                    amount=receipt.credit_amount,
                    description=f"Bank Receipt: {receipt.description}",
                    entry_date=receipt.date,
                    reference_number=f'BANK-RECEIPT-{receipt.id}',
                    is_posted=True,
                    workflow_status='AUTHORIZED'
                )
                
                # Update receipt status
                receipt.workflow_status = 'AUTHORIZED'
                receipt.status = 'POSTED'
                receipt.save()
                
                AuditLog.objects.create(
                    user=request.user,
                    action='authorize_bank_receipt',
                    model_name='BankReceiptLine',
                    object_id=receipt.id,
                    entity=request.entity,
                    description=f"Authorized and posted bank receipt: {receipt.description}"
                )
                
                messages.success(request, 'Bank receipt authorized and posted to GL!')
            except Account.DoesNotExist:
                messages.error(request, 'Bank account (1000) not found in system!')
            except Exception as e:
                messages.error(request, f'Error authorizing receipt: {str(e)}')
        
        return redirect('accounting:bank_receipt_list')


class BankReceiptRejectView(LoginRequiredMixin, SessionEntityMixin, View):
    """Reject bank receipt."""
    
    def post(self, request, pk):
        receipt = get_object_or_404(BankReceiptLine, pk=pk, entity=request.entity)
        
        if receipt.workflow_status in ['AUTHORIZED', 'POSTED']:
            messages.error(request, 'Cannot reject authorized or posted receipts')
            return redirect('accounting:bank_receipt_list')
        
        with transaction.atomic():
            receipt.workflow_status = 'REJECTED'
            receipt.save()
            
            AuditLog.objects.create(
                user=request.user,
                action='reject_bank_receipt',
                model_name='BankReceiptLine',
                object_id=receipt.id,
                entity=request.entity,
                description=f"Rejected bank receipt: {receipt.description}"
            )
            
            messages.success(request, 'Bank receipt rejected.')
        
        return redirect('accounting:bank_receipt_list')


# ============ BANK PAYMENT WORKFLOW VIEWS ============

class BankPaymentApprovalView(LoginRequiredMixin, SessionEntityMixin, View):
    """Approve bank payment."""
    
    def post(self, request, pk):
        payment = get_object_or_404(BankPaymentLine, pk=pk, entity=request.entity)
        
        if payment.workflow_status not in ['DRAFT', 'PENDING_APPROVAL']:
            messages.error(request, 'Can only approve Draft or Pending Approval payments')
            return redirect('accounting:bank_payment_list')
        
        with transaction.atomic():
            payment.workflow_status = 'APPROVED'
            payment.save()
            
            AuditLog.objects.create(
                user=request.user,
                action='approve_bank_payment',
                model_name='BankPaymentLine',
                object_id=payment.id,
                entity=request.entity,
                description=f"Approved bank payment: {payment.description}"
            )
            
            messages.success(request, 'Bank payment approved! Ready for authorization.')
        
        return redirect('accounting:bank_payment_list')


class BankPaymentAuthorizationView(LoginRequiredMixin, SessionEntityMixin, View):
    """Authorize bank payment and create GL entries."""
    
    def post(self, request, pk):
        payment = get_object_or_404(BankPaymentLine, pk=pk, entity=request.entity)
        
        if payment.workflow_status != 'APPROVED':
            messages.error(request, 'Payment must be approved before authorization')
            return redirect('accounting:bank_payment_list')
        
        with transaction.atomic():
            try:
                # Use provided credit_account or fallback to cash account 100001
                if payment.credit_account:
                    bank_account = payment.credit_account
                else:
                    bank_account = Account.objects.get(
                        entity=request.entity,
                        account_number='100001'  # Cash account
                    )
                
                # Create DEBIT entry to payee's capital account (reducing their equity)
                LedgerEntry.objects.create(
                    entity=request.entity,
                    account=payment.account,  # DEBIT the payee's capital account
                    entry_type='DEBIT',
                    amount=payment.debit_amount,
                    description=f"Bank Payment: {payment.description}",
                    entry_date=payment.date,
                    reference_number=f'BANK-PAYMENT-{payment.id}',
                    is_posted=True,
                    workflow_status='AUTHORIZED'
                )
                
                # Create CREDIT entry to bank/cash account (reducing cash)
                LedgerEntry.objects.create(
                    entity=request.entity,
                    account=bank_account,  # CREDIT the bank/cash account
                    entry_type='CREDIT',
                    amount=payment.credit_amount,
                    description=f"Bank Payment: {payment.description}",
                    entry_date=payment.date,
                    reference_number=f'BANK-PAYMENT-{payment.id}',
                    is_posted=True,
                    workflow_status='AUTHORIZED'
                )
                
                # Update payment status
                payment.workflow_status = 'AUTHORIZED'
                payment.status = 'POSTED'
                payment.save()
                
                AuditLog.objects.create(
                    user=request.user,
                    action='authorize_bank_payment',
                    model_name='BankPaymentLine',
                    object_id=payment.id,
                    entity=request.entity,
                    description=f"Authorized and posted bank payment: {payment.description}"
                )
                
                messages.success(request, 'Bank payment authorized and posted to GL!')
            except Account.DoesNotExist:
                messages.error(request, 'Bank account (1000) not found in system!')
            except Exception as e:
                messages.error(request, f'Error authorizing payment: {str(e)}')
        
        return redirect('accounting:bank_payment_list')


class BankPaymentRejectView(LoginRequiredMixin, SessionEntityMixin, View):
    """Reject bank payment."""
    
    def post(self, request, pk):
        payment = get_object_or_404(BankPaymentLine, pk=pk, entity=request.entity)
        
        if payment.workflow_status in ['AUTHORIZED', 'POSTED']:
            messages.error(request, 'Cannot reject authorized or posted payments')
            return redirect('accounting:bank_payment_list')
        
        with transaction.atomic():
            payment.workflow_status = 'REJECTED'
            payment.save()
            
            AuditLog.objects.create(
                user=request.user,
                action='reject_bank_payment',
                model_name='BankPaymentLine',
                object_id=payment.id,
                entity=request.entity,
                description=f"Rejected bank payment: {payment.description}"
            )
            
            messages.success(request, 'Bank payment rejected.')
        
        return redirect('accounting:bank_payment_list')

