"""
HR Module Views
Employee management, payroll processing, and GL integration.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse_lazy
from django.db.models import Q, Sum, Count, F
from django.utils import timezone
from django.http import JsonResponse
from decimal import Decimal
from datetime import datetime, timedelta

from .models import (
    Employee, Department, Position, Payroll, PayrollRecord,
    Benefit, EmployeeBenefit, Leave, LeaveBalance, LeaveRequest,
    Performance, Disciplinary, SalaryHistory, Attendance
)
from .forms import (
    EmployeeForm, PayrollForm, PayrollRecordForm, BenefitForm,
    LeaveRequestForm, PerformanceForm, DisciplinaryForm
)
from accounting.models import Entity, Account, LedgerEntry
from accounting.rbac_decorators import require_permission_class, require_permission


# Employee Management Views

@method_decorator(csrf_protect, name='dispatch')
class EmployeeListView(LoginRequiredMixin, ListView):
    """List all employees."""
    model = Employee
    template_name = 'hr/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 50
    
    def get_queryset(self):
        # Get entities accessible to this user through UserRole
        from accounting.role_models import UserRole
        user_entities = UserRole.objects.filter(
            user=self.request.user,
            is_active=True
        ).values_list('entity_id', flat=True).distinct()
        
        queryset = Employee.objects.filter(
            entity_id__in=user_entities
        ).select_related('department', 'position', 'manager')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by department
        department = self.request.GET.get('department')
        if department:
            queryset = queryset.filter(department_id=department)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset.order_by('last_name', 'first_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get entities accessible to this user
        from accounting.role_models import UserRole
        user_entities = UserRole.objects.filter(
            user=self.request.user,
            is_active=True
        ).values_list('entity_id', flat=True).distinct()
        
        context['departments'] = Department.objects.filter(entity_id__in=user_entities).order_by('name')
        
        return context


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    """View employee details with full history."""
    model = Employee
    template_name = 'hr/employee_detail.html'
    context_object_name = 'employee'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.get_object()
        
        # Get employee information
        context['salary_history'] = employee.salary_history.all()[:10]
        context['leave_balances'] = employee.leave_balances.all()
        context['leave_requests'] = employee.leave_requests.all()[:5]
        context['performance_reviews'] = employee.performance_reviews.all()[:3]
        context['disciplinary_actions'] = employee.disciplinary_actions.all()
        context['benefits'] = employee.enrolled_benefits.filter(is_active=True)
        context['recent_payroll'] = employee.payroll_records.all()[:5]
        
        return context


@method_decorator(csrf_protect, name='dispatch')
class EmployeeCreateView(LoginRequiredMixin, CreateView):
    """Create new employee."""
    model = Employee
    form_class = EmployeeForm
    template_name = 'hr/employee_form.html'
    success_url = reverse_lazy('hr:employee-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ensure CSRF token is available
        get_token(self.request)
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Get entities accessible to this user
        from accounting.role_models import UserRole
        user_entities = UserRole.objects.filter(
            user=self.request.user,
            is_active=True
        ).values_list('entity_id', flat=True).distinct()
        
        # If only one entity, set it as default
        if user_entities.count() == 1:
            entity_id = user_entities.first()
            if 'data' not in kwargs:
                kwargs['initial'] = kwargs.get('initial', {})
            kwargs['initial']['entity'] = entity_id
        
        return kwargs
    
    def form_valid(self, form):
        # Save employee
        employee = form.save(commit=False)
        employee.created_by = self.request.user
        employee.save()
        
        # Auto-create leave balances for all leave types
        current_year = timezone.now().year
        for leave_type in Leave.objects.filter(entity=employee.entity):
            LeaveBalance.objects.get_or_create(
                employee=employee,
                leave_type=leave_type,
                year=current_year,
                defaults={
                    'opening_balance': 0,
                    'allocated': leave_type.annual_allocation,
                }
            )
        
        # Redirect to success URL
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(self.get_success_url())
class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    """Update employee information."""
    model = Employee
    form_class = EmployeeForm
    template_name = 'hr/employee_form.html'
    success_url = reverse_lazy('hr:employee-list')


# Payroll Views

@method_decorator(csrf_protect, name='dispatch')
class PayrollListView(LoginRequiredMixin, ListView):
    """List payroll runs."""
    model = Payroll
    template_name = 'hr/payroll_list.html'
    context_object_name = 'payrolls'
    paginate_by = 20
    
    def get_queryset(self):
        # Get entities accessible to this user through UserRole
        from accounting.role_models import UserRole
        user_entities = UserRole.objects.filter(
            user=self.request.user,
            is_active=True
        ).values_list('entity_id', flat=True).distinct()
        
        return Payroll.objects.filter(
            entity_id__in=user_entities
        ).order_by('-payroll_date')


class PayrollDetailView(LoginRequiredMixin, DetailView):
    """View payroll details and records."""
    model = Payroll
    template_name = 'hr/payroll_detail.html'
    context_object_name = 'payroll'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payroll = self.get_object()
        context['payroll_records'] = payroll.payroll_records.all()
        context['total_gross'] = payroll.payroll_records.aggregate(Sum('gross_amount'))['gross_amount__sum'] or 0
        context['total_net'] = payroll.payroll_records.aggregate(Sum('net_amount'))['net_amount__sum'] or 0
        return context


@method_decorator(csrf_protect, name='dispatch')
class PayrollCreateView(LoginRequiredMixin, CreateView):
    """Create new payroll run."""
    model = Payroll
    form_class = PayrollForm
    template_name = 'hr/payroll_form.html'
    success_url = reverse_lazy('hr:payroll-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ensure CSRF token is available
        get_token(self.request)
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Get entities accessible to this user
        from accounting.role_models import UserRole
        user_entities = UserRole.objects.filter(
            user=self.request.user,
            is_active=True
        ).values_list('entity_id', flat=True).distinct()
        
        # If only one entity, set it as default
        if user_entities.count() == 1:
            entity_id = user_entities.first()
            if 'data' not in kwargs:
                kwargs['initial'] = kwargs.get('initial', {})
            kwargs['initial']['entity'] = entity_id
        
        return kwargs
    
    def form_valid(self, form):
        # Save payroll
        payroll = form.save(commit=False)
        payroll.save()
        
        # Auto-create payroll records for active employees
        employees = Employee.objects.filter(
            entity=payroll.entity,
            status__in=['ACTIVE', 'ON_LEAVE']
        )
        
        for employee in employees:
            PayrollRecord.objects.get_or_create(
                payroll=payroll,
                employee=employee,
                defaults={
                    'base_salary': employee.base_salary,
                    'gross_amount': employee.base_salary,
                    'net_amount': employee.base_salary,
                }
            )
        
        payroll.calculate_totals()
        
        # Redirect to success URL
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(self.get_success_url())


class PayrollApproveView(LoginRequiredMixin, UpdateView):
    """Approve payroll for processing."""
    model = Payroll
    fields = []
    template_name = 'hr/payroll_approve.html'
    
    def post(self, request, *args, **kwargs):
        payroll = self.get_object()
        payroll.status = 'APPROVED'
        payroll.approved_by = request.user
        payroll.approved_date = timezone.now()
        payroll.save()
        return redirect('hr:payroll-detail', pk=payroll.id)


@login_required
def payroll_post_to_gl(request, pk):
    """
    Post payroll to GL as journal entry.
    Creates debit/credit entries for salary expenses and liabilities.
    """
    payroll = get_object_or_404(Payroll, pk=pk)
    
    if payroll.is_posted:
        return JsonResponse({'error': 'Payroll already posted'}, status=400)
    
    if payroll.status != 'APPROVED':
        return JsonResponse({'error': 'Payroll must be approved first'}, status=400)
    
    try:
        # Get salary expense account from entity
        salary_account = Account.objects.filter(
            entity=payroll.entity,
            account_code__startswith='60'  # Salary expense
        ).first()
        
        # Get payable account
        payable_account = Account.objects.filter(
            entity=payroll.entity,
            account_code__startswith='21'  # Payables
        ).first()
        
        if not salary_account or not payable_account:
            return JsonResponse(
                {'error': 'Required GL accounts not configured'},
                status=400
            )
        
        # Create debit entry for salary expense
        LedgerEntry.objects.create(
            account=salary_account,
            entity=payroll.entity,
            entry_date=payroll.payroll_date,
            entry_type='DEBIT',
            amount=payroll.total_gross,
            description=f"Payroll: {payroll.payroll_number}",
            reference_number=payroll.payroll_number,
            is_posted=True,
            posted_by=request.user
        )
        
        # Create credit entry for salary payable
        LedgerEntry.objects.create(
            account=payable_account,
            entity=payroll.entity,
            entry_date=payroll.payroll_date,
            entry_type='CREDIT',
            amount=payroll.total_net,
            description=f"Payroll: {payroll.payroll_number}",
            reference_number=payroll.payroll_number,
            is_posted=True,
            posted_by=request.user
        )
        
        # Update payroll
        payroll.is_posted = True
        payroll.posted_date = timezone.now()
        payroll.save()
        
        return redirect('hr:payroll-detail', pk=payroll.id)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Leave Management Views

class LeaveRequestListView(LoginRequiredMixin, ListView):
    """List leave requests."""
    model = LeaveRequest
    template_name = 'hr/leave_request_list.html'
    context_object_name = 'leave_requests'
    paginate_by = 50
    
    def get_queryset(self):
        # Get entities accessible to this user through UserRole
        from accounting.role_models import UserRole
        user_entities = UserRole.objects.filter(
            user=self.request.user,
            is_active=True
        ).values_list('entity_id', flat=True).distinct()
        
        queryset = LeaveRequest.objects.filter(
            employee__entity_id__in=user_entities
        ).select_related('employee', 'leave_type')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-start_date')


class LeaveRequestCreateView(LoginRequiredMixin, CreateView):
    """Create new leave request."""
    model = LeaveRequest
    form_class = LeaveRequestForm
    template_name = 'hr/leave_request_form.html'
    success_url = reverse_lazy('hr:leave-request-list')
    
    def form_valid(self, form):
        leave_request = form.save(commit=False)
        
        # Validate leave balance
        leave_balance = LeaveBalance.objects.get(
            employee=leave_request.employee,
            leave_type=leave_request.leave_type,
            year=leave_request.start_date.year
        )
        
        if leave_request.duration > leave_balance.available:
            form.add_error(
                None,
                f"Insufficient leave balance. Available: {leave_balance.available} days"
            )
            return self.form_invalid(form)
        
        return super().form_valid(form)


@login_required
def approve_leave_request(request, pk):
    """Approve leave request."""
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    if request.method == 'POST':
        leave_request.status = 'APPROVED'
        leave_request.approved_by = request.user
        leave_request.approval_date = timezone.now()
        leave_request.save()
        
        return redirect('hr:leave-request-detail', pk=leave_request.id)
    
    return render(request, 'hr/leave_request_approve.html', {'leave_request': leave_request})


# Performance Management Views

class PerformanceListView(LoginRequiredMixin, ListView):
    """List performance reviews."""
    model = Performance
    template_name = 'hr/performance_list.html'
    context_object_name = 'reviews'
    paginate_by = 50
    
    def get_queryset(self):
        # Get entities accessible to this user through UserRole
        from accounting.role_models import UserRole
        user_entities = UserRole.objects.filter(
            user=self.request.user,
            is_active=True
        ).values_list('entity_id', flat=True).distinct()
        
        return Performance.objects.filter(
            employee__entity_id__in=user_entities
        ).order_by('-review_date')


@method_decorator(csrf_protect, name='dispatch')
class PerformanceCreateView(LoginRequiredMixin, CreateView):
    """Create new performance review."""
    model = Performance
    form_class = PerformanceForm
    template_name = 'hr/performance_form.html'
    success_url = reverse_lazy('hr:performance-list')


# Dashboard Views

@login_required
def hr_dashboard(request):
    """HR Dashboard with key metrics and statistics."""
    # Get accessible entities through UserRole
    from accounting.role_models import UserRole
    user_entities = UserRole.objects.filter(
        user=request.user,
        is_active=True
    ).values_list('entity_id', flat=True).distinct()
    
    context = {
        # Employee Statistics
        'total_employees': Employee.objects.filter(
            entity_id__in=user_entities,
            status='ACTIVE'
        ).count(),
        'employees_on_leave': Employee.objects.filter(
            entity_id__in=user_entities,
            status='ON_LEAVE'
        ).count(),
        'new_hires_this_month': Employee.objects.filter(
            entity_id__in=user_entities,
            hire_date__month=timezone.now().month,
            hire_date__year=timezone.now().year
        ).count(),
        
        # Payroll Statistics
        'pending_payrolls': Payroll.objects.filter(
            entity_id__in=user_entities,
            status='DRAFT'
        ).count(),
        'approved_payrolls': Payroll.objects.filter(
            entity_id__in=user_entities,
            status='APPROVED'
        ).count(),
        
        # Leave Statistics
        'pending_leave_requests': LeaveRequest.objects.filter(
            employee__entity_id__in=user_entities,
            status='SUBMITTED'
        ).count(),
        
        # Recent Activities
        'recent_employees': Employee.objects.filter(
            entity_id__in=user_entities
        ).order_by('-created_at')[:5],
        'recent_payrolls': Payroll.objects.filter(
            entity_id__in=user_entities
        ).order_by('-created_at')[:5],
    }
    
    return render(request, 'hr/dashboard.html', context)


@login_required
def employee_payroll_history(request, employee_id):
    """View employee payroll history."""
    employee = get_object_or_404(Employee, pk=employee_id)
    payroll_records = employee.payroll_records.all().order_by('-payroll__payroll_date')
    
    context = {
        'employee': employee,
        'payroll_records': payroll_records,
        'total_gross': payroll_records.aggregate(Sum('gross_amount'))['gross_amount__sum'] or 0,
        'total_net': payroll_records.aggregate(Sum('net_amount'))['net_amount__sum'] or 0,
    }
    
    return render(request, 'hr/employee_payroll_history.html', context)


@login_required
def department_report(request, department_id):
    """View department statistics and employees."""
    department = get_object_or_404(Department, pk=department_id)
    employees = department.employees.filter(status='ACTIVE')
    
    total_salary = employees.aggregate(Sum('base_salary'))['base_salary__sum'] or 0
    
    context = {
        'department': department,
        'employees': employees,
        'total_salary': total_salary,
        'employee_count': employees.count(),
    }
    
    return render(request, 'hr/department_report.html', context)
