from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Sum, Count
from accounting.models import Stakeholder, CapitalContribution, Shareholding, Entity
from accounting.stakeholder_forms import StakeholderForm, CapitalContributionForm, ShareholdingForm
from accounting.mixins import SessionEntityMixin


# ==================== Shareholder Dashboard ====================

class ShareholderDashboardView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'shareholder/dashboard.html'
    permission_required = 'accounting.view_stakeholder'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity_id = self.request.session.get('selected_entity_id')
        
        if entity_id:
            # Filter by entity
            stakeholders = Stakeholder.objects.filter(entity_id=entity_id)
            contributions = CapitalContribution.objects.filter(entity_id=entity_id)
            shareholdings = Shareholding.objects.filter(entity_id=entity_id)
        else:
            # If no entity selected, show all (shouldn't happen with SessionEntityMixin)
            stakeholders = Stakeholder.objects.all()
            contributions = CapitalContribution.objects.all()
            shareholdings = Shareholding.objects.all()
        
        # Dashboard statistics
        context['total_stakeholders'] = stakeholders.count()
        context['total_contributions'] = contributions.count()
        context['total_shareholdings'] = shareholdings.count()
        
        # Calculate totals
        total_capital = sum(float(cc.amount_company_currency or 0) for cc in contributions)
        context['total_capital_invested'] = total_capital
        context['total_shares'] = shareholdings.aggregate(total=Sum('number_of_shares'))['total'] or 0
        
        # Top shareholders by contribution
        context['top_contributors'] = stakeholders.annotate(
            total_contributed=Sum('capital_contributions__amount_company_currency')
        ).filter(total_contributed__isnull=False).order_by('-total_contributed')[:5]
        
        # Share type distribution
        context['share_distribution'] = shareholdings.values('share_type').annotate(
            count=Count('id'),
            total_shares=Sum('number_of_shares')
        ).order_by('-total_shares')
        
        # Recent contributions
        context['recent_contributions'] = contributions.select_related('stakeholder').order_by('-contribution_date')[:5]
        
        # Pending contributions
        context['pending_contributions'] = contributions.filter(status='PENDING').count()
        
        # Recent shareholdings
        context['recent_shareholdings'] = shareholdings.select_related('stakeholder').order_by('-acquisition_date')[:5]
        
        return context


# ==================== Shareholder Views ====================

class ShareholderListView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Stakeholder
    template_name = 'shareholder/stakeholder_list.html'
    context_object_name = 'stakeholders'
    paginate_by = 20
    permission_required = 'accounting.view_stakeholder'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Use filtered queryset from mixin
        queryset = self.get_queryset()
        context['total_stakeholders'] = queryset.count()
        
        # Calculate total capital invested for this entity only
        entity_id = self.request.session.get('selected_entity_id')
        if entity_id:
            entity_contributions = CapitalContribution.objects.filter(entity_id=entity_id)
            entity_shareholdings = Shareholding.objects.filter(entity_id=entity_id)
        else:
            entity_contributions = CapitalContribution.objects.none()
            entity_shareholdings = Shareholding.objects.none()
        
        total_capital = 0
        for cc in entity_contributions:
            total_capital += float(cc.amount_company_currency or 0)
        context['total_capital'] = total_capital
        context['total_shares'] = entity_shareholdings.aggregate(total=Sum('number_of_shares'))['total'] or 0
        return context


class ShareholderDetailView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Stakeholder
    template_name = 'shareholder/stakeholder_detail.html'
    context_object_name = 'stakeholder'
    permission_required = 'accounting.view_stakeholder'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stakeholder = self.get_object()
        entity_id = self.request.session.get('selected_entity_id')
        
        # Get contributions and shareholdings
        context['contributions'] = CapitalContribution.objects.filter(stakeholder=stakeholder).order_by('-contribution_date')
        context['shareholdings'] = Shareholding.objects.filter(stakeholder=stakeholder).order_by('-acquisition_date')
        
        # Calculate total invested from completed contributions only
        completed_contributions = CapitalContribution.objects.filter(
            stakeholder=stakeholder,
            status='COMPLETED'
        )
        total_from_contributions = sum(
            float(cc.amount_company_currency or 0) for cc in completed_contributions
        )
        
        # Import ShareholderPaymentCommitment here to avoid circular imports
        from accounting.models import ShareholderPaymentCommitment
        
        # Calculate total from paid commitments
        paid_commitments = ShareholderPaymentCommitment.objects.filter(
            stakeholder=stakeholder,
            status='PAID',
            entity_id=entity_id
        )
        total_from_commitments = sum(
            float(pc.committed_amount or 0) for pc in paid_commitments
        )
        
        # Store breakdown in context
        context['completed_contributions_total'] = total_from_contributions
        context['paid_commitments_total'] = total_from_commitments
        context['completed_contributions_count'] = completed_contributions.count()
        context['paid_commitments_count'] = paid_commitments.count()
        
        return context


class InvestmentHistoryView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """Display investment history for a shareholder with timeline view."""
    model = Stakeholder
    template_name = 'shareholder/investment_history.html'
    context_object_name = 'stakeholder'
    permission_required = 'accounting.view_stakeholder'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stakeholder = self.get_object()
        
        # Get all capital contributions for this stakeholder, ordered by date
        contributions = CapitalContribution.objects.filter(
            stakeholder=stakeholder
        ).select_related('currency', 'currency_destination', 'entity').order_by('-contribution_date')
        
        context['contributions'] = contributions
        
        # Calculate statistics
        context['total_invested'] = sum(float(cc.amount_company_currency or 0) for cc in contributions)
        context['total_contributions'] = contributions.count()
        context['pending_contributions'] = contributions.filter(status='PENDING').count()
        context['completed_contributions'] = contributions.filter(status='COMPLETED').count()
        
        # By entity
        by_entity = {}
        for contribution in contributions:
            entity_name = contribution.entity.name
            if entity_name not in by_entity:
                by_entity[entity_name] = {
                    'total': 0,
                    'contributions': [],
                    'entity': contribution.entity
                }
            by_entity[entity_name]['total'] += float(contribution.amount_company_currency or 0)
            by_entity[entity_name]['contributions'].append(contribution)
        
        context['contributions_by_entity'] = by_entity
        
        return context


class ShareholderCreateView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Stakeholder
    form_class = StakeholderForm
    template_name = 'shareholder/stakeholder_form.html'
    permission_required = 'accounting.add_stakeholder'
    success_url = reverse_lazy('shareholder:stakeholder-list')

    def get_initial(self):
        initial = super().get_initial()
        entity_id = self.request.session.get('selected_entity_id')
        if entity_id:
            from accounting.models import Entity
            try:
                initial['entity'] = Entity.objects.get(id=entity_id)
            except:
                pass
        return initial

    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        if entity_id:
            from accounting.models import Entity
            from django.utils import timezone
            try:
                form.instance.entity = Entity.objects.get(id=entity_id)
                # Set default joined_date if not provided
                if not form.instance.joined_date:
                    form.instance.joined_date = timezone.now().date()
            except:
                pass
        return super().form_valid(form)


class ShareholderUpdateView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Stakeholder
    form_class = StakeholderForm
    template_name = 'shareholder/stakeholder_form.html'
    permission_required = 'accounting.change_stakeholder'
    success_url = reverse_lazy('shareholder:stakeholder-list')

    def get_queryset(self):
        # Filter by session entity using mixin
        return super().get_queryset()


class ShareholderDeleteView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Stakeholder
    template_name = 'shareholder/stakeholder_confirm_delete.html'
    permission_required = 'accounting.delete_stakeholder'
    success_url = reverse_lazy('shareholder:stakeholder-list')

    def get_queryset(self):
        # Filter by session entity using mixin
        return super().get_queryset()


# ==================== Capital Contribution Views ====================

class CapitalContributionListView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = CapitalContribution
    template_name = 'shareholder/capital_contribution_list.html'
    context_object_name = 'contributions'
    paginate_by = 20
    permission_required = 'accounting.view_capitalcontribution'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Use filtered queryset from mixin instead of CapitalContribution.objects.all()
        queryset = self.get_queryset()
        context['total_contributions'] = queryset.count()
        context['pending_total'] = queryset.filter(status='PENDING').aggregate(total=Sum('amount'))['total'] or 0
        context['completed_total'] = queryset.filter(status='COMPLETED').aggregate(total=Sum('amount_company_currency'))['total'] or 0
        return context


class CapitalContributionDetailView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = CapitalContribution
    template_name = 'shareholder/capital_contribution_detail.html'
    context_object_name = 'contribution'
    permission_required = 'accounting.view_capitalcontribution'

    def get_queryset(self):
        # Filter by session entity using mixin
        return super().get_queryset()


class CapitalContributionCreateView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = CapitalContribution
    form_class = CapitalContributionForm
    template_name = 'shareholder/capital_contribution_form.html'
    permission_required = 'accounting.add_capitalcontribution'
    success_url = reverse_lazy('shareholder:capital-contribution-list')

    def get_initial(self):
        initial = super().get_initial()
        stakeholder_id = self.kwargs.get('stakeholder_id')
        entity_id = self.request.session.get('selected_entity_id')
        
        if stakeholder_id:
            initial['stakeholder'] = Stakeholder.objects.get(pk=stakeholder_id)
        if entity_id:
            from accounting.models import Entity
            try:
                initial['entity'] = Entity.objects.get(id=entity_id)
            except:
                pass
        return initial

    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        if entity_id:
            from accounting.models import Entity
            from django.utils import timezone
            try:
                form.instance.entity = Entity.objects.get(id=entity_id)
                # Set default contribution_date if not provided
                if not form.instance.contribution_date:
                    form.instance.contribution_date = timezone.now().date()
            except:
                pass
        return super().form_valid(form)


class CapitalContributionUpdateView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = CapitalContribution
    form_class = CapitalContributionForm
    template_name = 'shareholder/capital_contribution_form.html'
    permission_required = 'accounting.change_capitalcontribution'
    success_url = reverse_lazy('shareholder:capital-contribution-list')

    def get_queryset(self):
        # Filter by session entity using mixin
        return super().get_queryset()


# ==================== Shareholding Views ====================

class ShareholdingListView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Shareholding
    template_name = 'shareholder/shareholding_list.html'
    context_object_name = 'shareholdings'
    paginate_by = 20
    permission_required = 'accounting.view_shareholding'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Use filtered queryset from mixin
        queryset = self.get_queryset()
        context['total_shares'] = queryset.aggregate(total=Sum('number_of_shares'))['total'] or 0
        context['share_types'] = queryset.values('share_type').annotate(count=Count('id'), total_shares=Sum('number_of_shares'))
        return context


class ShareholdingDetailView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Shareholding
    template_name = 'shareholder/shareholding_detail.html'
    context_object_name = 'shareholding'
    permission_required = 'accounting.view_shareholding'

    def get_queryset(self):
        # Filter by session entity using mixin
        return super().get_queryset()


class ShareholdingCreateView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Shareholding
    form_class = ShareholdingForm
    template_name = 'shareholder/shareholding_form.html'
    permission_required = 'accounting.add_shareholding'
    success_url = reverse_lazy('shareholder:shareholding-list')

    def get_initial(self):
        initial = super().get_initial()
        stakeholder_id = self.kwargs.get('stakeholder_id')
        entity_id = self.request.session.get('selected_entity_id')
        
        if stakeholder_id:
            initial['stakeholder'] = Stakeholder.objects.get(pk=stakeholder_id)
        if entity_id:
            from accounting.models import Entity
            try:
                initial['entity'] = Entity.objects.get(id=entity_id)
            except:
                pass
        return initial

    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        if entity_id:
            from accounting.models import Entity
            from django.utils import timezone
            try:
                form.instance.entity = Entity.objects.get(id=entity_id)
                # Set default acquisition_date if not provided
                if not form.instance.acquisition_date:
                    form.instance.acquisition_date = timezone.now().date()
            except:
                pass
        return super().form_valid(form)


class ShareholdingUpdateView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Shareholding
    form_class = ShareholdingForm
    template_name = 'shareholder/shareholding_form.html'
    permission_required = 'accounting.change_shareholding'
    success_url = reverse_lazy('shareholder:shareholding-list')

    def get_queryset(self):
        # Filter by session entity using mixin
        return super().get_queryset()


# ==================== Shareholder Investment Tracking ====================

from accounting.models import ShareholderInvestmentLimit, ShareholderPaymentCommitment
from shareholder.forms import ShareholderInvestmentLimitForm, ShareholderPaymentCommitmentForm


class ShareholderInvestmentReportView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """Report showing investment status for all shareholders."""
    template_name = 'shareholder/investment_report.html'
    permission_required = 'accounting.view_stakeholder'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id).first()
        
        if not entity:
            context['investment_data'] = []
            return context
        
        # Get all investment limits for this entity
        limits = ShareholderInvestmentLimit.objects.filter(entity=entity, is_active=True)
        
        investment_data = []
        for limit in limits:
            # Get next pending/overdue commitment OR most recent paid commitment
            pending_commitments = ShareholderPaymentCommitment.objects.filter(
                stakeholder=limit.stakeholder,
                entity=entity,
                status__in=['PENDING', 'OVERDUE']
            ).first()
            
            # If no pending, get the most recent paid commitment for display
            paid_commitment = None
            if not pending_commitments:
                paid_commitment = ShareholderPaymentCommitment.objects.filter(
                    stakeholder=limit.stakeholder,
                    entity=entity,
                    status='PAID'
                ).order_by('-actual_payment_date').first()
            
            # Use the stakeholder's total_invested property (includes completed contributions + paid commitments)
            actual_invested_amount = limit.stakeholder.total_invested
            # Convert to Decimal for calculation consistency
            from decimal import Decimal
            target_amount = Decimal(str(limit.target_investment_amount))
            invested_amount = Decimal(str(actual_invested_amount))
            balance_to_invest = target_amount - invested_amount
            invested_percentage = float((invested_amount / target_amount * 100)) if target_amount > 0 else 0
            
            # Determine if investment is completed
            is_completed = balance_to_invest <= 0
            
            # Clear next payment info if investment is completed
            if is_completed:
                pending_commitments = None
                paid_commitment = None
            
            investment_data.append({
                'stakeholder': limit.stakeholder,
                'target_amount': limit.target_investment_amount,
                'invested_amount': actual_invested_amount,
                'balance_to_invest': balance_to_invest,
                'invested_percentage': invested_percentage,
                'currency': limit.currency,
                'next_payment_date': pending_commitments.promised_payment_date if pending_commitments else (paid_commitment.actual_payment_date if paid_commitment else None),
                'next_payment_amount': pending_commitments.committed_amount if pending_commitments else (paid_commitment.committed_amount if paid_commitment else None),
                'is_overdue': pending_commitments.is_overdue if pending_commitments else False,
                'next_payment_id': pending_commitments.id if pending_commitments else (paid_commitment.id if paid_commitment else None),
                'payment_status': pending_commitments.status if pending_commitments else (paid_commitment.status if paid_commitment else None),
                'is_completed': is_completed,
            })
        
        context['investment_data'] = investment_data
        context['entity'] = entity
        return context


class ShareholderInvestmentLimitCreateView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Create shareholder investment limit."""
    model = ShareholderInvestmentLimit
    form_class = ShareholderInvestmentLimitForm
    template_name = 'shareholder/investment_limit_form.html'
    permission_required = 'accounting.add_shareholderinvestmentlimit'
    success_url = reverse_lazy('shareholder:investment_report')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity_id = self.request.session.get('selected_entity_id')
        # Filter stakeholders for this entity in the form
        if 'data' not in kwargs:
            entity = Entity.objects.filter(id=entity_id).first()
            if entity:
                initial = kwargs.get('initial', {})
                initial['entity'] = entity
                kwargs['initial'] = initial
        return kwargs

    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        form.instance.entity_id = entity_id
        form.instance.update_totals()
        return super().form_valid(form)


class ShareholderInvestmentLimitUpdateView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Update shareholder investment limit."""
    model = ShareholderInvestmentLimit
    form_class = ShareholderInvestmentLimitForm
    template_name = 'shareholder/investment_limit_form.html'
    permission_required = 'accounting.change_shareholderinvestmentlimit'
    success_url = reverse_lazy('shareholder:investment_report')

    def form_valid(self, form):
        form.instance.update_totals()
        return super().form_valid(form)


class ShareholderPaymentCommitmentCreateView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Create shareholder payment commitment."""
    model = ShareholderPaymentCommitment
    form_class = ShareholderPaymentCommitmentForm
    template_name = 'shareholder/payment_commitment_form.html'
    permission_required = 'accounting.add_shareholderpaymentcommitment'
    success_url = reverse_lazy('shareholder:investment_report')

    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        form.instance.entity_id = entity_id
        return super().form_valid(form)


class ShareholderPaymentCommitmentUpdateView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Update shareholder payment commitment."""
    model = ShareholderPaymentCommitment
    form_class = ShareholderPaymentCommitmentForm
    template_name = 'shareholder/payment_commitment_form.html'
    permission_required = 'accounting.change_shareholderpaymentcommitment'
    success_url = reverse_lazy('shareholder:investment_report')

    def form_valid(self, form):
        commitment = form.instance
        
        # When status is changed to PAID, update investment limit totals
        if form.cleaned_data.get('status') == 'PAID':
            try:
                investment_limit = ShareholderInvestmentLimit.objects.get(
                    stakeholder=commitment.stakeholder,
                    entity=commitment.entity
                )
                # Recalculate totals after payment is marked as paid
                investment_limit.update_totals()
            except ShareholderInvestmentLimit.DoesNotExist:
                pass
        
        return super().form_valid(form)

