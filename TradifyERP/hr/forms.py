"""
HR Module Forms
Forms for employee management, payroll, and leave requests.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from datetime import datetime, timedelta

from .models import (
    Employee, Department, Position, Payroll, PayrollRecord,
    Benefit, EmployeeBenefit, Leave, LeaveBalance, LeaveRequest,
    Performance, Disciplinary, SalaryHistory, Attendance
)


class EmployeeForm(forms.ModelForm):
    """Form for creating/updating employees."""
    
    class Meta:
        model = Employee
        fields = [
            'entity', 'employee_id', 'first_name', 'last_name', 'email', 'phone',
            'ssn', 'tax_id', 'position', 'department', 'status',
            'hire_date', 'termination_date', 'base_salary', 'salary_currency',
            'pay_frequency', 'manager', 'address', 'city', 'state',
            'postal_code', 'country', 'user'
        ]
        widgets = {
            'entity': forms.Select(attrs={'class': 'form-control'}),
            'employee_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'EMP001'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'ssn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'termination_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'base_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'salary_currency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'USD'}),
            'pay_frequency': forms.Select(attrs={'class': 'form-control'}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Extract request if passed
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Pre-populate entity from session
        if request and hasattr(request, 'session'):
            entity_id = request.session.get('selected_entity_id')
            if entity_id:
                self.fields['entity'].initial = entity_id
    
    def clean_email(self):
        """Validate email uniqueness excluding current instance."""
        email = self.cleaned_data.get('email')
        if email:
            # Exclude current instance from uniqueness check
            qs = Employee.objects.filter(email=email)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError('This email address is already in use.')
        return email
    
    def clean_employee_id(self):
        """Validate employee_id uniqueness excluding current instance."""
        employee_id = self.cleaned_data.get('employee_id')
        if employee_id:
            # Exclude current instance from uniqueness check
            qs = Employee.objects.filter(employee_id=employee_id)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError('This employee ID is already in use.')
        return employee_id
    
    def clean_ssn(self):
        """Validate SSN uniqueness excluding current instance."""
        ssn = self.cleaned_data.get('ssn')
        if ssn:
            # Exclude current instance from uniqueness check
            qs = Employee.objects.filter(ssn=ssn)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError('This SSN is already in use.')
        return ssn


class DepartmentForm(forms.ModelForm):
    """Form for department creation/editing."""
    
    class Meta:
        model = Department
        fields = ['entity', 'name', 'code', 'description', 'cost_center_account', 'manager', 'annual_budget', 'is_active']
        widgets = {
            'entity': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DEPT001'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cost_center_account': forms.Select(attrs={'class': 'form-control'}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
            'annual_budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Extract request if passed
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Pre-populate entity from session
        if request and hasattr(request, 'session'):
            entity_id = request.session.get('selected_entity_id')
            if entity_id:
                self.fields['entity'].initial = entity_id


class PositionForm(forms.ModelForm):
    """Form for job position creation/editing."""
    
    class Meta:
        model = Position
        fields = [
            'entity', 'title', 'code', 'description', 'department', 'employment_type',
            'salary_grade', 'min_salary', 'max_salary', 'salary_expense_account',
            'reports_to', 'is_active'
        ]
        widgets = {
            'entity': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'POS001'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'employment_type': forms.Select(attrs={'class': 'form-control'}),
            'salary_grade': forms.TextInput(attrs={'class': 'form-control'}),
            'min_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'salary_expense_account': forms.Select(attrs={'class': 'form-control'}),
            'reports_to': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Extract request if passed
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Pre-populate entity from session
        if request and hasattr(request, 'session'):
            entity_id = request.session.get('selected_entity_id')
            if entity_id:
                self.fields['entity'].initial = entity_id


class PayrollForm(forms.ModelForm):
    """Form for creating payroll runs."""
    
    class Meta:
        model = Payroll
        fields = ['entity', 'payroll_number', 'payroll_date', 'period_start', 'period_end']
        widgets = {
            'entity': forms.Select(attrs={'class': 'form-control'}),
            'payroll_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PAY-2025-01 (optional - auto-generated if blank)'}),
            'payroll_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'period_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'period_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Extract request if passed
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        # Make payroll_number optional
        self.fields['payroll_number'].required = False
        
        # Pre-populate entity from session
        if request and hasattr(request, 'session'):
            entity_id = request.session.get('selected_entity_id')
            if entity_id:
                self.fields['entity'].initial = entity_id
    
    def clean(self):
        cleaned_data = super().clean()
        period_start = cleaned_data.get('period_start')
        period_end = cleaned_data.get('period_end')
        payroll_date = cleaned_data.get('payroll_date')
        
        if period_start and period_end:
            if period_start >= period_end:
                raise ValidationError("Period start date must be before period end date.")
        
        if payroll_date and period_end:
            if payroll_date < period_end:
                raise ValidationError("Payroll date must be on or after period end date.")
        
        return cleaned_data


class PayrollRecordForm(forms.ModelForm):
    """Form for editing individual payroll records."""
    
    class Meta:
        model = PayrollRecord
        fields = [
            'days_worked', 'hours_worked', 'overtime_amount', 'bonus',
            'allowances', 'employee_tax', 'social_security',
            'health_insurance', 'other_deductions', 'notes'
        ]
        widgets = {
            'days_worked': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'hours_worked': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'overtime_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bonus': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'allowances': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'employee_tax': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'social_security': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'health_insurance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'other_deductions': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class LeaveRequestForm(forms.ModelForm):
    """Form for employee leave requests."""
    
    class Meta:
        model = LeaveRequest
        fields = ['employee', 'leave_type', 'start_date', 'end_date', 'duration', 'reason']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    def __init__(self, *args, entity_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter employee by entity
        if entity_id:
            self.fields['employee'].queryset = Employee.objects.filter(entity_id=entity_id)
            # Filter leave_type by entity - show all leaves but prefer approved
            # This allows users to see what's available and get proper error messages
            self.fields['leave_type'].queryset = Leave.objects.filter(entity_id=entity_id)
        else:
            self.fields['employee'].queryset = Employee.objects.none()
            self.fields['leave_type'].queryset = Leave.objects.none()
    
    def clean_leave_type(self):
        """Validate that selected leave type is approved."""
        leave_type = self.cleaned_data.get('leave_type')
        if leave_type and leave_type.status != 'APPROVED':
            raise forms.ValidationError(
                f"Leave type '{leave_type.name}' is not approved yet. "
                f"Current status: {leave_type.get_status_display()}"
            )
        return leave_type
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        duration = cleaned_data.get('duration')
        
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("Start date must be before or equal to end date.")
            
            # Validate duration
            days_diff = (end_date - start_date).days + 1
            if duration and duration > days_diff:
                raise ValidationError(f"Duration cannot exceed {days_diff} days based on date range.")
        
        return cleaned_data


class PerformanceForm(forms.ModelForm):
    """Form for performance reviews."""
    
    class Meta:
        model = Performance
        fields = [
            'employee', 'review_date', 'review_period_start', 'review_period_end',
            'overall_rating', 'quality_rating', 'productivity_rating',
            'teamwork_rating', 'leadership_rating', 'strengths',
            'areas_for_improvement', 'goals_for_next_period', 'recommended_raise'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'review_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'review_period_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'review_period_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'overall_rating': forms.Select(attrs={'class': 'form-control'}),
            'quality_rating': forms.Select(attrs={'class': 'form-control'}),
            'productivity_rating': forms.Select(attrs={'class': 'form-control'}),
            'teamwork_rating': forms.Select(attrs={'class': 'form-control'}),
            'leadership_rating': forms.Select(attrs={'class': 'form-control'}),
            'strengths': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'areas_for_improvement': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'goals_for_next_period': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recommended_raise': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    
    def clean(self):
        """Validate the form."""
        cleaned_data = super().clean()
        
        employee = cleaned_data.get('employee')
        review_date = cleaned_data.get('review_date')
        
        if employee and review_date:
            # Check if a review already exists for this employee on this date
            from hr.models import Performance
            existing = Performance.objects.filter(
                employee=employee,
                review_date=review_date
            ).exists()
            
            if existing:
                raise forms.ValidationError(
                    f"A performance review already exists for {employee} on {review_date}."
                )
        
        return cleaned_data


class DisciplinaryForm(forms.ModelForm):
    """Form for disciplinary actions."""
    
    class Meta:
        model = Disciplinary
        fields = [
            'employee', 'action_type', 'action_date', 'reason', 'description',
            'suspension_start', 'suspension_end', 'salary_deduction', 'is_resolved',
            'resolved_date'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'action_type': forms.Select(attrs={'class': 'form-control'}),
            'action_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'suspension_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'suspension_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'salary_deduction': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_resolved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'resolved_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class BenefitForm(forms.ModelForm):
    """Form for creating/editing benefits."""
    
    class Meta:
        model = Benefit
        fields = [
            'entity', 'name', 'benefit_type', 'description',
            'employee_cost', 'employer_cost', 'employee_expense_account', 
            'employer_expense_account', 'is_active'
        ]
        widgets = {
            'entity': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'benefit_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'employee_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'employer_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'employee_expense_account': forms.Select(attrs={'class': 'form-control'}),
            'employer_expense_account': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Extract request if passed
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Pre-populate entity from session
        if request and hasattr(request, 'session'):
            entity_id = request.session.get('selected_entity_id')
            if entity_id:
                self.fields['entity'].initial = entity_id


class EmployeeBenefitForm(forms.ModelForm):
    """Form for enrolling employees in benefits."""
    
    class Meta:
        model = EmployeeBenefit
        fields = [
            'employee', 'benefit', 'enrollment_date', 'termination_date',
            'employee_contribution', 'employer_contribution', 'is_active'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'benefit': forms.Select(attrs={'class': 'form-control'}),
            'enrollment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'termination_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'employee_contribution': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'employer_contribution': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SalaryHistoryForm(forms.ModelForm):
    """Form for salary change records with workflow approval."""
    
    # Additional field for approver selection
    approved_by = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True),
        required=False,
        label='Select Approver',
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Select who should approve this salary change'
    )
    
    class Meta:
        model = SalaryHistory
        fields = [
            'employee', 'effective_date', 'salary_before', 'salary_after',
            'change_reason', 'performance_rating', 'status', 'approved_by', 'approval_notes'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'salary_before': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'salary_after': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'change_reason': forms.Select(attrs={'class': 'form-control'}),
            'performance_rating': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'approval_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class LeaveForm(forms.ModelForm):
    """Form for creating/editing leave types."""
    
    ACCRUAL_CHOICES = [
        ('ANNUAL', 'Annual - All days at beginning of year'),
        ('MONTHLY', 'Monthly - Accrued each month'),
        ('QUARTERLY', 'Quarterly - Accrued each quarter'),
    ]
    
    accrual_method = forms.ChoiceField(
        choices=ACCRUAL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="How and when leave is accrued"
    )
    
    class Meta:
        model = Leave
        fields = [
            'entity', 'name', 'code', 'annual_allocation', 'accrual_method',
            'can_carry_over', 'max_carryover', 'requires_approval', 'notice_days_required'
        ]
        widgets = {
            'entity': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_name', 'placeholder': 'Enter leave type name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_code', 'readonly': 'readonly', 'placeholder': 'Auto-generated'}),
            'annual_allocation': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'can_carry_over': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'max_carryover': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '5'}),
            'requires_approval': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notice_days_required': forms.NumberInput(attrs={'class': 'form-control', 'type': 'number'}),
        }
    
    def __init__(self, *args, entity_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter entity field to show only the selected entity
        if entity_id:
            from accounting.models import Entity
            self.fields['entity'].queryset = Entity.objects.filter(id=entity_id)
            self.fields['entity'].initial = entity_id
    
    def clean_max_carryover(self):
        """Validate that max carryover is not more than 5 days."""
        max_carryover = self.cleaned_data.get('max_carryover')
        if max_carryover and max_carryover > 5:
            raise forms.ValidationError('Maximum carryover cannot exceed 5 days.')
        return max_carryover
    
    def clean_code(self):
        """Validate that code is unique (excluding current instance)."""
        code = self.cleaned_data.get('code')
        if code:
            qs = Leave.objects.filter(code=code)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('This leave code already exists.')
        return code


class LeaveBalanceForm(forms.ModelForm):
    """Form for managing employee leave balances."""
    
    class Meta:
        model = LeaveBalance
        fields = [
            'employee', 'leave_type', 'year', 'opening_balance',
            'allocated', 'taken'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'type': 'number', 'min': '2020'}),
            'opening_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'allocated': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'taken': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }
    
    def __init__(self, *args, entity_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter employee by entity
        if entity_id:
            self.fields['employee'].queryset = Employee.objects.filter(entity_id=entity_id)
            self.fields['leave_type'].queryset = Leave.objects.filter(entity_id=entity_id)
        else:
            self.fields['employee'].queryset = Employee.objects.none()
            self.fields['leave_type'].queryset = Leave.objects.none()
    
    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get('employee')
        leave_type = cleaned_data.get('leave_type')
        year = cleaned_data.get('year')
        
        # Check for duplicate leave balance
        if employee and leave_type and year:
            qs = LeaveBalance.objects.filter(
                employee=employee,
                leave_type=leave_type,
                year=year
            )
            # Exclude current instance if updating
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            
            if qs.exists():
                raise forms.ValidationError(
                    f'Leave balance for {employee} - {leave_type} ({year}) already exists.'
                )
        
        return cleaned_data
