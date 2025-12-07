"""
Employee Expense Module Views
Handles expense report submission, approval, and reimbursement
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.db.models import Q, Sum, F
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal
from datetime import datetime, timedelta
import logging
import traceback

from accounting.mixins import SessionEntityMixin
from accounting.models import AuditLog
from hr.models import Employee
from .models import (
    EmployeeExpenseReport, EmployeeExpense, ExpenseCategory,
    ExpenseBudget, ExpenseApprovalWorkflow, ExpenseReimbursement,
    ExpenseAttachment
)
from .forms import (
    EmployeeExpenseReportForm, EmployeeExpenseForm,
    ExpenseCategoryForm, ExpenseBudgetForm, ExpenseReimbursementForm,
    ExpenseAttachmentForm
)

logger = logging.getLogger(__name__)


class ExpenseDashboardView(SessionEntityMixin, LoginRequiredMixin, TemplateView):
    """Dashboard for expense module"""
    template_name = 'expenses/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = self.request.entity
        
        # Get current month
        today = timezone.now().date()
        month_start = today.replace(day=1)
        next_month = (month_start + timedelta(days=32)).replace(day=1)
        month_end = next_month - timedelta(days=1)
        
        # Statistics
        context['total_reports'] = EmployeeExpenseReport.objects.filter(
            entity=entity
        ).count()
        
        context['pending_reports'] = EmployeeExpenseReport.objects.filter(
            entity=entity,
            status__in=['SUBMITTED', 'PENDING_REVIEW', 'PENDING_APPROVAL']
        ).count()
        
        context['monthly_expenses'] = EmployeeExpense.objects.filter(
            report__entity=entity,
            expense_date__gte=month_start,
            expense_date__lte=month_end,
            status='APPROVED'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        context['recent_reports'] = EmployeeExpenseReport.objects.filter(
            entity=entity
        ).order_by('-created_at')[:5]
        
        return context


class EmployeeExpenseReportListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all expense reports"""
    model = EmployeeExpenseReport
    template_name = 'expenses/report_list.html'
    context_object_name = 'reports'
    paginate_by = 20
    
    def get_queryset(self):
        entity = self.request.entity
        queryset = EmployeeExpenseReport.objects.filter(entity=entity).order_by('-created_at')
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by employee
        employee_id = self.request.GET.get('employee', '')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # Search by employee name
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                employee__user__first_name__icontains=search |
                Q(employee__user__last_name__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = EmployeeExpenseReport.STATUS_CHOICES
        context['employees'] = Employee.objects.filter(
            entity=self.request.entity
        ).order_by('user__first_name')
        return context


class EmployeeExpenseReportDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """View expense report details"""
    model = EmployeeExpenseReport
    template_name = 'expenses/report_detail.html'
    context_object_name = 'report'
    
    def get_queryset(self):
        return EmployeeExpenseReport.objects.filter(entity=self.request.entity)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report = context['report']
        context['items'] = report.items.all()
        context['attachments'] = report.attachments.all()
        context['workflow'] = getattr(report, 'approval_workflow', None)
        context['total_amount'] = sum(item.amount for item in report.items.all())
        context['approved_amount'] = sum(
            item.amount for item in report.items.filter(status='APPROVED')
        )
        
        # Get reviewers - users with 'reviewer' or 'expenses_can_approve' permission
        from accounting.module_permissions import ModulePermission
        reviewer_ids = ModulePermission.objects.filter(
            module='reviewer',
            can_view=True
        ).values_list('user_id', flat=True)
        
        context['reviewers'] = User.objects.filter(
            id__in=reviewer_ids,
            is_active=True
        ).order_by('first_name', 'last_name')
        
        # Get approvers - users with 'approver' or expense approval permission
        approver_ids = ModulePermission.objects.filter(
            module='expenses',
            can_approve=True
        ).values_list('user_id', flat=True)
        
        context['approvers'] = User.objects.filter(
            id__in=approver_ids,
            is_active=True
        ).order_by('first_name', 'last_name')
        
        # Check if current user is an approver
        context['is_approver'] = ModulePermission.objects.filter(
            user=self.request.user,
            module='expenses',
            can_approve=True
        ).exists()
        
        # Check if current user is a reviewer
        context['is_reviewer'] = ModulePermission.objects.filter(
            user=self.request.user,
            module='reviewer',
            can_view=True
        ).exists()
        
        return context


class EmployeeExpenseReportCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create new expense report - employee auto-populated from logged-in user"""
    model = EmployeeExpenseReport
    form_class = EmployeeExpenseReportForm
    template_name = 'expenses/report_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        logger.info(f"EmployeeExpenseReportCreateView.form_valid called for user {self.request.user.username}")
        form.instance.entity = self.request.entity
        
        # Auto-populate employee from logged-in user
        try:
            employee = Employee.objects.get(user=self.request.user)
            form.instance.employee = employee
            logger.info(f"Employee found: {employee}")
        except Employee.DoesNotExist:
            error_msg = 'Your user account is not linked to an employee record. Please contact your administrator to create an employee profile.'
            logger.error(f"Employee not found for user {self.request.user.username}")
            messages.error(self.request, error_msg)
            return self.form_invalid(form)
        
        try:
            logger.info("Calling super().form_valid(form)")
            response = super().form_valid(form)
            logger.info(f"Form saved successfully, instance ID: {form.instance.id}")
            
            # Create approval workflow
            try:
                logger.info(f"Creating approval workflow for report {form.instance.id}")
                ExpenseApprovalWorkflow.objects.create(
                    report=form.instance
                )
                logger.info("Approval workflow created successfully")
            except Exception as e:
                logger.error(f"Error creating approval workflow: {str(e)}\n{traceback.format_exc()}")
                messages.error(self.request, f"Error creating approval workflow: {str(e)}")
                form.instance.delete()
                return self.form_invalid(form)
            
            # Create audit log
            try:
                logger.info(f"Creating audit log for report {form.instance.id}")
                AuditLog.objects.create(
                    entity=self.request.entity,
                    action='CREATE',
                    model_name='EmployeeExpenseReport',
                    object_id=str(form.instance.id),
                    user=self.request.user.username,
                    description=f"Created new expense report",
                    new_values={'status': 'DRAFT'}
                )
                logger.info("Audit log created successfully")
            except Exception as e:
                logger.warning(f"Error creating audit log: {str(e)}\n{traceback.format_exc()}")
                messages.warning(self.request, f"Report created but audit log failed: {str(e)}")
            
            messages.success(self.request, 'Expense report created successfully!')
            logger.info(f"Form submission completed successfully for user {self.request.user.username}")
            return response
        except Exception as e:
            logger.error(f"Error creating expense report: {str(e)}\n{traceback.format_exc()}")
            messages.error(self.request, f"Error creating expense report: {str(e)}")
            return self.form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('expenses:report_detail', kwargs={'pk': self.object.pk})


class EmployeeExpenseCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Add expense item to report"""
    model = EmployeeExpense
    form_class = EmployeeExpenseForm
    template_name = 'expenses/expense_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Filter categories by entity
        report_id = self.kwargs.get('report_id')
        report = get_object_or_404(EmployeeExpenseReport, id=report_id, entity=self.request.entity)
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report_id = self.kwargs.get('report_id')
        context['report'] = get_object_or_404(EmployeeExpenseReport, id=report_id, entity=self.request.entity)
        return context
    
    def form_valid(self, form):
        report_id = self.kwargs.get('report_id')
        form.instance.report_id = report_id
        response = super().form_valid(form)
        
        # Recalculate totals
        report = form.instance.report
        report.calculate_totals()
        
        messages.success(self.request, 'Expense item added successfully!')
        return response
    
    def get_success_url(self):
        return reverse_lazy('expenses:report_detail', kwargs={'pk': self.kwargs.get('report_id')})


class EmployeeExpenseSubmitView(SessionEntityMixin, LoginRequiredMixin, View):
    """Submit expense report for manager review"""
    
    def post(self, request, pk):
        report = get_object_or_404(
            EmployeeExpenseReport,
            pk=pk,
            entity=request.entity,
            status='DRAFT'
        )
        
        # Check if user is the employee who submitted the report or has permission
        if report.employee.user != request.user and not request.user.is_staff:
            messages.error(request, 'You do not have permission to submit this report.')
            return redirect('expenses:report_detail', pk=pk)
        
        # Check if report has items
        if not report.items.exists():
            messages.error(request, 'Cannot submit empty expense report!')
            return redirect('expenses:report_detail', pk=pk)
        
        # Check if all required receipts are attached
        for item in report.items.all():
            if item.category.requires_receipt and not item.receipt and not item.attachments.exists():
                messages.warning(
                    request,
                    f'Receipt required for {item.category.name} - {item.description}. Please attach a receipt.'
                )
                return redirect('expenses:report_detail', pk=pk)
        
        # Submit report
        report.status = 'PENDING_REVIEW'
        report.submitted_by = request.user
        report.submitted_at = timezone.now()
        report.save()
        
        # Update workflow
        workflow = report.approval_workflow
        workflow.status = 'PENDING_MANAGER_REVIEW'
        workflow.save()
        
        # Create audit log
        AuditLog.objects.create(
            entity=request.entity,
            action='SUBMIT',
            model_name='EmployeeExpenseReport',
            object_id=str(report.id),
            user=request.user.username,
            description=f"Submitted expense report for manager review",
            old_values={'status': 'DRAFT'},
            new_values={'status': 'PENDING_REVIEW'}
        )
        
        messages.success(request, 'Expense report submitted for manager review!')
        return redirect('expenses:report_detail', pk=pk)


class EmployeeExpenseApproveView(SessionEntityMixin, LoginRequiredMixin, View):
    """Manager reviews and approves expense report"""
    
    def get(self, request, pk):
        report = get_object_or_404(
            EmployeeExpenseReport,
            pk=pk,
            entity=request.entity,
            status='PENDING_REVIEW'
        )
        
        # Check if user is manager or finance staff
        if not request.user.is_staff and not request.user.groups.filter(name__in=['Manager', 'Finance']).exists():
            messages.error(request, 'You do not have permission to approve this report.')
            return redirect('expenses:report_detail', pk=pk)
        
        context = {
            'report': report,
            'items': report.items.all(),
            'attachments': report.attachments.all(),
            'workflow': report.approval_workflow,
            'total_amount': sum(item.amount for item in report.items.all()),
        }
        return render(request, 'expenses/report_approve.html', context)
    
    def post(self, request, pk):
        report = get_object_or_404(
            EmployeeExpenseReport,
            pk=pk,
            entity=request.entity,
            status='PENDING_REVIEW'
        )
        
        # Check if user is manager or finance staff
        if not request.user.is_staff and not request.user.groups.filter(name__in=['Manager', 'Finance']).exists():
            messages.error(request, 'You do not have permission to approve this report.')
            return redirect('expenses:report_detail', pk=pk)
        
        action = request.POST.get('action', 'reject')
        notes = request.POST.get('notes', '')
        
        if action == 'approve':
            # Manager approves - move to finance approval
            report.status = 'PENDING_APPROVAL'
            report.reviewed_by = request.user
            report.reviewed_at = timezone.now()
            report.review_notes = notes
            report.save()
            
            workflow = report.approval_workflow
            workflow.manager = request.user.employee if hasattr(request.user, 'employee') else None
            workflow.manager_approved = True
            workflow.manager_notes = notes
            workflow.manager_review_at = timezone.now()
            workflow.status = 'PENDING_FINANCE_APPROVAL'
            workflow.save()
            
            AuditLog.objects.create(
                entity=request.entity,
                action='MANAGER_APPROVED',
                model_name='EmployeeExpenseReport',
                object_id=str(report.id),
                user=request.user.username,
                description='Manager approved expense report',
                old_values={'status': 'PENDING_REVIEW'},
                new_values={'status': 'PENDING_APPROVAL', 'notes': notes}
            )
            
            messages.success(request, 'Report approved for finance review!')
        else:
            # Manager rejects
            report.status = 'REJECTED'
            report.rejection_reason = notes
            report.rejected_at = timezone.now()
            report.reviewed_by = request.user
            report.reviewed_at = timezone.now()
            report.save()
            
            workflow = report.approval_workflow
            workflow.status = 'REJECTED'
            workflow.save()
            
            AuditLog.objects.create(
                entity=request.entity,
                action='MANAGER_REJECTED',
                model_name='EmployeeExpenseReport',
                object_id=str(report.id),
                user=request.user.username,
                description='Manager rejected expense report',
                old_values={'status': 'PENDING_REVIEW'},
                new_values={'status': 'REJECTED', 'reason': notes}
            )
            
            messages.warning(request, 'Report rejected. Employee has been notified.')
        
        return redirect('expenses:report_detail', pk=pk)


class EmployeeExpenseFinanceApprovalView(SessionEntityMixin, LoginRequiredMixin, View):
    """Finance manager approves and finalizes expense report"""
    
    def get(self, request, pk):
        report = get_object_or_404(
            EmployeeExpenseReport,
            pk=pk,
            entity=request.entity,
            status='PENDING_APPROVAL'
        )
        
        # Check if user is finance staff
        if not request.user.is_staff and not request.user.groups.filter(name='Finance').exists():
            messages.error(request, 'You do not have permission to approve this report.')
            return redirect('expenses:report_detail', pk=pk)
        
        context = {
            'report': report,
            'items': report.items.all(),
            'attachments': report.attachments.all(),
            'workflow': report.approval_workflow,
            'total_amount': sum(item.amount for item in report.items.all()),
        }
        return render(request, 'expenses/report_finance_approve.html', context)
    
    def post(self, request, pk):
        report = get_object_or_404(
            EmployeeExpenseReport,
            pk=pk,
            entity=request.entity,
            status='PENDING_APPROVAL'
        )
        
        # Check if user is finance staff
        if not request.user.is_staff and not request.user.groups.filter(name='Finance').exists():
            messages.error(request, 'You do not have permission to approve this report.')
            return redirect('expenses:report_detail', pk=pk)
        
        action = request.POST.get('action', 'reject')
        notes = request.POST.get('notes', '')
        
        if action == 'approve':
            # Finance approves and posts to GL
            report.status = 'APPROVED'
            report.approved_by = request.user
            report.approved_at = timezone.now()
            report.approval_notes = notes
            report.save()
            
            workflow = report.approval_workflow
            workflow.finance_approver = request.user
            workflow.finance_approved = True
            workflow.finance_notes = notes
            workflow.finance_approved_at = timezone.now()
            workflow.status = 'APPROVED'
            workflow.save()
            
            # Create reimbursement record
            from .models import ExpenseReimbursement
            total_approved = sum(
                item.amount for item in report.items.filter(status='APPROVED')
            )
            
            if total_approved > 0:
                reimbursement = ExpenseReimbursement.objects.create(
                    report=report,
                    amount=total_approved
                )
            
            # Post to GL
            try:
                for item in report.items.filter(status='APPROVED'):
                    item.post_to_gl()
                report.is_posted = True
                report.posted_at = timezone.now()
                report.status = 'POSTED'
                report.save()
                
                AuditLog.objects.create(
                    entity=request.entity,
                    action='FINANCE_APPROVED',
                    model_name='EmployeeExpenseReport',
                    object_id=str(report.id),
                    user=request.user.username,
                    description='Finance approved and posted expense report to GL',
                    old_values={'status': 'PENDING_APPROVAL'},
                    new_values={'status': 'APPROVED', 'is_posted': True}
                )
                
                messages.success(request, 'Report approved, posted to GL, and scheduled for reimbursement!')
            except Exception as e:
                messages.error(request, f'Error posting to GL: {str(e)}')
                return redirect('expenses:report_detail', pk=pk)
        else:
            # Finance rejects
            report.status = 'REJECTED'
            report.rejection_reason = notes
            report.rejected_at = timezone.now()
            report.approved_by = request.user
            report.approved_at = timezone.now()
            report.save()
            
            workflow = report.approval_workflow
            workflow.status = 'REJECTED'
            workflow.finance_approver = request.user
            workflow.finance_approved_at = timezone.now()
            workflow.finance_notes = notes
            workflow.save()
            
            AuditLog.objects.create(
                entity=request.entity,
                action='FINANCE_REJECTED',
                model_name='EmployeeExpenseReport',
                object_id=str(report.id),
                user=request.user.username,
                description='Finance rejected expense report',
                old_values={'status': 'PENDING_APPROVAL'},
                new_values={'status': 'REJECTED', 'reason': notes}
            )
            
            messages.warning(request, 'Report rejected. Employee has been notified.')
        
        return redirect('expenses:report_detail', pk=pk)


class EmployeeExpenseRejectView(SessionEntityMixin, LoginRequiredMixin, View):
    """Reject expense report"""
    
    def post(self, request, pk):
        report = get_object_or_404(
            EmployeeExpenseReport,
            pk=pk,
            entity=request.entity,
            status__in=['PENDING_REVIEW', 'PENDING_APPROVAL']
        )
        
        reason = request.POST.get('reason', '')
        report.reject(request.user, reason)
        
        messages.success(request, 'Expense report rejected!')
        return redirect('expenses:report_detail', pk=pk)


class ExpenseBudgetListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List expense budgets"""
    model = ExpenseBudget
    template_name = 'expenses/budget_list.html'
    context_object_name = 'budgets'
    paginate_by = 20
    
    def get_queryset(self):
        return ExpenseBudget.objects.filter(
            entity=self.request.entity,
            is_active=True
        ).order_by('-period_end')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.filter(entity=self.request.entity)
        return context


class ExpenseBudgetDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """View budget details with variance analysis"""
    model = ExpenseBudget
    template_name = 'expenses/budget_detail.html'
    context_object_name = 'budget'
    
    def get_queryset(self):
        return ExpenseBudget.objects.filter(entity=self.request.entity)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        budget = context['budget']
        
        # Get expenses in this budget period
        expenses = EmployeeExpense.objects.filter(
            report__employee=budget.employee,
            category=budget.category,
            expense_date__gte=budget.period_start,
            expense_date__lte=budget.period_end,
            status='APPROVED'
        )
        
        context['expenses'] = expenses
        context['spent'] = sum(e.amount for e in expenses)
        context['remaining'] = budget.get_remaining_budget()
        context['variance_percent'] = budget.get_variance_percent()
        
        return context


class ExpenseReimbursementListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List pending and completed reimbursements"""
    model = ExpenseReimbursement
    template_name = 'expenses/reimbursement_list.html'
    context_object_name = 'reimbursements'
    paginate_by = 20
    
    def get_queryset(self):
        return ExpenseReimbursement.objects.filter(
            report__entity=self.request.entity
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = ExpenseReimbursement.STATUS_CHOICES
        return context


class ExpenseReimbursementCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create reimbursement for approved expense report"""
    model = ExpenseReimbursement
    form_class = ExpenseReimbursementForm
    template_name = 'expenses/reimbursement_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        report_id = self.kwargs.get('report_id')
        report = get_object_or_404(
            EmployeeExpenseReport,
            id=report_id,
            entity=self.request.entity,
            status='APPROVED'
        )
        initial['amount'] = report.total_approved
        return initial
    
    def form_valid(self, form):
        report_id = self.kwargs.get('report_id')
        form.instance.report_id = report_id
        response = super().form_valid(form)
        
        messages.success(self.request, 'Reimbursement created successfully!')
        return response
    
    def get_success_url(self):
        return reverse_lazy('expenses:reimbursement_detail', kwargs={'pk': self.object.pk})


class ExpenseReimbursementDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """View reimbursement details"""
    model = ExpenseReimbursement
    template_name = 'expenses/reimbursement_detail.html'
    context_object_name = 'reimbursement'
    
    def get_queryset(self):
        return ExpenseReimbursement.objects.filter(report__entity=self.request.entity)


class ExpenseReimbursementProcessView(SessionEntityMixin, LoginRequiredMixin, View):
    """Process reimbursement payment"""
    
    def post(self, request, pk):
        reimbursement = get_object_or_404(
            ExpenseReimbursement,
            pk=pk,
            report__entity=request.entity,
            status='SCHEDULED'
        )
        
        transaction_id = request.POST.get('transaction_id', '')
        reimbursement.complete_payment(transaction_id)
        
        messages.success(request, 'Reimbursement processed successfully!')
        return redirect('expenses:reimbursement_detail', pk=pk)


class ExpenseCategoryListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List expense categories"""
    model = ExpenseCategory
    template_name = 'expenses/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20
    
    def get_queryset(self):
        return ExpenseCategory.objects.filter(
            entity=self.request.entity,
            is_active=True
        ).order_by('name')


class ExpenseAttachmentUploadView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Upload attachment to expense report or item"""
    model = ExpenseAttachment
    form_class = ExpenseAttachmentForm
    template_name = 'expenses/attachment_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Determine if attaching to report or item
        report_id = self.kwargs.get('report_id')
        expense_id = self.kwargs.get('expense_id')
        
        if report_id:
            report = get_object_or_404(EmployeeExpenseReport, id=report_id, entity=self.request.entity)
            context['report'] = report
        elif expense_id:
            expense = get_object_or_404(EmployeeExpense, id=expense_id)
            context['expense'] = expense
            context['report'] = expense.report
        
        return context
    
    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        
        report_id = self.kwargs.get('report_id')
        expense_id = self.kwargs.get('expense_id')
        
        if report_id:
            form.instance.report_id = report_id
        elif expense_id:
            form.instance.expense_item_id = expense_id
        
        response = super().form_valid(form)
        messages.success(self.request, 'Attachment uploaded successfully!')
        return response
    
    def get_success_url(self):
        report_id = self.kwargs.get('report_id')
        expense_id = self.kwargs.get('expense_id')
        
        if expense_id:
            expense = EmployeeExpense.objects.get(id=expense_id)
            return reverse_lazy('expenses:report_detail', kwargs={'pk': expense.report_id})
        else:
            return reverse_lazy('expenses:report_detail', kwargs={'pk': report_id})


class ExpenseAttachmentDeleteView(SessionEntityMixin, LoginRequiredMixin, View):
    """Delete an attachment"""
    
    def post(self, request, pk):
        attachment = get_object_or_404(ExpenseAttachment, pk=pk)
        
        # Check permissions - can only delete own attachments or if staff
        if attachment.uploaded_by != request.user and not request.user.is_staff:
            messages.error(request, 'You do not have permission to delete this attachment.')
            return redirect('expenses:report_detail', pk=attachment.report_id)
        
        report_id = attachment.report_id
        file_path = attachment.file.path if attachment.file else None
        
        # Delete file from storage
        if file_path and attachment.file:
            try:
                import os
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file: {e}")
        
        attachment.delete()
        messages.success(request, 'Attachment deleted successfully!')
        
        return redirect('expenses:report_detail', pk=report_id)


class ExpenseCategoryCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create new expense category"""
    model = ExpenseCategory
    form_class = ExpenseCategoryForm
    template_name = 'expenses/category_form.html'
    
    def form_valid(self, form):
        form.instance.entity = self.request.entity
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('expenses:category_list')


class EmployeeExpenseInlineReviewView(SessionEntityMixin, LoginRequiredMixin, View):
    """Inline reviewer assignment from detail page with dropdown selection"""
    
    def post(self, request, pk):
        from accounting.module_permissions import ModulePermission
        
        report = get_object_or_404(
            EmployeeExpenseReport,
            pk=pk,
            entity=request.entity,
            status='PENDING_REVIEW'
        )
        
        action = request.POST.get('action', 'reject')
        reviewer_id = request.POST.get('reviewer_id')
        notes = request.POST.get('notes', '')
        
        # Get reviewer - must have reviewer permission
        try:
            reviewer = User.objects.get(id=reviewer_id, is_active=True)
            # Check if user has reviewer permission
            has_permission = ModulePermission.objects.filter(
                user=reviewer,
                module='reviewer',
                can_view=True
            ).exists()
            if not has_permission:
                messages.error(request, 'Selected user does not have reviewer permissions.')
                return redirect('expenses:report_detail', pk=pk)
        except User.DoesNotExist:
            messages.error(request, 'Invalid reviewer selected.')
            return redirect('expenses:report_detail', pk=pk)
        
        if action == 'approve':
            # Reviewer approves - move to finance approval
            report.status = 'PENDING_APPROVAL'
            report.reviewed_by = reviewer
            report.reviewed_at = timezone.now()
            report.review_notes = notes
            report.save()
            
            workflow = report.approval_workflow
            workflow.manager = None  # Clear manager field, use reviewed_by on report instead
            workflow.manager_approved = True
            workflow.manager_notes = notes
            workflow.manager_review_at = timezone.now()
            workflow.status = 'PENDING_FINANCE_APPROVAL'
            workflow.save()
            
            AuditLog.objects.create(
                entity=request.entity,
                action='MANAGER_APPROVED',
                model_name='EmployeeExpenseReport',
                object_id=str(report.id),
                user=request.user.username,
                description=f'Reviewer {reviewer.get_full_name()} approved expense report',
                old_values={'status': 'PENDING_REVIEW'},
                new_values={'status': 'PENDING_APPROVAL', 'reviewer': reviewer.username, 'notes': notes}
            )
            
            messages.success(request, f'Report reviewed and approved by {reviewer.get_full_name()}. Forwarding to finance.')
        else:
            # Reviewer rejects
            report.status = 'REJECTED'
            report.rejection_reason = notes
            report.rejected_at = timezone.now()
            report.reviewed_by = reviewer
            report.reviewed_at = timezone.now()
            report.save()
            
            workflow = report.approval_workflow
            workflow.manager = None
            workflow.status = 'REJECTED'
            workflow.save()
            
            AuditLog.objects.create(
                entity=request.entity,
                action='MANAGER_REJECTED',
                model_name='EmployeeExpenseReport',
                object_id=str(report.id),
                user=request.user.username,
                description=f'Reviewer {reviewer.get_full_name()} rejected expense report',
                old_values={'status': 'PENDING_REVIEW'},
                new_values={'status': 'REJECTED', 'reviewer': reviewer.username, 'reason': notes}
            )
            
            messages.warning(request, f'Report rejected by {reviewer.get_full_name()}. Employee has been notified.')
        
        return redirect('expenses:report_detail', pk=pk)


class EmployeeExpenseInlineFinanceApprovalView(SessionEntityMixin, LoginRequiredMixin, View):
    """Inline finance approval from detail page with dropdown selection"""
    
    def post(self, request, pk):
        from accounting.module_permissions import ModulePermission
        
        report = get_object_or_404(
            EmployeeExpenseReport,
            pk=pk,
            entity=request.entity,
            status='PENDING_APPROVAL'
        )
        
        action = request.POST.get('action', 'reject')
        finance_approver_id = request.POST.get('finance_approver_id')
        notes = request.POST.get('notes', '')
        
        # Get finance approver - must have expense approval permission
        try:
            finance_approver = User.objects.get(id=finance_approver_id, is_active=True)
            # Check if user has expense approval permission
            has_permission = ModulePermission.objects.filter(
                user=finance_approver,
                module='expenses',
                can_approve=True
            ).exists()
            if not has_permission:
                messages.error(request, 'Selected user does not have expense approval permissions.')
                return redirect('expenses:report_detail', pk=pk)
        except User.DoesNotExist:
            messages.error(request, 'Invalid finance approver selected.')
            return redirect('expenses:report_detail', pk=pk)
        
        if action == 'approve':
            # Finance approves and posts to GL
            report.status = 'APPROVED'
            report.approved_by = finance_approver
            report.approved_at = timezone.now()
            report.approval_notes = notes
            report.save()
            
            workflow = report.approval_workflow
            workflow.finance_approver = finance_approver
            workflow.finance_approved = True
            workflow.finance_notes = notes
            workflow.finance_approved_at = timezone.now()
            workflow.status = 'APPROVED'
            workflow.save()
            
            # Create reimbursement record
            total_approved = sum(
                item.amount for item in report.items.filter(status='APPROVED')
            )
            
            if total_approved > 0:
                ExpenseReimbursement.objects.create(
                    report=report,
                    amount=total_approved
                )
            
            # Post to GL
            try:
                for item in report.items.filter(status='APPROVED'):
                    item.post_to_gl()
                report.is_posted = True
                report.posted_at = timezone.now()
                report.status = 'POSTED'
                report.save()
                
                AuditLog.objects.create(
                    entity=request.entity,
                    action='FINANCE_APPROVED',
                    model_name='EmployeeExpenseReport',
                    object_id=str(report.id),
                    user=request.user.username,
                    description=f'Finance {finance_approver.get_full_name()} approved and posted expense report to GL',
                    old_values={'status': 'PENDING_APPROVAL'},
                    new_values={'status': 'APPROVED', 'is_posted': True, 'approver': finance_approver.username}
                )
                
                messages.success(request, f'Report approved by {finance_approver.get_full_name()}, posted to GL, and scheduled for reimbursement!')
            except Exception as e:
                logger.error(f"Error posting to GL: {str(e)}\n{traceback.format_exc()}")
                messages.error(request, f'Error posting to GL: {str(e)}')
                return redirect('expenses:report_detail', pk=pk)
        else:
            # Finance rejects
            report.status = 'REJECTED'
            report.rejection_reason = notes
            report.rejected_at = timezone.now()
            report.approved_by = finance_approver
            report.approved_at = timezone.now()
            report.save()
            
            workflow = report.approval_workflow
            workflow.finance_approver = finance_approver
            workflow.status = 'REJECTED'
            workflow.save()
            
            AuditLog.objects.create(
                entity=request.entity,
                action='FINANCE_REJECTED',
                model_name='EmployeeExpenseReport',
                object_id=str(report.id),
                user=request.user.username,
                description=f'Finance {finance_approver.get_full_name()} rejected expense report',
                old_values={'status': 'PENDING_APPROVAL'},
                new_values={'status': 'REJECTED', 'approver': finance_approver.username, 'reason': notes}
            )
            
            messages.warning(request, f'Report rejected by {finance_approver.get_full_name()}. Employee has been notified.')
        
        return redirect('expenses:report_detail', pk=pk)

