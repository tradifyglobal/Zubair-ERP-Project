"""
Employee Expense Module Views
Handles expense report submission, approval, and reimbursement
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q, Sum, F
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal
from datetime import datetime, timedelta

from accounting.mixins import SessionEntityMixin
from accounting.models import AuditLog
from hr.models import Employee
from .models import (
    EmployeeExpenseReport, EmployeeExpense, ExpenseCategory,
    ExpenseBudget, ExpenseApprovalWorkflow, ExpenseReimbursement
)

from .forms import (
    EmployeeExpenseReportForm, EmployeeExpenseForm,
    ExpenseCategoryForm, ExpenseBudgetForm, ExpenseReimbursementForm, ExpenseApprovalForm
)


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
        context['workflow'] = getattr(report, 'approval_workflow', None)
        context['total_amount'] = sum(item.amount for item in report.items.all())
        context['approved_amount'] = sum(
            item.amount for item in report.items.filter(status='APPROVED')
        )
        return context


class EmployeeExpenseReportCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create new expense report"""
    model = EmployeeExpenseReport
    form_class = EmployeeExpenseReportForm
    template_name = 'expenses/report_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass entity to form to filter employees
        kwargs['entity'] = self.request.entity
        return kwargs
    
    def form_valid(self, form):
        form.instance.entity = self.request.entity
        response = super().form_valid(form)
        
        # Create approval workflow
        ExpenseApprovalWorkflow.objects.create(
            report=form.instance
        )
        
        messages.success(self.request, 'Expense report created successfully!')
        return response
    
    def get_success_url(self):
        return reverse_lazy('expenses:report_detail', kwargs={'pk': self.object.pk})


class EmployeeExpenseCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Add expense item to report"""
    model = EmployeeExpense
    form_class = EmployeeExpenseForm
    template_name = 'expenses/expense_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass entity to form to filter categories
        kwargs['entity'] = self.request.entity
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
    """Submit expense report for review"""
    
    def post(self, request, pk):
        report = get_object_or_404(
            EmployeeExpenseReport,
            pk=pk,
            entity=request.entity,
            status='DRAFT'
        )
        
        # Check if report has items
        if not report.items.exists():
            messages.error(request, 'Cannot submit empty expense report!')
            return redirect('expenses:report_detail', pk=pk)
        
        # Submit report
        report.submit(request.user)
        
        # Update workflow
        workflow = report.approval_workflow
        workflow.submit_for_manager_review()
        
        AuditLog.objects.create(
            entity=request.entity,
            action='SUBMIT',
            model_name='EmployeeExpenseReport',
            object_id=str(report.id),
            user=request.user.username,
            description=f"Submitted expense report: {report}",
            old_values={'status': 'DRAFT'},
            new_values={'status': 'SUBMITTED'}
        )
        
        messages.success(request, 'Expense report submitted for review!')
        return redirect('expenses:report_detail', pk=pk)


class EmployeeExpenseApproveView(SessionEntityMixin, LoginRequiredMixin, View):
    """Approve expense report"""
    
    def post(self, request, pk):
        report = get_object_or_404(
            EmployeeExpenseReport,
            pk=pk,
            entity=request.entity,
            status__in=['SUBMITTED', 'PENDING_REVIEW', 'PENDING_APPROVAL']
        )
        
        notes = request.POST.get('notes', '')
        report.approve(request.user, notes)
        
        # Update workflow
        workflow = report.approval_workflow
        workflow.finance_approve(request.user, notes)
        
        # Post to GL (DEBIT Expense, CREDIT AP)
        if report.post_to_gl():
            messages.success(request, 'Expense report approved and posted to GL!')
        else:
            messages.warning(request, 'Expense report approved but GL posting failed. Please verify expense category accounts are configured.')
        
        return redirect('expenses:report_detail', pk=pk)


class EmployeeExpenseRejectView(SessionEntityMixin, LoginRequiredMixin, View):
    """Reject expense report"""
    
    def post(self, request, pk):
        report = get_object_or_404(
            EmployeeExpenseReport,
            pk=pk,
            entity=request.entity,
            status__in=['SUBMITTED', 'PENDING_REVIEW', 'PENDING_APPROVAL']
        )
        
        reason = request.POST.get('reason', '')
        report.reject(request.user, reason)
        
        messages.success(request, 'Expense report rejected!')
        return redirect('expenses:report_detail', pk=pk)


# --- Inline Review View ---
class EmployeeExpenseInlineReviewView(SessionEntityMixin, LoginRequiredMixin, View):
    """Handle inline manager review (approve/reject/assign reviewer) via POST."""
    def post(self, request, pk):
        report = get_object_or_404(
            EmployeeExpenseReport,
            pk=pk,
            entity=request.entity,
            status='PENDING_REVIEW'
        )
        action = request.POST.get('action')
        reviewer_id = request.POST.get('reviewer_id')
        notes = request.POST.get('notes', '')
        user = request.user

        # Assign reviewer if provided
        if reviewer_id and not report.reviewed_by_id:
            from django.contrib.auth import get_user_model
            UserModel = get_user_model()
            reviewer = UserModel.objects.filter(id=reviewer_id).first()
            if reviewer:
                report.reviewed_by = reviewer
                report.reviewed_at = timezone.now()
                report.save()

        # Approve or reject
        if action == 'approve':
            # Mark manager review as approved in workflow
            workflow = report.approval_workflow
            workflow.manager_approve(user, notes)
            report.status = 'PENDING_APPROVAL'
            report.review_notes = notes
            report.save()
            messages.success(request, 'Expense report reviewed and submitted for approval!')
        elif action == 'reject':
            report.reject(user, notes or 'Rejected by reviewer')
            messages.success(request, 'Expense report rejected!')
        else:
            messages.error(request, 'Invalid action.')
        return redirect('expenses:report_detail', pk=pk)


# --- Inline Finance Approval View ---
class EmployeeExpenseInlineFinanceApprovalView(SessionEntityMixin, LoginRequiredMixin, View):
    """Handle inline finance approval (approve/reject/assign approver) via POST."""
    def post(self, request, pk):
        report = get_object_or_404(
            EmployeeExpenseReport,
            pk=pk,
            entity=request.entity,
            status='PENDING_APPROVAL'
        )
        action = request.POST.get('action')
        finance_approver_id = request.POST.get('finance_approver_id')
        notes = request.POST.get('notes', '')
        user = request.user

        workflow = report.approval_workflow

        # Assign finance approver if provided
        if finance_approver_id and (not workflow.finance_approver or str(workflow.finance_approver.id) != finance_approver_id):
            from django.contrib.auth import get_user_model
            UserModel = get_user_model()
            approver = UserModel.objects.filter(id=finance_approver_id).first()
            if approver:
                workflow.finance_approver = approver
                workflow.save()
                messages.success(request, 'Finance approver assigned.')
                return redirect('expenses:report_detail', pk=pk)

        # Approve or reject
        if action == 'final_approve':
            workflow.finance_approve(user, notes)
            report.status = 'APPROVED'
            report.approval_notes = notes
            report.save()
            # Post to GL
            report.post_to_gl()
            messages.success(request, 'Expense report approved and posted to GL!')
        elif action == 'reject':
            report.reject(user, notes or 'Rejected by finance approver')
            messages.success(request, 'Expense report rejected!')
        elif action == 'submit_to_approver':
            # Just assign finance approver, handled above
            pass
        else:
            messages.error(request, 'Invalid action.')
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
        budget = self.object  # Use self.object instead of context['budget']
        
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
        
        return context


class ExpenseBudgetCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new expense budget"""
    model = ExpenseBudget
    form_class = ExpenseBudgetForm
    template_name = 'expenses/budget_form.html'
    success_url = '/expenses/budgets/'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['entity'] = self.request.entity
        return kwargs
    
    def form_valid(self, form):
        form.instance.entity = self.request.entity
        messages.success(self.request, 'Budget created successfully!')
        return super().form_valid(form)
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
        
        # Post to General Ledger (DEBIT AP, CREDIT Cash/Bank)
        if reimbursement.post_to_gl():
            messages.success(request, 'Reimbursement processed and posted to GL successfully!')
        else:
            messages.warning(request, 'Reimbursement processed but GL posting failed. Please check account configuration.')
        
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
