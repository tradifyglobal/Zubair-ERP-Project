"""
Views for Shareholder Investment Register & Reports
Place this in: TradifyERP/accounting/views_reports.py (or accounting/views_shareholder.py)
"""

from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Sum, Count, Q, Min, Max, Avg, F, DecimalField
from django.db.models.functions import TruncDate
from datetime import timedelta, date
from .models import (
    ShareholderInvestmentRegister, ShareholderInvestmentSummary,
    CashReceiptLine, BankReceiptLine, Stakeholder, Entity
)
from .mixins import SessionEntityMixin
from accounting.models import AuditLog


class ShareholderInvestmentRegisterListView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    List all shareholder investments with filtering and sorting capabilities.
    """
    model = ShareholderInvestmentRegister
    template_name = 'accounting/shareholder_investment_register_list.html'
    context_object_name = 'investments'
    permission_required = 'accounting.view_sharehoiderinvestmentregister'
    paginate_by = 50
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        queryset = ShareholderInvestmentRegister.objects.filter(
            entity_id=entity_id
        ).select_related(
            'stakeholder',
            'currency',
            'source_cash_receipt',
            'source_bank_receipt',
            'created_by'
        ).order_by('-investment_date', '-created_date')
        
        # Filtering
        stakeholder_id = self.request.GET.get('stakeholder')
        if stakeholder_id:
            queryset = queryset.filter(stakeholder_id=stakeholder_id)
        
        investment_type = self.request.GET.get('type')
        if investment_type:
            queryset = queryset.filter(investment_type=investment_type)
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Date Range
        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')
        if from_date:
            queryset = queryset.filter(investment_date__gte=from_date)
        if to_date:
            queryset = queryset.filter(investment_date__lte=to_date)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity_id = self.request.session.get('selected_entity_id')
        
        # Summary Statistics
        investments = ShareholderInvestmentRegister.objects.filter(entity_id=entity_id)
        
        context['total_investments'] = investments.count()
        context['total_amount'] = investments.aggregate(
            Sum('amount_company_currency')
        )['amount_company_currency__sum'] or 0
        
        context['by_status'] = investments.values('status').annotate(
            count=Count('id'),
            amount=Sum('amount_company_currency')
        )
        
        context['by_type'] = investments.values('investment_type').annotate(
            count=Count('id'),
            amount=Sum('amount_company_currency')
        )
        
        # Filter options
        context['stakeholders'] = Stakeholder.objects.filter(
            investment_register__entity_id=entity_id
        ).distinct()
        
        context['investment_types'] = ShareholderInvestmentRegister.INVESTMENT_TYPE_CHOICES
        context['statuses'] = ShareholderInvestmentRegister.STATUS_CHOICES
        
        return context


class ShareholderInvestmentDetailView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """
    Detailed view of individual shareholder investment with full history.
    """
    model = ShareholderInvestmentRegister
    template_name = 'accounting/shareholder_investment_detail.html'
    permission_required = 'accounting.view_sharehoiderinvestmentregister'
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        return ShareholderInvestmentRegister.objects.filter(entity_id=entity_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        investment = self.object
        
        # Get related GL entries if linked
        if investment.gl_reference:
            from .models import LedgerEntry
            context['gl_entries'] = LedgerEntry.objects.filter(
                reference_number=investment.gl_reference
            )
        
        # Get audit trail
        context['audit_trail'] = AuditLog.objects.filter(
            model_name='CashReceiptLine',
            object_id=investment.source_cash_receipt_id if investment.source_cash_receipt else investment.source_bank_receipt_id
        ).order_by('-timestamp')
        
        # Get other investments by same stakeholder
        context['other_investments'] = ShareholderInvestmentRegister.objects.filter(
            stakeholder=investment.stakeholder,
            entity=investment.entity
        ).exclude(id=investment.id).order_by('-investment_date')[:10]
        
        return context


class ShareholderInvestmentReportView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """
    Comprehensive shareholder investment summary report.
    
    Shows:
    - All stakeholders with total contributions
    - Contribution count and average
    - Status breakdown
    - Investment type distribution
    - Charts and visualizations
    """
    template_name = 'accounting/shareholder_investment_report.html'
    permission_required = 'accounting.view_sharehoiderinvestmentregister'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity_id = self.request.session.get('selected_entity_id')
        
        try:
            entity = Entity.objects.get(id=entity_id)
            context['entity'] = entity
        except Entity.DoesNotExist:
            context['error'] = 'Entity not found'
            return context
        
        # Get all investments for entity
        all_investments = ShareholderInvestmentRegister.objects.filter(
            entity=entity
        )
        
        # === OVERALL SUMMARY ===
        overall_stats = all_investments.aggregate(
            total_invested=Sum('amount_company_currency'),
            investment_count=Count('id'),
            avg_investment=Avg('amount_company_currency'),
            completed_count=Count('id', filter=Q(status='COMPLETED')),
            pending_count=Count('id', filter=Q(status='PENDING')),
            cancelled_count=Count('id', filter=Q(status='CANCELLED')),
        )
        
        context['overall_stats'] = overall_stats
        
        # === SHAREHOLDER SUMMARY ===
        shareholder_summary = all_investments.values(
            'stakeholder__id',
            'stakeholder__name',
            'stakeholder__email'
        ).annotate(
            total_amount=Sum('amount_company_currency'),
            contribution_count=Count('id'),
            first_date=Min('investment_date'),
            last_date=Max('investment_date'),
            avg_amount=Avg('amount_company_currency'),
            completed=Count('id', filter=Q(status='COMPLETED')),
            pending=Count('id', filter=Q(status='PENDING')),
            cancelled=Count('id', filter=Q(status='CANCELLED')),
        ).order_by('-total_amount')
        
        context['shareholder_summary'] = shareholder_summary
        
        # === BY INVESTMENT TYPE ===
        by_type = all_investments.values('investment_type').annotate(
            total=Sum('amount_company_currency'),
            count=Count('id'),
            completed=Count('id', filter=Q(status='COMPLETED')),
            pending=Count('id', filter=Q(status='PENDING')),
        ).order_by('-total')
        
        context['by_type'] = by_type
        
        # === BY STATUS ===
        by_status = all_investments.values('status').annotate(
            total=Sum('amount_company_currency'),
            count=Count('id'),
        )
        
        context['by_status'] = by_status
        
        # === MONTHLY TREND ===
        monthly_trend = all_investments.annotate(
            month=TruncDate('investment_date')
        ).values('month').annotate(
            total=Sum('amount_company_currency'),
            count=Count('id'),
            completed=Count('id', filter=Q(status='COMPLETED')),
        ).order_by('month')
        
        context['monthly_trend'] = monthly_trend
        
        # === RECENT INVESTMENTS ===
        context['recent_investments'] = all_investments.order_by(
            '-investment_date'
        )[:10]
        
        # === PENDING INVESTMENTS (needs authorization/approval) ===
        context['pending_investments'] = all_investments.filter(
            status='PENDING'
        ).order_by('investment_date')
        
        # === TOTALS ===
        context['total_received'] = overall_stats['total_invested'] or 0
        context['total_pending'] = all_investments.filter(
            status='PENDING'
        ).aggregate(Sum('amount_company_currency'))['amount_company_currency__sum'] or 0
        
        return context


class ShareholderCapitalStatusView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """
    Dashboard showing capital contribution status by shareholder.
    
    Similar to ShareholderInvestmentReportView but focused on CAPITAL investment type.
    """
    template_name = 'accounting/shareholder_capital_status.html'
    permission_required = 'accounting.view_account'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity_id = self.request.session.get('selected_entity_id')
        
        # Get only CAPITAL contributions
        capital_investments = ShareholderInvestmentRegister.objects.filter(
            entity_id=entity_id,
            investment_type='CAPITAL'
        )
        
        # === SUMMARY ===
        summary = capital_investments.aggregate(
            total_capital=Sum('amount_company_currency'),
            shareholder_count=Count('stakeholder', distinct=True),
            completed_count=Count('id', filter=Q(status='COMPLETED')),
            pending_count=Count('id', filter=Q(status='PENDING')),
        )
        
        context['summary'] = summary
        
        # === BY SHAREHOLDER ===
        shareholder_capitals = capital_investments.values(
            'stakeholder__name'
        ).annotate(
            total_capital=Sum('amount_company_currency'),
            contribution_count=Count('id'),
            latest_date=Max('investment_date'),
            status=F('status')
        ).order_by('-total_capital')
        
        context['shareholder_capitals'] = shareholder_capitals
        
        # === PIE CHART DATA ===
        context['pie_data'] = [
            {
                'name': item['stakeholder__name'],
                'value': float(item['total_capital'])
            }
            for item in shareholder_capitals
        ]
        
        return context


class ShareholderInvestmentAuditTrailView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """
    Audit trail for a specific investment showing all approvals and GL entries.
    """
    model = ShareholderInvestmentRegister
    template_name = 'accounting/shareholder_investment_audit_trail.html'
    permission_required = 'accounting.view_sharehoiderinvestmentregister'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        investment = self.object
        
        # Get source receipt (either cash or bank)
        if investment.source_cash_receipt:
            receipt = investment.source_cash_receipt
            model_name = 'CashReceiptLine'
        else:
            receipt = investment.source_bank_receipt
            model_name = 'BankReceiptLine'
        
        # Get complete audit trail for this receipt
        audit_trail = AuditLog.objects.filter(
            model_name=model_name,
            object_id=receipt.id
        ).select_related('user').order_by('timestamp')
        
        context['audit_trail'] = audit_trail
        context['receipt'] = receipt
        
        # Get GL entries if posted
        if investment.gl_reference:
            from .models import LedgerEntry
            context['gl_entries'] = LedgerEntry.objects.filter(
                reference_number=investment.gl_reference
            ).order_by('-created_at')
        
        # Timeline visualization data
        timeline_events = []
        for log in audit_trail:
            timeline_events.append({
                'timestamp': log.timestamp,
                'action': log.get_action_display(),
                'user': log.user.get_full_name() or log.user.username,
                'description': log.description,
                'details': log.changes if hasattr(log, 'changes') else {}
            })
        
        context['timeline_events'] = timeline_events
        
        return context
