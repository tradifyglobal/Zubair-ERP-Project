from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum, Q
from accounting.models import Stakeholder, CapitalContribution, Shareholding, Entity, AuditLog
from accounting.stakeholder_forms import StakeholderForm, CapitalContributionForm, ShareholdingForm


# ============ STAKEHOLDER VIEWS ============

class StakeholderListView(LoginRequiredMixin, ListView):
    """List all stakeholders."""
    model = Stakeholder
    template_name = 'accounting/stakeholder_list.html'
    context_object_name = 'stakeholders'
    paginate_by = 25
    
    def get_queryset(self):
        entity = Entity.objects.filter(is_active=True).first()
        if not entity:
            return Stakeholder.objects.none()
        return Stakeholder.objects.filter(entity=entity).select_related('entity')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            context['total_stakeholders'] = Stakeholder.objects.filter(entity=entity).count()
            context['total_capital'] = CapitalContribution.objects.filter(
                entity=entity, status='COMPLETED'
            ).aggregate(Sum('amount_company_currency'))['amount_company_currency__sum'] or 0
            context['total_shares'] = Shareholding.objects.filter(
                entity=entity, is_active=True
            ).aggregate(Sum('number_of_shares'))['number_of_shares__sum'] or 0
        return context


class StakeholderDetailView(LoginRequiredMixin, DetailView):
    """View stakeholder details with capital contributions and shares."""
    model = Stakeholder
    template_name = 'accounting/stakeholder_detail.html'
    context_object_name = 'stakeholder'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stakeholder = self.object
        context['capital_contributions'] = CapitalContribution.objects.filter(
            stakeholder=stakeholder
        ).select_related('currency', 'currency_destination')
        context['shareholdings'] = Shareholding.objects.filter(
            stakeholder=stakeholder
        ).select_related('acquisition_currency')
        context['total_invested'] = stakeholder.total_invested
        context['total_shares'] = stakeholder.total_shares
        context['ownership_percentage'] = stakeholder.ownership_percentage
        return context


class StakeholderCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Create a new stakeholder."""
    model = Stakeholder
    form_class = StakeholderForm
    template_name = 'accounting/stakeholder_form.html'
    success_url = reverse_lazy('accounting:stakeholder_list')
    permission_required = 'accounting.add_stakeholder'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity = Entity.objects.filter(is_active=True).first()
        return kwargs
    
    def form_valid(self, form):
        entity = Entity.objects.filter(is_active=True).first()
        if not entity:
            messages.error(self.request, 'No active entity configured.')
            return self.form_invalid(form)
        
        form.instance.entity = entity
        response = super().form_valid(form)
        
        AuditLog.objects.create(
            entity=entity,
            user=self.request.user.username,
            action='CREATE',
            model_name='Stakeholder',
            object_id=form.instance.id,
            description=f'Created stakeholder: {form.instance.full_name}'
        )
        messages.success(self.request, f'Stakeholder {form.instance.full_name} created successfully.')
        return response


class StakeholderUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Update stakeholder information."""
    model = Stakeholder
    form_class = StakeholderForm
    template_name = 'accounting/stakeholder_form.html'
    success_url = reverse_lazy('accounting:stakeholder_list')
    permission_required = 'accounting.change_stakeholder'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        AuditLog.objects.create(
            entity=self.object.entity,
            user=self.request.user.username,
            action='UPDATE',
            model_name='Stakeholder',
            object_id=self.object.id,
            description=f'Updated stakeholder: {self.object.full_name}'
        )
        messages.success(self.request, f'Stakeholder {self.object.full_name} updated successfully.')
        return response


class StakeholderDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Delete stakeholder."""
    model = Stakeholder
    template_name = 'accounting/stakeholder_confirm_delete.html'
    success_url = reverse_lazy('accounting:stakeholder_list')
    permission_required = 'accounting.delete_stakeholder'
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        AuditLog.objects.create(
            entity=obj.entity,
            user=request.user.username,
            action='DELETE',
            model_name='Stakeholder',
            object_id=obj.id,
            description=f'Deleted stakeholder: {obj.full_name}'
        )
        messages.success(request, f'Stakeholder {obj.full_name} deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ============ CAPITAL CONTRIBUTION VIEWS ============

class CapitalContributionListView(LoginRequiredMixin, ListView):
    """List all capital contributions."""
    model = CapitalContribution
    template_name = 'accounting/capital_contribution_list.html'
    context_object_name = 'object_list'
    paginate_by = 25
    
    def get_queryset(self):
        entity = Entity.objects.filter(is_active=True).first()
        if not entity:
            return CapitalContribution.objects.none()
        return CapitalContribution.objects.filter(entity=entity).select_related(
            'stakeholder', 'currency', 'currency_destination'
        )
    
    def get_context_data(self, **kwargs):
        # Write debug info to a file
        with open('/tmp/pending_debug.log', 'a') as f:
            f.write(f"\n===== ACCOUNTING CAPITAL CONTRIBUTION LIST VIEW CALLED at {__import__('datetime').datetime.now()} =====\n")
        
        context = super().get_context_data(**kwargs)
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            contributions = CapitalContribution.objects.filter(entity=entity)
            context['total_contributions'] = contributions.count()
            context['total_amount'] = sum(float(c.amount_company_currency or 0) for c in contributions.filter(status='COMPLETED'))
            context['pending_amount'] = sum(float(c.amount_company_currency or 0) for c in contributions.filter(status='PENDING'))
            
            with open('/tmp/pending_debug.log', 'a') as f:
                f.write(f"Entity: {entity.name}, pending_amount = {context['pending_amount']}\n")
        return context


class CapitalContributionDetailView(LoginRequiredMixin, DetailView):
    """View capital contribution details."""
    model = CapitalContribution
    template_name = 'accounting/capital_contribution_detail.html'
    context_object_name = 'contribution'


class CapitalContributionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Record a new capital contribution."""
    model = CapitalContribution
    form_class = CapitalContributionForm
    template_name = 'accounting/capital_contribution_form.html'
    success_url = reverse_lazy('accounting:capital_contribution_list')
    permission_required = 'accounting.add_capitalcontribution'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        stakeholder_id = self.kwargs.get('stakeholder_id')
        if stakeholder_id:
            stakeholder = get_object_or_404(Stakeholder, pk=stakeholder_id)
            self.stakeholder = stakeholder
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'stakeholder'):
            context['stakeholder'] = self.stakeholder
        return context
    
    def form_valid(self, form):
        entity = Entity.objects.filter(is_active=True).first()
        if not entity:
            messages.error(self.request, 'No active entity configured.')
            return self.form_invalid(form)
        
        if hasattr(self, 'stakeholder'):
            form.instance.stakeholder = self.stakeholder
        
        form.instance.entity = entity
        response = super().form_valid(form)
        
        AuditLog.objects.create(
            entity=entity,
            user=self.request.user.username,
            action='CREATE',
            model_name='CapitalContribution',
            object_id=form.instance.id,
            description=f'Recorded capital contribution: {form.instance.amount} {form.instance.currency.code}'
        )
        messages.success(self.request, 'Capital contribution recorded successfully.')
        return response


class CapitalContributionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Update capital contribution."""
    model = CapitalContribution
    form_class = CapitalContributionForm
    template_name = 'accounting/capital_contribution_form.html'
    success_url = reverse_lazy('accounting:capital_contribution_list')
    permission_required = 'accounting.change_capitalcontribution'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        AuditLog.objects.create(
            entity=self.object.entity,
            user=self.request.user.username,
            action='UPDATE',
            model_name='CapitalContribution',
            object_id=self.object.id,
            description=f'Updated capital contribution: {self.object.amount}'
        )
        messages.success(self.request, 'Capital contribution updated successfully.')
        return response


# ============ SHAREHOLDING VIEWS ============

class ShareholdingListView(LoginRequiredMixin, ListView):
    """List all shareholdings."""
    model = Shareholding
    template_name = 'accounting/shareholding_list.html'
    context_object_name = 'shareholdings'
    paginate_by = 25
    
    def get_queryset(self):
        entity = Entity.objects.filter(is_active=True).first()
        if not entity:
            return Shareholding.objects.none()
        return Shareholding.objects.filter(entity=entity).select_related(
            'stakeholder', 'acquisition_currency'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = Entity.objects.filter(is_active=True).first()
        if entity:
            shareholdings = Shareholding.objects.filter(entity=entity, is_active=True)
            context['total_shares'] = shareholdings.aggregate(
                Sum('number_of_shares')
            )['number_of_shares__sum'] or 0
            context['total_value'] = shareholdings.aggregate(
                total=Sum('number_of_shares') * Sum('acquisition_price')
            ) or 0
        return context


class ShareholdingDetailView(LoginRequiredMixin, DetailView):
    """View shareholding details."""
    model = Shareholding
    template_name = 'accounting/shareholding_detail.html'
    context_object_name = 'shareholding'


class ShareholdingCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Record a new shareholding."""
    model = Shareholding
    form_class = ShareholdingForm
    template_name = 'accounting/shareholding_form.html'
    success_url = reverse_lazy('accounting:shareholding_list')
    permission_required = 'accounting.add_shareholding'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        stakeholder_id = self.kwargs.get('stakeholder_id')
        if stakeholder_id:
            stakeholder = get_object_or_404(Stakeholder, pk=stakeholder_id)
            self.stakeholder = stakeholder
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'stakeholder'):
            context['stakeholder'] = self.stakeholder
        return context
    
    def form_valid(self, form):
        entity = Entity.objects.filter(is_active=True).first()
        if not entity:
            messages.error(self.request, 'No active entity configured.')
            return self.form_invalid(form)
        
        if hasattr(self, 'stakeholder'):
            form.instance.stakeholder = self.stakeholder
        
        form.instance.entity = entity
        response = super().form_valid(form)
        
        AuditLog.objects.create(
            entity=entity,
            user=self.request.user.username,
            action='CREATE',
            model_name='Shareholding',
            object_id=form.instance.id,
            description=f'Recorded shareholding: {form.instance.number_of_shares} {form.instance.share_type} shares'
        )
        messages.success(self.request, 'Shareholding recorded successfully.')
        return response


class ShareholdingUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Update shareholding."""
    model = Shareholding
    form_class = ShareholdingForm
    template_name = 'accounting/shareholding_form.html'
    success_url = reverse_lazy('accounting:shareholding_list')
    permission_required = 'accounting.change_shareholding'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        AuditLog.objects.create(
            entity=self.object.entity,
            user=self.request.user.username,
            action='UPDATE',
            model_name='Shareholding',
            object_id=self.object.id,
            description=f'Updated shareholding: {self.object.number_of_shares} shares'
        )
        messages.success(self.request, 'Shareholding updated successfully.')
        return response
