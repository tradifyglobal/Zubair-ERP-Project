from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Sum, Count, Q
from django.contrib import messages
from django.http import JsonResponse
from accounting.models import Stakeholder, CapitalContribution, Shareholding, Entity
from accounting.stakeholder_forms import StakeholderForm, CapitalContributionForm, ShareholdingForm
from accounting.mixins import SessionEntityMixin
from shareholder.import_export import (
    export_shareholders_csv, export_shareholders_excel,
    import_shareholders_csv, import_shareholders_excel,
    export_capital_contributions_csv, export_capital_contributions_excel,
    import_capital_contributions_csv, import_capital_contributions_excel
)
from shareholder.notifications import get_all_pending_for_user


# ==================== Shareholder Dashboard ====================

class ShareholderDashboardView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'shareholder/dashboard.html'
    permission_required = 'accounting.view_stakeholder'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity_id = self.request.session.get('selected_entity_id')
        
        if entity_id:
            # Filter by entity
            entity = Entity.objects.filter(id=entity_id).first()
            stakeholders = Stakeholder.objects.filter(entity_id=entity_id)
            # Only include APPROVED contributions in dashboard calculations
            contributions = CapitalContribution.objects.filter(
                entity_id=entity_id,
                workflow_status='APPROVED'
            )
            shareholdings = Shareholding.objects.filter(entity_id=entity_id)
        else:
            # If no entity selected, show all (shouldn't happen with SessionEntityMixin)
            entity = None
            stakeholders = Stakeholder.objects.all()
            # Only include APPROVED contributions in dashboard calculations
            contributions = CapitalContribution.objects.filter(workflow_status='APPROVED')
            shareholdings = Shareholding.objects.all()
        
        context['entity'] = entity
        
        # Dashboard statistics
        context['total_stakeholders'] = stakeholders.count()
        context['total_contributions'] = contributions.count()
        context['total_shareholdings'] = shareholdings.count()
        
        # Calculate totals - only from APPROVED contributions
        total_capital = sum(float(cc.amount_company_currency or 0) for cc in contributions)
        context['total_capital_invested'] = total_capital
        context['total_shares'] = shareholdings.aggregate(total=Sum('number_of_shares'))['total'] or 0
        
        # Top shareholders by contribution - only APPROVED contributions
        context['top_contributors'] = stakeholders.annotate(
            total_contributed=Sum('capital_contributions__amount_company_currency', 
                                filter=Q(capital_contributions__workflow_status='APPROVED'))
        ).filter(total_contributed__isnull=False).order_by('-total_contributed')[:5]
        
        # Share type distribution
        context['share_distribution'] = shareholdings.values('share_type').annotate(
            count=Count('id'),
            total_shares=Sum('number_of_shares')
        ).order_by('-total_shares')
        
        # Recent contributions - only APPROVED
        context['recent_contributions'] = contributions.select_related('stakeholder').order_by('-contribution_date')[:5]
        
        # Pending contributions - those in SUBMITTED or REVIEWED status (awaiting approval)
        if entity_id:
            pending_contributions = CapitalContribution.objects.filter(
                entity_id=entity_id,
                workflow_status__in=['SUBMITTED', 'REVIEWED']
            )
        else:
            pending_contributions = CapitalContribution.objects.filter(
                workflow_status__in=['SUBMITTED', 'REVIEWED']
            )
        context['pending_contributions'] = pending_contributions.count()
        
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
        entity = None
        if entity_id:
            entity = Entity.objects.filter(id=entity_id).first()
            # Filter for APPROVED contributions only (workflow_status = APPROVED)
            entity_contributions = CapitalContribution.objects.filter(
                entity_id=entity_id,
                workflow_status='APPROVED'
            )
            entity_shareholdings = Shareholding.objects.filter(entity_id=entity_id)
        else:
            entity_contributions = CapitalContribution.objects.none()
            entity_shareholdings = Shareholding.objects.none()
        
        total_capital = 0
        for cc in entity_contributions:
            total_capital += float(cc.amount_company_currency or 0)
        context['total_capital'] = total_capital
        context['entity'] = entity
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
        
        # Get entity for currency display
        entity = Entity.objects.filter(id=entity_id).first() if entity_id else None
        context['entity'] = entity
        
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
        
        # Calculate statistics - only count APPROVED contributions
        approved_contributions = contributions.filter(workflow_status='APPROVED')
        context['total_invested'] = sum(float(cc.amount_company_currency or 0) for cc in approved_contributions)
        context['total_contributions'] = contributions.count()
        context['pending_contributions'] = contributions.filter(status='PENDING').count()
        context['completed_contributions'] = contributions.filter(status='COMPLETED').count()
        context['approved_contributions'] = approved_contributions.count()
        
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


class ShareholderBulkDeleteView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    """Handle bulk deletion of shareholders"""
    permission_required = 'accounting.delete_stakeholder'
    
    def post(self, request, *args, **kwargs):
        stakeholder_ids = request.POST.getlist('stakeholder_ids')
        
        if not stakeholder_ids:
            messages.warning(request, 'Please select at least one shareholder to delete.')
            return redirect('shareholder:stakeholder-list')
        
        # Filter by session entity and the provided IDs
        entity_id = request.session.get('selected_entity_id')
        stakeholders = Stakeholder.objects.filter(
            id__in=stakeholder_ids,
            entity_id=entity_id
        )
        
        count = stakeholders.count()
        if count == 0:
            messages.error(request, 'No valid shareholders found to delete.')
            return redirect('shareholder:stakeholder-list')
        
        # Delete the stakeholders
        stakeholders.delete()
        
        messages.success(
            request,
            f'Successfully deleted {count} shareholder{"s" if count > 1 else ""}.'
        )
        return redirect('shareholder:stakeholder-list')


# ==================== Capital Contribution Views ====================

class CapitalContributionListView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = CapitalContribution
    template_name = 'shareholder/capital_contribution_list.html'
    context_object_name = 'contributions'
    paginate_by = 20
    permission_required = 'accounting.view_capitalcontribution'

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Check for filter parameter
        filter_type = self.request.GET.get('filter', None)
        
        if filter_type == 'pending_review':
            # Show only contributions assigned to current user for review
            from django.db.models import Q
            queryset = queryset.filter(
                Q(assigned_reviewer_1=self.request.user, workflow_status__in=['SUBMITTED', 'FIRST_REVIEW_COMPLETED']) |
                Q(assigned_reviewer_2=self.request.user, workflow_status__in=['SUBMITTED', 'FIRST_REVIEW_COMPLETED'])
            )
        elif filter_type == 'pending_approval':
            # Show only contributions assigned to current user for approval
            queryset = queryset.filter(
                assigned_approver=self.request.user,
                workflow_status='REVIEWED'
            )
        
        return queryset.order_by('-submitted_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Use filtered queryset from mixin instead of CapitalContribution.objects.all()
        queryset = self.get_queryset()
        context['total_contributions'] = queryset.count()
        context['pending_total'] = queryset.filter(status='PENDING').aggregate(total=Sum('amount'))['total'] or 0
        context['completed_total'] = queryset.filter(status='COMPLETED').aggregate(total=Sum('amount_company_currency'))['total'] or 0
        
        # Get entity for currency display
        entity_id = self.request.session.get('selected_entity_id')
        if entity_id:
            entity = Entity.objects.filter(id=entity_id).first()
            context['entity'] = entity
        
        # Add filter type to context for template display
        context['filter_type'] = self.request.GET.get('filter', None)
        
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Ensure entity_id is set on instance before form initialization
        entity_id = self.request.session.get('selected_entity_id')
        if entity_id:
            if not kwargs.get('instance'):
                kwargs['instance'] = CapitalContribution()
            # Set entity_id directly (before accessing the entity property)
            kwargs['instance'].entity_id = entity_id
        return kwargs

    def form_valid(self, form):
        entity_id = self.request.session.get('selected_entity_id')
        if entity_id:
            from django.utils import timezone
            # Set entity_id directly (not via the property accessor)
            form.instance.entity_id = entity_id
            # Set default contribution_date if not provided
            if not form.instance.contribution_date:
                form.instance.contribution_date = timezone.now().date()
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Ensure entity_id is set on instance for form field filtering
        entity_id = self.request.session.get('selected_entity_id')
        if entity_id and kwargs.get('instance'):
            kwargs['instance'].entity_id = entity_id
        return kwargs


# ==================== Capital Contribution Workflow Views ====================

class CapitalContributionSubmitView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Submit a draft capital contribution for review and assign reviewer."""
    model = CapitalContribution
    permission_required = 'accounting.change_capitalcontribution'
    form_class = None  # Will be set dynamically
    template_name = 'shareholder/capital_contribution_submit.html'
    
    def get_form_class(self):
        from accounting.stakeholder_forms import CapitalContributionSubmitForm
        return CapitalContributionSubmitForm
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter reviewers by entity
        from accounting.models import UserEntity
        entity_id = self.request.session.get('selected_entity_id')
        user_ids = UserEntity.objects.filter(
            entity_id=entity_id
        ).values_list('user_id', flat=True)
        
        from django.contrib.auth.models import User
        active_entity_users = User.objects.filter(
            id__in=user_ids,
            is_active=True
        ).order_by('first_name', 'last_name')
        
        form.fields['reviewer'].queryset = active_entity_users
        form.fields['reviewer_2'].queryset = active_entity_users
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.workflow_status != 'DRAFT':
            context['error'] = "Only draft contributions can be submitted."
        return context
    
    def form_valid(self, form):
        from django.utils import timezone
        contribution = form.instance
        
        if contribution.workflow_status != 'DRAFT':
            messages.error(self.request, "Only draft contributions can be submitted.")
            return redirect('shareholder:capital-contribution-detail', pk=contribution.pk)
        
        contribution.workflow_status = 'SUBMITTED'
        contribution.submitted_by = self.request.user
        contribution.submitted_at = timezone.now()
        
        # Get selected reviewers from form data
        reviewer_id = self.request.POST.get('reviewer')
        reviewer_id_2 = self.request.POST.get('reviewer_2')
        
        from django.contrib.auth.models import User
        if reviewer_id:
            try:
                contribution.assigned_reviewer_1 = User.objects.get(id=reviewer_id)
            except User.DoesNotExist:
                pass
        
        if reviewer_id_2:
            try:
                contribution.assigned_reviewer_2 = User.objects.get(id=reviewer_id_2)
            except User.DoesNotExist:
                pass
        
        contribution.save()
        reviewer1_name = contribution.assigned_reviewer_1.get_full_name() if contribution.assigned_reviewer_1 else "Unknown"
        reviewer2_name = contribution.assigned_reviewer_2.get_full_name() if contribution.assigned_reviewer_2 else "Unknown"
        messages.success(self.request, f"Contribution submitted for review to {reviewer1_name} and {reviewer2_name}.")
        return redirect('shareholder:capital-contribution-detail', pk=contribution.pk)


class CapitalContributionReviewView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Handle review by both first and second reviewers. After both complete, move to approval stage."""
    model = CapitalContribution
    permission_required = 'accounting.change_capitalcontribution'
    form_class = None  # Will be set dynamically
    template_name = 'shareholder/capital_contribution_review.html'
    
    def get_form_class(self):
        from accounting.stakeholder_forms import CapitalContributionReviewForm
        return CapitalContributionReviewForm
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter approvers by entity
        from accounting.models import UserEntity
        entity_id = self.request.session.get('selected_entity_id')
        user_ids = UserEntity.objects.filter(
            entity_id=entity_id
        ).values_list('user_id', flat=True)
        
        from django.contrib.auth.models import User
        form.fields['approver'].queryset = User.objects.filter(
            id__in=user_ids,
            is_active=True
        ).order_by('first_name', 'last_name')
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contribution = self.object
        
        # Determine which reviewer this is
        if contribution.workflow_status not in ['SUBMITTED', 'FIRST_REVIEW_COMPLETED']:
            context['error'] = "This contribution is not in a reviewable status."
        else:
            if contribution.workflow_status == 'SUBMITTED':
                context['reviewer_type'] = 'First Reviewer'
            elif contribution.workflow_status == 'FIRST_REVIEW_COMPLETED':
                context['reviewer_type'] = 'Second Reviewer'
        
        return context
    
    def form_valid(self, form):
        from django.utils import timezone
        contribution = form.instance
        
        if contribution.workflow_status == 'SUBMITTED':
            # First reviewer completing review
            if not contribution.reviewed_by:
                contribution.reviewed_by = self.request.user
                contribution.reviewed_at = timezone.now()
                contribution.workflow_status = 'FIRST_REVIEW_COMPLETED'
                contribution.save()
                messages.success(self.request, "First review completed. Waiting for second reviewer.")
                return redirect('shareholder:capital-contribution-detail', pk=contribution.pk)
        
        elif contribution.workflow_status == 'FIRST_REVIEW_COMPLETED':
            # Second reviewer completing review
            if not contribution.reviewed_by_2:
                contribution.reviewed_by_2 = self.request.user
                contribution.reviewed_at_2 = timezone.now()
                contribution.workflow_status = 'REVIEWED'
                
                # Get selected approver from form data
                approver_id = self.request.POST.get('approver')
                if approver_id:
                    from django.contrib.auth.models import User
                    try:
                        contribution.approved_by = User.objects.get(id=approver_id)
                    except User.DoesNotExist:
                        pass
                
                contribution.save()
                approver_name = contribution.approved_by.get_full_name() if contribution.approved_by else "Unknown"
                messages.success(self.request, f"Both reviews completed! Contribution assigned to {approver_name} for approval.")
                return redirect('shareholder:capital-contribution-detail', pk=contribution.pk)
        
        messages.error(self.request, "Unable to process review at this time.")
        return redirect('shareholder:capital-contribution-detail', pk=contribution.pk)


class CapitalContributionApproveView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Approve a reviewed capital contribution."""
    model = CapitalContribution
    permission_required = 'accounting.change_capitalcontribution'
    form_class = None  # Will be set dynamically
    template_name = 'shareholder/capital_contribution_approve.html'
    
    def get_form_class(self):
        from accounting.stakeholder_forms import CapitalContributionApprovalForm
        return CapitalContributionApprovalForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.workflow_status != 'REVIEWED':
            context['error'] = "This contribution is not in reviewed status."
        return context
    
    def form_valid(self, form):
        from django.utils import timezone
        contribution = form.instance
        
        if contribution.workflow_status != 'REVIEWED':
            messages.error(self.request, "This contribution is not in reviewed status.")
            return redirect('shareholder:capital-contribution-detail', pk=contribution.pk)
        
        contribution.workflow_status = 'APPROVED'
        contribution.approved_by = self.request.user
        contribution.approved_at = timezone.now()
        
        # Mark status as COMPLETED when approved (so ledger entries are created)
        if contribution.status == 'PENDING':
            contribution.status = 'COMPLETED'
        
        # Save first - this will trigger ledger entry creation in save() method
        contribution.save()
        
        messages.success(self.request, "Contribution approved and ledger entry created.")
        return redirect('shareholder:capital-contribution-detail', pk=contribution.pk)


class CapitalContributionRejectView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Reject a capital contribution during review or approval."""
    model = CapitalContribution
    permission_required = 'accounting.change_capitalcontribution'
    fields = ['rejection_reason']
    template_name = 'shareholder/capital_contribution_reject.html'
    
    def form_valid(self, form):
        contribution = form.instance
        contribution.workflow_status = 'REJECTED'
        contribution.save()
        
        messages.success(self.request, "Contribution has been rejected.")
        return redirect('shareholder:capital-contribution-detail', pk=contribution.pk)



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
        if entity_id:
            # Set entity_id on instance before form initialization
            if not kwargs.get('instance'):
                kwargs['instance'] = ShareholderInvestmentLimit()
            kwargs['instance'].entity_id = entity_id
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity_id = self.request.session.get('selected_entity_id')
        if entity_id:
            # Set entity_id on instance before form initialization
            if not kwargs.get('instance'):
                kwargs['instance'] = ShareholderPaymentCommitment()
            kwargs['instance'].entity_id = entity_id
        return kwargs

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


# ==================== Import/Export Views ====================

class ShareholderExportView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'accounting.view_stakeholder'
    
    def get(self, request):
        entity_id = request.session.get('selected_entity_id')
        stakeholders = Stakeholder.objects.filter(entity_id=entity_id).order_by('id')
        
        format_type = request.GET.get('format', 'csv')
        
        if format_type == 'excel':
            return export_shareholders_excel(stakeholders)
        else:
            return export_shareholders_csv(stakeholders)


class ShareholderImportView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'accounting.add_stakeholder'
    
    def post(self, request):
        entity_id = request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id).first()
        
        if not entity:
            messages.error(request, 'Entity not found')
            return redirect('shareholder:stakeholder-list')
        
        file = request.FILES.get('file')
        if not file:
            messages.error(request, 'No file provided')
            return redirect('shareholder:stakeholder-list')
        
        overwrite = request.POST.get('overwrite') == 'true'
        imported_count = 0
        errors = []
        
        try:
            if file.name.endswith('.csv'):
                imported_count, errors = import_shareholders_csv(file, entity, overwrite)
            elif file.name.endswith(('.xlsx', '.xls')):
                imported_count, errors = import_shareholders_excel(file, entity, overwrite)
            else:
                messages.error(request, 'Unsupported file format. Please use CSV or Excel (.xlsx, .xls)')
                return redirect('shareholder:stakeholder-list')
            
            if imported_count > 0:
                messages.success(request, f'Successfully imported {imported_count} shareholder(s)')
            
            if errors:
                for error in errors[:10]:  # Show first 10 errors
                    messages.warning(request, error)
                if len(errors) > 10:
                    messages.warning(request, f'... and {len(errors) - 10} more errors')
        
        except Exception as e:
            messages.error(request, f'Error importing file: {str(e)}')
        
        return redirect('shareholder:stakeholder-list')


# ==================== Capital Contribution Export/Import ====================

class CapitalContributionExportView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'accounting.view_capitalcontribution'
    
    def get(self, request):
        entity_id = request.session.get('selected_entity_id')
        contributions = CapitalContribution.objects.filter(entity_id=entity_id).select_related('stakeholder', 'currency').order_by('-contribution_date')
        
        format_type = request.GET.get('format', 'csv')
        
        if format_type == 'excel':
            return export_capital_contributions_excel(contributions)
        else:
            return export_capital_contributions_csv(contributions)


class CapitalContributionImportView(SessionEntityMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'accounting.add_capitalcontribution'
    
    def post(self, request):
        entity_id = request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id).first()
        
        if not entity:
            messages.error(request, 'Entity not found')
            return redirect('shareholder:capital-contribution-list')
        
        file = request.FILES.get('file')
        if not file:
            messages.error(request, 'No file provided')
            return redirect('shareholder:capital-contribution-list')
        
        overwrite = request.POST.get('overwrite') == 'true'
        imported_count = 0
        errors = []
        
        try:
            if file.name.endswith('.csv'):
                imported_count, errors = import_capital_contributions_csv(file, entity, overwrite)
            elif file.name.endswith(('.xlsx', '.xls')):
                imported_count, errors = import_capital_contributions_excel(file, entity, overwrite)
            else:
                messages.error(request, 'Unsupported file format. Please use CSV or Excel (.xlsx, .xls)')
                return redirect('shareholder:capital-contribution-list')
            
            if imported_count > 0:
                messages.success(request, f'Successfully imported {imported_count} capital contribution(s)')
            
            if errors:
                for error in errors[:10]:  # Show first 10 errors
                    messages.warning(request, error)
                if len(errors) > 10:
                    messages.warning(request, f'... and {len(errors) - 10} more errors')
        
        except Exception as e:
            messages.error(request, f'Error importing file: {str(e)}')
        
        return redirect('shareholder:capital-contribution-list')


# ==================== API Endpoints ====================

class NotificationAPIView(LoginRequiredMixin, View):
    """
    API endpoint for fetching pending notifications
    """
    def get(self, request):
        """
        Get pending reviews and approvals for the current user
        Returns JSON with pending counts and details
        """
        entity = None
        if 'selected_entity_id' in request.session:
            try:
                entity = Entity.objects.get(id=request.session['selected_entity_id'])
            except Entity.DoesNotExist:
                pass
        
        pending = get_all_pending_for_user(request.user, entity)
        
        # Get details of pending items
        reviews = pending['pending_reviews'][:5]  # Get first 5
        approvals = pending['pending_approvals'][:5]  # Get first 5
        
        review_items = []
        for cc in reviews:
            review_items.append({
                'id': cc.id,
                'stakeholder': cc.stakeholder.full_name,
                'amount': str(cc.amount),
                'status': cc.workflow_status,
                'type': 'review',
                'url': f'/shareholder/capital-contributions/{cc.id}/review/'
            })
        
        approval_items = []
        for cc in approvals:
            approval_items.append({
                'id': cc.id,
                'stakeholder': cc.stakeholder.full_name,
                'amount': str(cc.amount),
                'status': cc.workflow_status,
                'type': 'approval',
                'url': f'/shareholder/capital-contributions/{cc.id}/approve/'
            })
        
        return JsonResponse({
            'success': True,
            'pending_reviews_count': pending['pending_reviews_count'],
            'pending_approvals_count': pending['pending_approvals_count'],
            'total_pending': pending['total_pending'],
            'review_items': review_items,
            'approval_items': approval_items,
        })
