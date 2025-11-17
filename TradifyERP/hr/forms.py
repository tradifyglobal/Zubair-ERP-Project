"""
HR Module Forms
Forms for employee management, payroll, and leave requests.
"""

from django import forms
from django.core.exceptions import ValidationError
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
            'ssn': forms.TextInput(attrs={'class': 'form-control', 'type': 'password'}),
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


class DepartmentForm(forms.ModelForm):
    """Form for department creation/editing."""
    
    class Meta:
        model = Department
        fields = ['name', 'code', 'description', 'cost_center_account', 'manager', 'annual_budget', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DEPT001'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cost_center_account': forms.Select(attrs={'class': 'form-control'}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
            'annual_budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PositionForm(forms.ModelForm):
    """Form for job position creation/editing."""
    
    class Meta:
        model = Position
        fields = [
            'title', 'code', 'description', 'department', 'employment_type',
            'salary_grade', 'min_salary', 'max_salary', 'salary_expense_account',
            'reports_to', 'is_active'
        ]
        widgets = {
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


class PayrollForm(forms.ModelForm):
    """Form for creating payroll runs."""
    
    class Meta:
        model = Payroll
        fields = ['entity', 'payroll_number', 'payroll_date', 'period_start', 'period_end']
        widgets = {
            'entity': forms.Select(attrs={'class': 'form-control'}),
            'payroll_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PAY-2025-01'}),
            'payroll_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'period_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'period_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
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
            'name', 'benefit_type', 'description', 'employee_cost',
            'employer_cost', 'employee_expense_account', 'employer_expense_account',
            'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'benefit_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'employee_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'employer_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'employee_expense_account': forms.Select(attrs={'class': 'form-control'}),
            'employer_expense_account': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


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
    """Form for salary change records."""
    
    class Meta:
        model = SalaryHistory
        fields = [
            'employee', 'effective_date', 'salary_before', 'salary_after',
            'change_reason', 'performance_rating', 'approval_notes'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'salary_before': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'salary_after': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'change_reason': forms.Select(attrs={'class': 'form-control'}),
            'performance_rating': forms.Select(attrs={'class': 'form-control'}),
            'approval_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
