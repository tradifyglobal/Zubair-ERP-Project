from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Sum, Count, Q, F
from .models import (
    Account, LedgerEntry, Entity, CapitalContribution, 
    Currency, Account
)
from accounting.mixins import SessionEntityMixin


class AccountingDashboardView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """Main accounting dashboard showing cash position and financial summary."""
    template_name = 'accounting/dashboard.html'
    permission_required = 'accounting.view_account'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity_id = self.request.session.get('selected_entity_id')
        
        if entity_id:
            try:
                entity = Entity.objects.get(id=entity_id)
                context['entity'] = entity
                
                # Get all cash accounts (ASSET type accounts with 'cash' or 'bank' in name)
                cash_accounts = Account.objects.filter(
                    entity_id=entity_id,
                    account_type='ASSET'
                ).filter(
                    Q(name__icontains='cash') | 
                    Q(name__icontains='bank') | 
                    Q(account_number__startswith='10')  # Typical cash account range
                )
                
                context['cash_accounts'] = cash_accounts
                
                # Calculate total cash balance
                total_cash_balance = 0
                cash_account_details = []
                
                for account in cash_accounts:
                    # Calculate balance: Debits - Credits
                    debits = account.ledger_entries.filter(
                        entry_type='DEBIT'
                    ).aggregate(total=Sum('amount'))['total'] or 0
                    
                    credits = account.ledger_entries.filter(
                        entry_type='CREDIT'
                    ).aggregate(total=Sum('amount'))['total'] or 0
                    
                    balance = float(debits) - float(credits)
                    total_cash_balance += balance
                    
                    cash_account_details.append({
                        'account': account,
                        'balance': balance,
                        'debits': debits,
                        'credits': credits
                    })
                
                context['cash_account_details'] = cash_account_details
                context['total_cash_balance'] = total_cash_balance
                
                # Capital contributions to this entity
                contributions = CapitalContribution.objects.filter(
                    entity_id=entity_id,
                    status='COMPLETED'
                ).select_related('stakeholder', 'currency', 'currency_destination')
                
                context['total_contributions'] = contributions.count()
                context['total_capital_received'] = sum(
                    float(c.amount_company_currency or 0) for c in contributions
                )
                context['total_capital_received_usd'] = sum(
                    float(c.amount_usd or 0) for c in contributions
                )
                
                # Pending contributions
                pending_contributions = CapitalContribution.objects.filter(
                    entity_id=entity_id,
                    status='PENDING'
                )
                context['pending_contributions_count'] = pending_contributions.count()
                context['pending_contributions_amount'] = sum(
                    float(c.amount_company_currency or 0) for c in pending_contributions
                )
                
                # Top contributors
                context['top_contributors'] = (
                    contributions
                    .values('stakeholder__first_name', 'stakeholder__last_name', 'stakeholder__id')
                    .annotate(total=Sum('amount_company_currency'))
                    .order_by('-total')[:5]
                )
                
                # Recent contributions
                context['recent_contributions'] = contributions.order_by('-contribution_date')[:5]
                
                # Capital by source currency
                capital_by_currency = (
                    contributions
                    .values('currency__code', 'currency__name')
                    .annotate(
                        count=Count('id'),
                        total_original=Sum('amount'),
                        total_converted=Sum('amount_company_currency')
                    )
                    .order_by('-total_converted')
                )
                context['capital_by_currency'] = capital_by_currency
                
                # Equity accounts balance (where capital contributions are credited)
                equity_accounts = Account.objects.filter(
                    entity_id=entity_id,
                    account_type='EQUITY'
                )
                
                equity_balance = 0
                equity_details = []
                
                for account in equity_accounts:
                    debits = account.ledger_entries.filter(
                        entry_type='DEBIT'
                    ).aggregate(total=Sum('amount'))['total'] or 0
                    
                    credits = account.ledger_entries.filter(
                        entry_type='CREDIT'
                    ).aggregate(total=Sum('amount'))['total'] or 0
                    
                    balance = float(credits) - float(debits)  # Equity: Credits - Debits
                    equity_balance += balance
                    
                    equity_details.append({
                        'account': account,
                        'balance': balance,
                        'debits': debits,
                        'credits': credits
                    })
                
                context['equity_accounts'] = equity_details
                context['total_equity'] = equity_balance
                
                # Ledger entries related to capital contributions
                context['capital_ledger_entries'] = LedgerEntry.objects.filter(
                    entity_id=entity_id,
                    capital_contribution__isnull=False
                ).select_related('account', 'capital_contribution').order_by('-entry_date')[:10]
                
            except Entity.DoesNotExist:
                context['error'] = 'Entity not found'
        else:
            context['error'] = 'No entity selected'
        
        return context


class CashPositionView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """Detailed view of company's cash position from investor contributions."""
    template_name = 'accounting/cash_position.html'
    permission_required = 'accounting.view_account'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity_id = self.request.session.get('selected_entity_id')
        
        if entity_id:
            try:
                entity = Entity.objects.get(id=entity_id)
                context['entity'] = entity
                
                # All capital contributions
                all_contributions = CapitalContribution.objects.filter(
                    entity_id=entity_id
                ).select_related('stakeholder', 'currency', 'currency_destination')
                
                # Summary by status
                completed = all_contributions.filter(status='COMPLETED')
                pending = all_contributions.filter(status='PENDING')
                cancelled = all_contributions.filter(status='CANCELLED')
                
                context['summary'] = {
                    'completed': {
                        'count': completed.count(),
                        'amount': sum(float(c.amount_company_currency or 0) for c in completed),
                    },
                    'pending': {
                        'count': pending.count(),
                        'amount': sum(float(c.amount_company_currency or 0) for c in pending),
                    },
                    'cancelled': {
                        'count': cancelled.count(),
                        'amount': sum(float(c.amount_company_currency or 0) for c in cancelled),
                    }
                }
                
                context['total_received'] = context['summary']['completed']['amount']
                context['total_pending'] = context['summary']['pending']['amount']
                
                # Detailed timeline
                context['contributions_timeline'] = all_contributions.order_by('-contribution_date')
                
                # By entity - ONLY for current entity (not all entities)
                entities_with_contributions = (
                    CapitalContribution.objects
                    .filter(status='COMPLETED', entity_id=entity_id)
                    .values('entity__name', 'entity__code')
                    .annotate(total=Sum('amount_company_currency'), count=Count('id'))
                    .order_by('-total')
                )
                context['by_entity'] = entities_with_contributions
                
            except Entity.DoesNotExist:
                context['error'] = 'Entity not found'
        else:
            context['error'] = 'No entity selected'
        
        return context
