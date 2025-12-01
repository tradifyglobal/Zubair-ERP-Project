"""
HR Module Views
Employee management, payroll processing, and GL integration.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Sum, Count, F
from django.utils import timezone
from django.http import JsonResponse, Http404
from decimal import Decimal
from datetime import datetime, timedelta

from .models import (
    Employee, Department, Position, Payroll, PayrollRecord,
    Benefit, EmployeeBenefit, Leave, LeaveBalance, LeaveRequest,
    Performance, Disciplinary, SalaryHistory, Attendance
)
from .forms import (
    EmployeeForm, PayrollForm, PayrollRecordForm, BenefitForm,
    LeaveRequestForm, PerformanceForm, DisciplinaryForm, PositionForm, DepartmentForm,
    SalaryHistoryForm, EmployeeBenefitForm, LeaveForm, LeaveBalanceForm
)
from accounting.models import Entity, Account, LedgerEntry
from accounting.rbac_decorators import require_permission_class, require_permission
from accounting.mixins import SessionEntityMixin


# Employee Management Views

@method_decorator(csrf_protect, name='dispatch')
class EmployeeListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all employees."""
    model = Employee
    template_name = 'hr/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 50
    
    def get_queryset(self):
        # Filter by selected entity in session
        entity_id = self.request.session.get('selected_entity_id')
        queryset = Employee.objects.filter(
            entity_id=entity_id
        ).select_related('department', 'position', 'manager') if entity_id else Employee.objects.none()
        
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
        # Get departments for selected entity
        entity_id = self.request.session.get('selected_entity_id')
        context['departments'] = Department.objects.filter(entity_id=entity_id).order_by('name') if entity_id else Department.objects.none()
        
        return context


class EmployeeDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """View employee details with full history."""
    model = Employee
    template_name = 'hr/employee_detail.html'
    context_object_name = 'employee'
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        return Employee.objects.filter(entity_id=entity_id) if entity_id else Employee.objects.none()
    
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
class EmployeeCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
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
        # Pass request to form for entity pre-population
        kwargs['request'] = self.request
        return kwargs
    
    def form_valid(self, form):
        """Handle form submission and create leave balances."""
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
        
        # Set object for success URL
        self.object = employee
        
        # Redirect to success URL
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(self.get_success_url())
@method_decorator(csrf_protect, name='dispatch')
class EmployeeUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update employee information."""
    model = Employee
    form_class = EmployeeForm
    template_name = 'hr/employee_form.html'
    success_url = reverse_lazy('hr:employee-list')
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        return Employee.objects.filter(entity_id=entity_id) if entity_id else Employee.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ensure CSRF token is available
        get_token(self.request)
        context['is_edit'] = True
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass request to form
        kwargs['request'] = self.request
        return kwargs
    
    def form_valid(self, form):
        """Handle form submission and save employee."""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f'Saving employee: {form.cleaned_data.get("first_name")} {form.cleaned_data.get("last_name")}')
            
            # Save employee
            employee = form.save(commit=False)
            employee.updated_at = timezone.now()
            employee.save()
            
            # Set object for success URL
            self.object = employee
            
            # Add success message
            messages.success(self.request, f'Employee {employee.full_name} updated successfully!')
            logger.info(f'Employee {employee.id} saved successfully')
            
            # Redirect to success URL
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())
            
        except Exception as e:
            logger.exception(f'Error updating employee: {str(e)}')
            messages.error(self.request, f'Error saving employee: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Handle invalid form submission."""
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Form validation errors: {form.errors}')
        for field, errors in form.errors.items():
            for error in errors:
                logger.error(f'  {field}: {error}')
        return super().form_invalid(form)


# Payroll Views

@method_decorator(csrf_protect, name='dispatch')
class PayrollListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List payroll runs."""
    model = Payroll
    template_name = 'hr/payroll_list.html'
    context_object_name = 'payrolls'
    paginate_by = 20
    
    def get_queryset(self):
        # Get selected entity from session
        entity_id = self.request.session.get('selected_entity_id')
        queryset = Payroll.objects.filter(entity_id=entity_id).order_by('-payroll_date') if entity_id else Payroll.objects.none()
        
        # Add search functionality
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(payroll_number__icontains=search) |
                Q(period_start__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add summary statistics
        queryset = self.get_queryset()
        context['draft_count'] = queryset.filter(status='DRAFT').count()
        context['approved_count'] = queryset.filter(status='APPROVED').count()
        context['posted_count'] = queryset.filter(is_posted=True).count()
        context['pending_count'] = queryset.filter(status__in=['PENDING', 'PROCESSING']).count()
        context['search'] = self.request.GET.get('search', '')
        return context


class PayrollDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """View payroll details and records."""
    model = Payroll
    template_name = 'hr/payroll_detail.html'
    context_object_name = 'payroll'
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        return Payroll.objects.filter(entity_id=entity_id) if entity_id else Payroll.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payroll = self.get_object()
        payroll_records = payroll.payroll_records.all()
        context['payroll_records'] = payroll_records
        context['total_gross'] = payroll.payroll_records.aggregate(Sum('gross_amount'))['gross_amount__sum'] or 0
        context['total_net'] = payroll.payroll_records.aggregate(Sum('net_amount'))['net_amount__sum'] or 0
        
        # Calculate average salary
        count = payroll_records.count()
        if count > 0:
            context['average_salary'] = context['total_gross'] / count
        else:
            context['average_salary'] = 0
        
        return context


@method_decorator(csrf_protect, name='dispatch')
class PayrollCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
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
    
    def post(self, request, *args, **kwargs):
        print("[PAYROLL] === POST REQUEST RECEIVED ===")
        print(f"[PAYROLL] POST data: {request.POST}")
        return super().post(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass request to form for entity pre-population
        kwargs['request'] = self.request
        return kwargs
        print("[PAYROLL] === FORM INVALID ===")
        print(f"[PAYROLL] Form errors: {form.errors}")
        return super().form_invalid(form)
    
    def form_valid(self, form):
        print("[PAYROLL] === FORM SUBMISSION STARTED ===")
        print(f"[PAYROLL] Form data: {form.cleaned_data}")
        try:
            # Save payroll
            payroll = form.save(commit=False)
            payroll.save()
            print(f"[PAYROLL] Created payroll: {payroll.payroll_number}, Entity: {payroll.entity}")
            
            # Auto-create payroll records for active employees
            from hr.models import PayrollRecord
            
            # Debug: Check what employees exist
            all_employees = Employee.objects.filter(entity=payroll.entity)
            print(f"[PAYROLL] Total employees in entity: {all_employees.count()}")
            
            # Fetch active employees
            employees = Employee.objects.filter(
                entity=payroll.entity,
                status__in=['ACTIVE', 'ON_LEAVE']
            )
            print(f"[PAYROLL] Active/On-Leave employees: {employees.count()}")
            
            # List employee details for debugging
            for emp in employees:
                print(f"[PAYROLL] Employee: {emp.employee_id} - {emp.first_name} {emp.last_name}, Status: {emp.status}, Base Salary: {emp.base_salary}")
            
            for employee in employees:
                record, created = PayrollRecord.objects.get_or_create(
                    payroll=payroll,
                    employee=employee,
                    defaults={
                        'base_salary': employee.base_salary or 0,
                        'gross_amount': employee.base_salary or 0,
                        'net_amount': employee.base_salary or 0,
                        'total_deductions': 0,
                        'total_taxes': 0,
                    }
                )
                print(f"[PAYROLL] {'Created' if created else 'Found'} PayrollRecord for {employee.employee_id}")
            
            # Calculate totals
            try:
                payroll.calculate_totals()
                print(f"[PAYROLL] Calculated totals - Gross: {payroll.total_gross}, Net: {payroll.total_net}")
            except Exception as e:
                # Log error but don't fail
                print(f"[PAYROLL] Error calculating totals: {e}")
                import traceback
                traceback.print_exc()
                payroll.save()
            
            # Set object for success URL
            self.object = payroll
            
            # Redirect to success URL
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())
        except Exception as e:
            # Log the error and show it
            print(f"[PAYROLL] Error creating payroll: {e}")
            import traceback
            traceback.print_exc()
            form.add_error(None, f"Error creating payroll: {str(e)}")
            return self.form_invalid(form)


class PayrollApproveView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Approve payroll for processing."""
    model = Payroll
    fields = []
    template_name = 'hr/payroll_approve.html'
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        return Payroll.objects.filter(entity_id=entity_id) if entity_id else Payroll.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payroll = self.get_object()
        context['payroll_records'] = payroll.payroll_records.all()
        return context
    
    def post(self, request, *args, **kwargs):
        payroll = self.get_object()
        # Verify payroll belongs to user's entity
        entity_id = request.session.get('selected_entity_id')
        if payroll.entity_id != entity_id:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
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
    
    # Verify payroll belongs to user's entity
    entity_id = request.session.get('selected_entity_id')
    if payroll.entity_id != entity_id:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if payroll.is_posted:
        return JsonResponse({'error': 'Payroll already posted'}, status=400)
    
    if payroll.status != 'APPROVED':
        return JsonResponse({'error': 'Payroll must be approved first'}, status=400)
    
    try:
        # Get salary expense account from entity
        salary_account = Account.objects.filter(
            entity=payroll.entity,
            account_number__startswith='60'  # Salary expense
        ).first()
        
        # Get payable account
        payable_account = Account.objects.filter(
            entity=payroll.entity,
            account_number__startswith='21'  # Payables
        ).first()
        
        # Only create GL entries if accounts are configured
        if salary_account and payable_account:
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

class LeaveRequestListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List leave requests."""
    model = LeaveRequest
    template_name = 'hr/leave_request_list.html'
    context_object_name = 'leave_requests'
    paginate_by = 50
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        queryset = LeaveRequest.objects.filter(
            employee__entity_id=entity_id
        ).select_related('employee', 'leave_type') if entity_id else LeaveRequest.objects.none()
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-start_date')


class LeaveRequestCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create new leave request."""
    model = LeaveRequest
    form_class = LeaveRequestForm
    template_name = 'hr/leave_request_form.html'
    success_url = reverse_lazy('hr:leave-request-list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity_id = self.request.session.get('selected_entity_id')
        kwargs['entity_id'] = entity_id
        return kwargs
    
    def form_valid(self, form):
        leave_request = form.save(commit=False)
        leave_request.requested_by = self.request.user
        leave_request.status = 'SUBMITTED'  # Set status to SUBMITTED when creating
        
        # Validate leave balance
        try:
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
        except LeaveBalance.DoesNotExist:
            form.add_error(
                None,
                "Leave balance not found for this employee and leave type. Please contact HR."
            )
            return self.form_invalid(form)
        
        return super().form_valid(form)


class LeaveRequestDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Display leave request details."""
    model = LeaveRequest
    template_name = 'hr/leave_request_detail.html'
    context_object_name = 'leave_request'
    
    def get_queryset(self):
        # Filter by entity for security
        entity_id = self.request.session.get('selected_entity_id')
        return LeaveRequest.objects.filter(
            employee__entity_id=entity_id
        ).select_related('employee', 'leave_type', 'requested_by', 'approved_by')


@login_required
def approve_leave_request(request, pk):
    """Approve leave request."""
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    # Verify leave request belongs to user's entity
    entity_id = request.session.get('selected_entity_id')
    if leave_request.employee.entity_id != entity_id:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        leave_request.status = 'APPROVED'
        leave_request.approved_by = request.user
        leave_request.approval_date = timezone.now()
        
        # Save comments if provided
        comments = request.POST.get('comments', '').strip()
        if comments:
            # If the model has a comments field, save it; otherwise ignore
            if hasattr(leave_request, 'comments'):
                leave_request.comments = comments
        
        leave_request.save()
        
        # Update leave balance - add the approved leave duration to "taken"
        try:
            leave_balance = LeaveBalance.objects.get(
                employee=leave_request.employee,
                leave_type=leave_request.leave_type,
                year=leave_request.start_date.year
            )
            # Convert duration to Decimal to avoid type mismatch
            leave_balance.taken = leave_balance.taken + Decimal(str(leave_request.duration))
            leave_balance.save()
        except LeaveBalance.DoesNotExist:
            pass  # Leave balance doesn't exist, but that's okay
        
        messages.success(request, 'Leave request approved successfully!')
        return redirect('hr:leave-request-detail', pk=leave_request.id)
    
    return render(request, 'hr/leave_request_approve.html', {'leave_request': leave_request})


@login_required
def reject_leave_request(request, pk):
    """Reject leave request."""
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    # Verify leave request belongs to user's entity
    entity_id = request.session.get('selected_entity_id')
    if leave_request.employee.entity_id != entity_id:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        leave_request.status = 'REJECTED'
        leave_request.approved_by = request.user
        leave_request.approval_date = timezone.now()
        
        # Save rejection comments if provided
        comments = request.POST.get('comments', '').strip()
        if comments:
            if hasattr(leave_request, 'comments'):
                leave_request.comments = comments
        
        leave_request.save()
        
        messages.success(request, 'Leave request rejected successfully!')
        return redirect('hr:leave-request-detail', pk=leave_request.id)
    
    return render(request, 'hr/leave_request_reject.html', {'leave_request': leave_request})


@login_required
def submit_leave_for_approval(request, pk):
    """Submit leave type for approval."""
    leave = get_object_or_404(Leave, pk=pk)
    
    # Verify leave belongs to user's entity
    entity_id = request.session.get('selected_entity_id')
    if leave.entity_id != entity_id:
        messages.error(request, 'Unauthorized access.')
        return redirect('hr:leave-list')
    
    if leave.status != 'DRAFT':
        messages.warning(request, 'Only draft leave types can be submitted for approval.')
        return redirect('hr:leave-detail', pk=pk)
    
    if request.method == 'POST':
        leave.status = 'SUBMITTED'
        leave.submitted_by = request.user
        leave.submitted_date = timezone.now()
        leave.save()
        messages.success(request, 'Leave type submitted for approval.')
        return redirect('hr:leave-detail', pk=pk)
    
    return render(request, 'hr/leave_approve.html', {'leave': leave, 'action': 'submit'})


@login_required
def approve_leave(request, pk):
    """Approve leave type."""
    leave = get_object_or_404(Leave, pk=pk)
    
    # Verify leave belongs to user's entity
    entity_id = request.session.get('selected_entity_id')
    if leave.entity_id != entity_id:
        messages.error(request, 'Unauthorized access.')
        return redirect('hr:leave-list')
    
    if leave.status != 'SUBMITTED':
        messages.warning(request, 'Only submitted leave types can be approved.')
        return redirect('hr:leave-detail', pk=pk)
    
    if request.method == 'POST':
        leave.status = 'APPROVED'
        leave.approved_by = request.user
        leave.approval_date = timezone.now()
        leave.save()
        messages.success(request, f'Leave type "{leave.name}" has been approved.')
        return redirect('hr:leave-detail', pk=pk)
    
    return render(request, 'hr/leave_approve.html', {'leave': leave, 'action': 'approve'})


@login_required
def reject_leave(request, pk):
    """Reject leave type."""
    leave = get_object_or_404(Leave, pk=pk)
    
    # Verify leave belongs to user's entity
    entity_id = request.session.get('selected_entity_id')
    if leave.entity_id != entity_id:
        messages.error(request, 'Unauthorized access.')
        return redirect('hr:leave-list')
    
    if leave.status != 'SUBMITTED':
        messages.warning(request, 'Only submitted leave types can be rejected.')
        return redirect('hr:leave-detail', pk=pk)
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')
        leave.status = 'REJECTED'
        leave.rejection_reason = rejection_reason
        leave.save()
        messages.success(request, f'Leave type "{leave.name}" has been rejected.')
        return redirect('hr:leave-detail', pk=pk)
    
    return render(request, 'hr/leave_approve.html', {'leave': leave, 'action': 'reject'})


# Performance Management Views

class PerformanceListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List performance reviews."""
    model = Performance
    template_name = 'hr/performance_list.html'
    context_object_name = 'reviews'
    paginate_by = 50
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        queryset = Performance.objects.filter(
            employee__entity_id=entity_id
        ).order_by('-review_date') if entity_id else Performance.objects.none()
        return queryset


@method_decorator(csrf_protect, name='dispatch')
class PerformanceCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create new performance review."""
    model = Performance
    form_class = PerformanceForm
    template_name = 'hr/performance_form.html'
    success_url = reverse_lazy('hr:performance-list')
    
    def form_valid(self, form):
        """Validate and save performance review."""
        try:
            performance = form.save(commit=False)
            performance.reviewed_by = self.request.user
            performance.save()
            messages.success(self.request, 'Performance review saved successfully!')
            return redirect(self.success_url)
        except Exception as e:
            messages.error(self.request, f'Error saving performance review: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Handle form errors."""
        print(f"Form errors: {form.errors}")
        print(f"Form non-field errors: {form.non_field_errors()}")
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)


# Dashboard Views

@login_required
def hr_dashboard(request):
    """HR Dashboard with key metrics and statistics."""
    # Get selected entity from session
    entity_id = request.session.get('selected_entity_id')
    
    if not entity_id:
        return redirect('entity-select')
    
    context = {
        # Employee Statistics
        'total_employees': Employee.objects.filter(
            entity_id=entity_id,
            status='ACTIVE'
        ).count(),
        'employees_on_leave': Employee.objects.filter(
            entity_id=entity_id,
            status='ON_LEAVE'
        ).count(),
        'new_hires_this_month': Employee.objects.filter(
            entity_id=entity_id,
            hire_date__month=timezone.now().month,
            hire_date__year=timezone.now().year
        ).count(),
        
        # Payroll Statistics
        'pending_payrolls': Payroll.objects.filter(
            entity_id=entity_id,
            status='DRAFT'
        ).count(),
        'approved_payrolls': Payroll.objects.filter(
            entity_id=entity_id,
            status='APPROVED'
        ).count(),
        
        # Leave Statistics
        'pending_leave_requests': LeaveRequest.objects.filter(
            employee__entity_id=entity_id,
            status='SUBMITTED'
        ).count(),
        
        # Recent Activities
        'recent_employees': Employee.objects.filter(
            entity_id=entity_id
        ).order_by('-created_at')[:5],
        'recent_payrolls': Payroll.objects.filter(
            entity_id=entity_id
        ).order_by('-created_at')[:5],
    }
    
    return render(request, 'hr/dashboard.html', context)


@login_required
def employee_payroll_history(request, employee_id):
    """View employee payroll history."""
    employee = get_object_or_404(Employee, pk=employee_id)
    
    # Verify employee belongs to user's entity
    entity_id = request.session.get('selected_entity_id')
    if employee.entity_id != entity_id:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
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
    
    # Verify department belongs to user's entity
    entity_id = request.session.get('selected_entity_id')
    if department.entity_id != entity_id:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    employees = department.employees.filter(status='ACTIVE')
    
    total_salary = employees.aggregate(Sum('base_salary'))['base_salary__sum'] or 0
    
    context = {
        'department': department,
        'employees': employees,
        'total_salary': total_salary,
        'employee_count': employees.count(),
    }
    
    return render(request, 'hr/department_report.html', context)


# ============== Additional HR List Views ==============

# Attendance Management
class AttendanceListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all attendance records."""
    model = Attendance
    template_name = 'hr/attendance_list.html'
    context_object_name = 'attendances'
    paginate_by = 20
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        queryset = Attendance.objects.filter(employee__entity_id=entity_id).order_by('-attendance_date') if entity_id else Attendance.objects.none()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
            )
        return queryset

# Position Management
class PositionListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all positions."""
    model = Position
    template_name = 'hr/position_list.html'
    context_object_name = 'positions'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(code__icontains=search)
            )
        return queryset


@method_decorator(csrf_protect, name='dispatch')
class PositionCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create new position."""
    model = Position
    form_class = PositionForm
    template_name = 'hr/position_form.html'
    success_url = reverse_lazy('hr:position-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ensure CSRF token is available
        get_token(self.request)
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass request to form for entity pre-population
        kwargs['request'] = self.request
        return kwargs
    
    def form_valid(self, form):
        """Handle form submission and save position."""
        position = form.save(commit=False)
        # Ensure entity is set from session if form didn't provide it
        if not position.entity_id:
            entity_id = self.request.session.get('selected_entity_id')
            if entity_id:
                position.entity_id = entity_id
            else:
                form.add_error(None, 'No entity selected in session')
                return self.form_invalid(form)
        position.save()
        return super().form_valid(form)


class PositionDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """View position details."""
    model = Position
    template_name = 'hr/position_detail.html'
    context_object_name = 'position'
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        return Position.objects.filter(entity_id=entity_id) if entity_id else Position.objects.none()


@method_decorator(csrf_protect, name='dispatch')
class PositionUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update position."""
    model = Position
    form_class = PositionForm
    template_name = 'hr/position_form.html'
    success_url = reverse_lazy('hr:position-list')
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        return Position.objects.filter(entity_id=entity_id) if entity_id else Position.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass request to form for entity pre-population
        kwargs['request'] = self.request
        return kwargs

# Department Management
class DepartmentListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all departments."""
    model = Department
    template_name = 'hr/department_list.html'
    context_object_name = 'departments'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search)
            )
        return queryset


@method_decorator(csrf_protect, name='dispatch')
class DepartmentCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create new department."""
    model = Department
    form_class = DepartmentForm
    template_name = 'hr/department_form.html'
    success_url = reverse_lazy('hr:department-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_token(self.request)
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def form_valid(self, form):
        department = form.save(commit=False)
        if not department.entity_id:
            entity_id = self.request.session.get('selected_entity_id')
            if entity_id:
                department.entity_id = entity_id
            else:
                form.add_error(None, 'No entity selected in session')
                return self.form_invalid(form)
        department.save()
        return super().form_valid(form)


class DepartmentDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """View department details."""
    model = Department
    template_name = 'hr/department_detail.html'
    context_object_name = 'department'
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        return Department.objects.filter(entity_id=entity_id) if entity_id else Department.objects.none()


@method_decorator(csrf_protect, name='dispatch')
class DepartmentUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update department."""
    model = Department
    form_class = DepartmentForm
    template_name = 'hr/department_form.html'
    success_url = reverse_lazy('hr:department-list')
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        return Department.objects.filter(entity_id=entity_id) if entity_id else Department.objects.none()
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

# Payroll Records
class PayrollRecordListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all payroll records."""
    model = PayrollRecord
    template_name = 'hr/payrollrecord_list.html'
    context_object_name = 'payroll_records'
    paginate_by = 20
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        queryset = PayrollRecord.objects.filter(employee__entity_id=entity_id).order_by('-created_at') if entity_id else PayrollRecord.objects.none()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
            )
        return queryset


class PayrollRecordDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """View payroll record details."""
    model = PayrollRecord
    template_name = 'hr/payrollrecord_detail.html'
    context_object_name = 'payroll_record'
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        return PayrollRecord.objects.filter(employee__entity_id=entity_id) if entity_id else PayrollRecord.objects.none()

# Salary History
class SalaryHistoryListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all salary history records."""
    model = SalaryHistory
    template_name = 'hr/salaryhistory_list.html'
    context_object_name = 'salary_histories'
    paginate_by = 20
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        queryset = SalaryHistory.objects.filter(employee__entity_id=entity_id).order_by('-effective_date') if entity_id else SalaryHistory.objects.none()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
            )
        return queryset


@method_decorator(csrf_protect, name='dispatch')
class SalaryHistoryCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create salary history record for employee salary update."""
    model = SalaryHistory
    form_class = SalaryHistoryForm
    template_name = 'hr/salaryhistory_form.html'
    success_url = reverse_lazy('hr:salaryhistory-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_token(self.request)
        entity_id = self.request.session.get('selected_entity_id')
        context['employees'] = Employee.objects.filter(entity_id=entity_id, status='ACTIVE') if entity_id else Employee.objects.none()
        context['is_edit'] = False
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity_id = self.request.session.get('selected_entity_id')
        return kwargs
    
    def form_valid(self, form):
        salary_history = form.save(commit=False)
        # Verify employee belongs to selected entity
        entity_id = self.request.session.get('selected_entity_id')
        if salary_history.employee.entity_id != entity_id:
            form.add_error('employee', 'Selected employee does not belong to your entity')
            return self.form_invalid(form)
        
        # Set initial status to REQUESTED
        salary_history.status = 'REQUESTED'
        salary_history.save()
        
        return super().form_valid(form)


class SalaryHistoryDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """View salary history record details."""
    model = SalaryHistory
    template_name = 'hr/salaryhistory_detail.html'
    context_object_name = 'salary_history'
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        return SalaryHistory.objects.filter(employee__entity_id=entity_id) if entity_id else SalaryHistory.objects.none()
    
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            messages.warning(request, 'Salary history record not found in current entity. Redirecting to dashboard.')
            return redirect('hr:dashboard')


@method_decorator(csrf_protect, name='dispatch')
class SalaryHistoryUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update salary history record with workflow enforcement."""
    model = SalaryHistory
    form_class = SalaryHistoryForm
    template_name = 'hr/salaryhistory_form.html'
    success_url = reverse_lazy('hr:salaryhistory-list')
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        return SalaryHistory.objects.filter(employee__entity_id=entity_id) if entity_id else SalaryHistory.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_token(self.request)
        entity_id = self.request.session.get('selected_entity_id')
        context['employees'] = Employee.objects.filter(entity_id=entity_id, status='ACTIVE') if entity_id else Employee.objects.none()
        context['is_edit'] = True
        # Check if record is approved
        context['is_approved'] = self.object.status == 'APPROVED'
        context['current_status'] = self.object.get_status_display()
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # If status is APPROVED, disable form fields (except for admin override)
        if self.object.status == 'APPROVED' and not self.request.user.is_superuser:
            for field in form.fields:
                form.fields[field].disabled = True
        return form
    
    def form_valid(self, form):
        # Prevent editing of approved records (unless admin)
        if self.object.status == 'APPROVED' and not self.request.user.is_superuser:
            messages.error(self.request, 'Cannot edit an approved salary history record. Contact admin if changes are needed.')
            return self.form_invalid(form)
        
        salary_history = form.save(commit=False)
        
        # Verify employee belongs to selected entity
        entity_id = self.request.session.get('selected_entity_id')
        if salary_history.employee.entity_id != entity_id:
            form.add_error('employee', 'Selected employee does not belong to your entity')
            return self.form_invalid(form)
        
        # Handle workflow transitions
        if salary_history.status == 'APPROVED':
            # When transitioning to APPROVED, set approved_by and date
            salary_history.approved_by = form.cleaned_data.get('approved_by') or self.request.user
            salary_history.approved_date = timezone.now()
            # Only update employee salary when approved
            salary_history.employee.base_salary = salary_history.salary_after
            salary_history.employee.save()
        
        salary_history.save()
        messages.success(self.request, f'Salary history updated. Status: {salary_history.get_status_display()}')
        return super().form_valid(form)

# Benefits Management
class BenefitListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all benefits."""
    model = Benefit
    template_name = 'hr/benefit_list.html'
    context_object_name = 'benefits'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search)
            )
        return queryset


class BenefitCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new benefit."""
    model = Benefit
    form_class = BenefitForm
    template_name = 'hr/benefit_form.html'
    success_url = reverse_lazy('hr:benefit-list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        entity_id = self.request.session.get('selected_entity_id')
        if entity_id:
            initial['entity'] = entity_id
        return initial
    
    def form_valid(self, form):
        messages.success(self.request, f'Benefit "{form.cleaned_data["name"]}" created successfully.')
        return super().form_valid(form)


class BenefitDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """View benefit details."""
    model = Benefit
    template_name = 'hr/benefit_detail.html'
    context_object_name = 'benefit'
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        return Benefit.objects.filter(entity_id=entity_id) if entity_id else Benefit.objects.none()
    
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            messages.warning(request, 'Benefit not found in current entity. Redirecting to benefits list.')
            return redirect('hr:benefit-list')


class BenefitUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update a benefit."""
    model = Benefit
    form_class = BenefitForm
    template_name = 'hr/benefit_form.html'
    success_url = reverse_lazy('hr:benefit-list')
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        return Benefit.objects.filter(entity_id=entity_id) if entity_id else Benefit.objects.none()
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Benefit "{form.cleaned_data["name"]}" updated successfully.')
        return super().form_valid(form)

# Employee Benefits
class EmployeeBenefitListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all employee benefits."""
    model = EmployeeBenefit
    template_name = 'hr/employeebenefit_list.html'
    context_object_name = 'employee_benefits'
    paginate_by = 20
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        queryset = EmployeeBenefit.objects.filter(employee__entity_id=entity_id).order_by('-enrollment_date') if entity_id else EmployeeBenefit.objects.none()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
            )
        return queryset


class EmployeeBenefitCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Assign a benefit to an employee."""
    model = EmployeeBenefit
    form_class = EmployeeBenefitForm
    template_name = 'hr/employeebenefit_form.html'
    success_url = reverse_lazy('hr:employeebenefit-list')
    
    def get_initial(self):
        initial = super().get_initial()
        initial['enrollment_date'] = timezone.now().date()
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity_id = self.request.session.get('selected_entity_id')
        # Filter employees by entity
        context['form'].fields['employee'].queryset = Employee.objects.filter(entity_id=entity_id, status='ACTIVE')
        # Filter benefits by entity
        context['form'].fields['benefit'].queryset = Benefit.objects.filter(entity_id=entity_id, is_active=True)
        return context
    
    def form_valid(self, form):
        # Verify employee and benefit belong to the same entity
        employee = form.cleaned_data['employee']
        entity_id = self.request.session.get('selected_entity_id')
        
        if employee.entity_id != entity_id:
            form.add_error('employee', 'Selected employee does not belong to your entity')
            return self.form_invalid(form)
        
        messages.success(self.request, f'Benefit assigned to {employee.full_name} successfully.')
        return super().form_valid(form)


class EmployeeBenefitUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update employee benefit assignment."""
    model = EmployeeBenefit
    form_class = EmployeeBenefitForm
    template_name = 'hr/employeebenefit_form.html'
    success_url = reverse_lazy('hr:employeebenefit-list')
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        return EmployeeBenefit.objects.filter(employee__entity_id=entity_id) if entity_id else EmployeeBenefit.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        entity_id = self.request.session.get('selected_entity_id')
        # Filter employees by entity
        context['form'].fields['employee'].queryset = Employee.objects.filter(entity_id=entity_id, status='ACTIVE')
        # Filter benefits by entity
        context['form'].fields['benefit'].queryset = Benefit.objects.filter(entity_id=entity_id, is_active=True)
        return context
    
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            messages.warning(request, 'Employee benefit record not found in current entity. Redirecting to list.')
            return redirect('hr:employeebenefit-list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Employee benefit updated successfully.')
        return super().form_valid(form)

# Leave Management
class LeaveListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all leave types."""
    model = Leave
    template_name = 'hr/leave_list.html'
    context_object_name = 'leaves'
    paginate_by = 20
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        queryset = Leave.objects.filter(entity_id=entity_id) if entity_id else Leave.objects.none()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search)
            )
        return queryset


class LeaveCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new leave type."""
    model = Leave
    form_class = LeaveForm
    template_name = 'hr/leave_form.html'
    success_url = reverse_lazy('hr:leave-list')
    
    def get_initial(self):
        initial = super().get_initial()
        entity_id = self.request.session.get('selected_entity_id')
        if entity_id:
            initial['entity'] = entity_id
        return initial
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity_id = self.request.session.get('selected_entity_id')
        kwargs['entity_id'] = entity_id
        return kwargs
    def form_valid(self, form):
        messages.success(self.request, f'Leave type "{form.cleaned_data["name"]}" created successfully.')
        return super().form_valid(form)


class LeaveDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """View leave type details."""
    model = Leave
    template_name = 'hr/leave_detail.html'
    context_object_name = 'leave'
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        return Leave.objects.filter(entity_id=entity_id) if entity_id else Leave.objects.none()
    
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            messages.warning(request, 'Leave type not found in current entity. Redirecting to list.')
            return redirect('hr:leave-list')


class LeaveUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update a leave type."""
    model = Leave
    form_class = LeaveForm
    template_name = 'hr/leave_form.html'
    success_url = reverse_lazy('hr:leave-list')
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        return Leave.objects.filter(entity_id=entity_id) if entity_id else Leave.objects.none()
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity_id = self.request.session.get('selected_entity_id')
        kwargs['entity_id'] = entity_id
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Leave type "{form.cleaned_data["name"]}" updated successfully.')
        return super().form_valid(form)

# Leave Balances
class LeaveBalanceListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all leave balances."""
    model = LeaveBalance
    template_name = 'hr/leavebalance_list.html'
    context_object_name = 'leave_balances'
    paginate_by = 20
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        queryset = LeaveBalance.objects.filter(employee__entity_id=entity_id) if entity_id else LeaveBalance.objects.none()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
            )
        return queryset


class LeaveBalanceCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new leave balance."""
    model = LeaveBalance
    form_class = LeaveBalanceForm
    template_name = 'hr/leavebalance_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['entity_id'] = self.request.session.get('selected_entity_id')
        return kwargs
    
    def get_success_url(self):
        return reverse('hr:leavebalance-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Leave Balance'
        context['action'] = 'Create'
        return context


class LeaveBalanceUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update an existing leave balance."""
    model = LeaveBalance
    form_class = LeaveBalanceForm
    template_name = 'hr/leavebalance_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['entity_id'] = self.request.session.get('selected_entity_id')
        return kwargs
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        return LeaveBalance.objects.filter(employee__entity_id=entity_id)
    
    def get_success_url(self):
        return reverse('hr:leavebalance-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee_name = f"{self.object.employee.first_name} {self.object.employee.last_name}".strip()
        if not employee_name:
            employee_name = str(self.object.employee)
        context['title'] = f'Edit Leave Balance - {employee_name} ({self.object.leave_type.name})'
        context['action'] = 'Update'
        return context


class LeaveBalanceDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Display leave balance details."""
    model = LeaveBalance
    template_name = 'hr/leavebalance_detail.html'
    context_object_name = 'leave_balance'
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        return LeaveBalance.objects.filter(employee__entity_id=entity_id)

# Disciplinary Management
class DisciplinaryListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all disciplinary records."""
    model = Disciplinary
    template_name = 'hr/disciplinary_list.html'
    context_object_name = 'disciplinary_records'
    paginate_by = 20
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        queryset = Disciplinary.objects.filter(employee__entity_id=entity_id).order_by('-incident_date') if entity_id else Disciplinary.objects.none()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
            )
        return queryset


# Position Management API
@login_required
def create_position(request):
    """Redirect to PositionCreateView for backward compatibility."""
    return PositionCreateView.as_view()(request)

