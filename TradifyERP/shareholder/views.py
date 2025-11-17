from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Sum, Count
from accounting.models import Stakeholder, CapitalContribution, Shareholding
from accounting.stakeholder_forms import StakeholderForm, CapitalContributionForm, ShareholdingForm


# ==================== Shareholder Views ====================

class ShareholderListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Stakeholder
    template_name = 'shareholder/stakeholder_list.html'
    context_object_name = 'stakeholders'
    paginate_by = 20
    permission_required = 'accounting.view_stakeholder'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_stakeholders'] = Stakeholder.objects.count()
        # Calculate total capital invested (using amount_company_currency for consistency)
        total_capital = 0
        for cc in CapitalContribution.objects.all():
            total_capital += float(cc.amount_company_currency or 0)
        context['total_capital'] = total_capital
        context['total_shares'] = Shareholding.objects.aggregate(total=Sum('number_of_shares'))['total'] or 0
        return context


class ShareholderDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
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


class ShareholderCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Stakeholder
    form_class = StakeholderForm
    template_name = 'shareholder/stakeholder_form.html'
    permission_required = 'accounting.add_stakeholder'
    success_url = reverse_lazy('shareholder:stakeholder-list')


class ShareholderUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Stakeholder
    form_class = StakeholderForm
    template_name = 'shareholder/stakeholder_form.html'
    permission_required = 'accounting.change_stakeholder'
    success_url = reverse_lazy('shareholder:stakeholder-list')


class ShareholderDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Stakeholder
    template_name = 'shareholder/stakeholder_confirm_delete.html'
    permission_required = 'accounting.delete_stakeholder'
    success_url = reverse_lazy('shareholder:stakeholder-list')


# ==================== Capital Contribution Views ====================

class CapitalContributionListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = CapitalContribution
    template_name = 'shareholder/capital_contribution_list.html'
    context_object_name = 'contributions'
    paginate_by = 20
    permission_required = 'accounting.view_capitalcontribution'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_contributions'] = CapitalContribution.objects.count()
        context['pending_total'] = CapitalContribution.objects.filter(status='PENDING').aggregate(total=Sum('amount'))['total'] or 0
        context['completed_total'] = CapitalContribution.objects.filter(status='COMPLETED').aggregate(total=Sum('amount_company_currency'))['total'] or 0
        return context


class CapitalContributionDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = CapitalContribution
    template_name = 'shareholder/capital_contribution_detail.html'
    context_object_name = 'contribution'
    permission_required = 'accounting.view_capitalcontribution'


class CapitalContributionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = CapitalContribution
    form_class = CapitalContributionForm
    template_name = 'shareholder/capital_contribution_form.html'
    permission_required = 'accounting.add_capitalcontribution'
    success_url = reverse_lazy('shareholder:capital-contribution-list')

    def get_initial(self):
        initial = super().get_initial()
        stakeholder_id = self.kwargs.get('stakeholder_id')
        if stakeholder_id:
            initial['stakeholder'] = Stakeholder.objects.get(pk=stakeholder_id)
        return initial


class CapitalContributionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = CapitalContribution
    form_class = CapitalContributionForm
    template_name = 'shareholder/capital_contribution_form.html'
    permission_required = 'accounting.change_capitalcontribution'
    success_url = reverse_lazy('shareholder:capital-contribution-list')


# ==================== Shareholding Views ====================

class ShareholdingListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Shareholding
    template_name = 'shareholder/shareholding_list.html'
    context_object_name = 'shareholdings'
    paginate_by = 20
    permission_required = 'accounting.view_shareholding'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_shares'] = Shareholding.objects.aggregate(total=Sum('number_of_shares'))['total'] or 0
        context['share_types'] = Shareholding.objects.values('share_type').annotate(count=Count('id'), total_shares=Sum('number_of_shares'))
        return context


class ShareholdingDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Shareholding
    template_name = 'shareholder/shareholding_detail.html'
    context_object_name = 'shareholding'
    permission_required = 'accounting.view_shareholding'


class ShareholdingCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Shareholding
    form_class = ShareholdingForm
    template_name = 'shareholder/shareholding_form.html'
    permission_required = 'accounting.add_shareholding'
    success_url = reverse_lazy('shareholder:shareholding-list')

    def get_initial(self):
        initial = super().get_initial()
        stakeholder_id = self.kwargs.get('stakeholder_id')
        if stakeholder_id:
            initial['stakeholder'] = Stakeholder.objects.get(pk=stakeholder_id)
        return initial


class ShareholdingUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Shareholding
    form_class = ShareholdingForm
    template_name = 'shareholder/shareholding_form.html'
    permission_required = 'accounting.change_shareholding'
    success_url = reverse_lazy('shareholder:shareholding-list')
