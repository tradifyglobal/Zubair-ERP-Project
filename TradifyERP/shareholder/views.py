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
        context['contributions'] = CapitalContribution.objects.filter(stakeholder=stakeholder).order_by('-contribution_date')
        context['shareholdings'] = Shareholding.objects.filter(stakeholder=stakeholder).order_by('-acquisition_date')
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
