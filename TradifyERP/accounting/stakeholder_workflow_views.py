"""
Workflow views for Capital Contribution approval process using Django Groups.

Workflow:
1. DRAFT → Submit (by creator) → SUBMITTED
2. SUBMITTED → First Review (by any member of 'Capital Contribution Reviewers' group) → FIRST_REVIEW_COMPLETED
3. FIRST_REVIEW_COMPLETED → Second Review (by different member of 'Capital Contribution Reviewers' group) → REVIEWED
4. REVIEWED → Approve/Reject (by any member of 'Capital Contribution Approvers' group) → APPROVED/REJECTED
"""

from django.views.generic import UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.contrib.auth.models import Group

from accounting.models import CapitalContribution, Entity, AuditLog
from accounting.stakeholder_forms import (
    CapitalContributionSubmitForm,
    CapitalContributionReviewForm,
    CapitalContributionApprovalForm
)


class CapitalContributionSubmitView(LoginRequiredMixin, UpdateView):
    """Submit a capital contribution for review.
    
    Any user who created the contribution can submit it.
    No need to assign specific reviewers - any member of
    'Capital Contribution Reviewers' group can review.
    """
    model = CapitalContribution
    form_class = CapitalContributionSubmitForm
    template_name = 'accounting/capital_contribution_submit.html'
    
    def get_success_url(self):
        return reverse('accounting:capital_contribution_detail', kwargs={'pk': self.object.pk})
    
    def test_func(self):
        """Only allow submission if contribution is in DRAFT status."""
        contribution = self.get_object()
        return contribution.workflow_status == 'DRAFT'
    
    def form_valid(self, form):
        contribution = form.save(commit=False)
        contribution.workflow_status = 'SUBMITTED'
        contribution.submitted_by = self.request.user
        contribution.submitted_at = timezone.now()
        contribution.save()
        
        # Create audit log
        AuditLog.objects.create(
            entity=contribution.entity,
            user=self.request.user.username,
            action='SUBMIT',
            model_name='CapitalContribution',
            object_id=contribution.id,
            description=f'Submitted capital contribution for review: {contribution.amount} {contribution.currency.code}'
        )
        
        messages.success(
            self.request,
            f'Capital contribution submitted for review. Any member of the "Capital Contribution Reviewers" group can now review it.'
        )
        return super().form_valid(form)


class GroupRequiredMixin(UserPassesTestMixin):
    """Mixin to check if user belongs to a specific group."""
    required_group = None
    
    def test_func(self):
        if not self.required_group:
            return False
        return self.request.user.groups.filter(name=self.required_group).exists()
    
    def handle_no_permission(self):
        messages.error(
            self.request,
            f'You must be a member of the "{self.required_group}" group to perform this action.'
        )
        return redirect('accounting:capital_contribution_list')


class CapitalContributionFirstReviewView(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    """First review of a capital contribution.
    
    Any member of 'Capital Contribution Reviewers' group can perform first review.
    """
    model = CapitalContribution
    form_class = CapitalContributionReviewForm
    template_name = 'accounting/capital_contribution_review.html'
    required_group = 'Capital Contribution Reviewers'
    
    def get_success_url(self):
        return reverse('accounting:capital_contribution_detail', kwargs={'pk': self.object.pk})
    
    def test_func(self):
        """Check group membership AND workflow status."""
        if not super().test_func():
            return False
        contribution = self.get_object()
        return contribution.workflow_status == 'SUBMITTED'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review_number'] = 1
        context['is_first_review'] = True
        return context
    
    def form_valid(self, form):
        contribution = form.save(commit=False)
        contribution.workflow_status = 'FIRST_REVIEW_COMPLETED'
        contribution.reviewed_by = self.request.user
        contribution.reviewed_at = timezone.now()
        
        # Save review notes to the first review notes field
        review_notes = form.cleaned_data.get('review_notes', '')
        if review_notes:
            contribution.review_notes = review_notes
        
        contribution.save()
        
        # Create audit log
        AuditLog.objects.create(
            entity=contribution.entity,
            user=self.request.user.username,
            action='FIRST_REVIEW',
            model_name='CapitalContribution',
            object_id=contribution.id,
            description=f'Completed first review of capital contribution: {contribution.amount} {contribution.currency.code}'
        )
        
        messages.success(
            self.request,
            'First review completed successfully. Awaiting second review.'
        )
        return super().form_valid(form)


class CapitalContributionSecondReviewView(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    """Second review of a capital contribution.
    
    Any member of 'Capital Contribution Reviewers' group can perform second review,
    but it must be a different user than the first reviewer.
    """
    model = CapitalContribution
    form_class = CapitalContributionReviewForm
    template_name = 'accounting/capital_contribution_review.html'
    required_group = 'Capital Contribution Reviewers'
    
    def get_success_url(self):
        return reverse('accounting:capital_contribution_detail', kwargs={'pk': self.object.pk})
    
    def get_form_kwargs(self):
        """Pass is_second_review=True to the form."""
        kwargs = super().get_form_kwargs()
        kwargs['is_second_review'] = True
        return kwargs
    
    def test_func(self):
        """Check group membership, workflow status, AND different reviewer."""
        if not super().test_func():
            return False
        contribution = self.get_object()
        
        # Must be in FIRST_REVIEW_COMPLETED status
        if contribution.workflow_status != 'FIRST_REVIEW_COMPLETED':
            return False
        
        # Second reviewer must be different from first reviewer
        if contribution.reviewed_by and contribution.reviewed_by == self.request.user:
            messages.error(
                self.request,
                'You cannot perform the second review as you already completed the first review.'
            )
            return False
        
        return True
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review_number'] = 2
        context['is_first_review'] = False
        context['first_reviewer'] = self.object.reviewed_by
        return context
    
    def form_valid(self, form):
        contribution = form.save(commit=False)
        contribution.workflow_status = 'REVIEWED'
        contribution.reviewed_by_2 = self.request.user
        contribution.reviewed_at_2 = timezone.now()
        
        # Save review notes to the second review notes field
        review_notes = form.cleaned_data.get('review_notes', '')
        if review_notes:
            contribution.review_notes_2 = review_notes
        
        contribution.save()
        
        # Create audit log
        AuditLog.objects.create(
            entity=contribution.entity,
            user=self.request.user.username,
            action='SECOND_REVIEW',
            model_name='CapitalContribution',
            object_id=contribution.id,
            description=f'Completed second review of capital contribution: {contribution.amount} {contribution.currency.code}'
        )
        
        messages.success(
            self.request,
            'Second review completed successfully. Capital contribution is now ready for approval.'
        )
        return super().form_valid(form)


class CapitalContributionApproveView(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    """Approve or reject a capital contribution.
    
    Any member of 'Capital Contribution Approvers' group can approve.
    """
    model = CapitalContribution
    form_class = CapitalContributionApprovalForm
    template_name = 'accounting/capital_contribution_approve.html'
    required_group = 'Capital Contribution Approvers'
    
    def get_success_url(self):
        return reverse('accounting:capital_contribution_detail', kwargs={'pk': self.object.pk})
    
    def test_func(self):
        """Check group membership AND workflow status."""
        if not super().test_func():
            return False
        contribution = self.get_object()
        return contribution.workflow_status == 'REVIEWED'
    
    def form_valid(self, form):
        contribution = form.save(commit=False)
        contribution.workflow_status = 'APPROVED'
        contribution.approved_by = self.request.user
        contribution.approved_at = timezone.now()
        
        # Update the contribution status to COMPLETED when approved
        contribution.status = 'COMPLETED'
        
        contribution.save()
        
        # Create audit log
        AuditLog.objects.create(
            entity=contribution.entity,
            user=self.request.user.username,
            action='APPROVE',
            model_name='CapitalContribution',
            object_id=contribution.id,
            description=f'Approved capital contribution: {contribution.amount} {contribution.currency.code}'
        )
        
        messages.success(
            self.request,
            'Capital contribution approved successfully!'
        )
        return super().form_valid(form)


class CapitalContributionRejectView(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    """Reject a capital contribution at any stage.
    
    Both reviewers and approvers can reject.
    """
    model = CapitalContribution
    template_name = 'accounting/capital_contribution_reject.html'
    fields = ['rejection_reason']
    required_group = None  # We'll check both groups
    
    def get_success_url(self):
        return reverse('accounting:capital_contribution_detail', kwargs={'pk': self.object.pk})
    
    def test_func(self):
        """Check if user is in either reviewers or approvers group."""
        user = self.request.user
        is_reviewer = user.groups.filter(name='Capital Contribution Reviewers').exists()
        is_approver = user.groups.filter(name='Capital Contribution Approvers').exists()
        
        if not (is_reviewer or is_approver):
            messages.error(
                self.request,
                'You must be a member of either "Capital Contribution Reviewers" or "Capital Contribution Approvers" group to reject.'
            )
            return False
        
        contribution = self.get_object()
        # Can reject if submitted, under review, or awaiting approval
        return contribution.workflow_status in ['SUBMITTED', 'FIRST_REVIEW_COMPLETED', 'REVIEWED']
    
    def form_valid(self, form):
        contribution = form.save(commit=False)
        contribution.workflow_status = 'REJECTED'
        contribution.status = 'CANCELLED'
        contribution.save()
        
        # Create audit log
        AuditLog.objects.create(
            entity=contribution.entity,
            user=self.request.user.username,
            action='REJECT',
            model_name='CapitalContribution',
            object_id=contribution.id,
            description=f'Rejected capital contribution: {contribution.amount} {contribution.currency.code}'
        )
        
        messages.warning(
            self.request,
            'Capital contribution has been rejected.'
        )
        return super().form_valid(form)
