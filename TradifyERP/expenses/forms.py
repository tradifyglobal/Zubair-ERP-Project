"""
Employee Expense Module Forms
"""

from django import forms
from django.db.models import Q
from .models import (
    EmployeeExpenseReport, EmployeeExpense, ExpenseCategory,
    ExpenseBudget, ExpenseReimbursement
)
from hr.models import Employee
from accounting.models import Stakeholder


class EmployeeExpenseReportForm(forms.ModelForm):
    """Form for creating/editing expense reports with shareholder dropdown"""
    
    # Add a shareholder field for display
    shareholder = forms.ModelChoiceField(
        queryset=Stakeholder.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_shareholder'}),
        label='Employee/Shareholder',
        help_text='Select a shareholder to create expense report for',
        required=False
    )
    
    class Meta:
        model = EmployeeExpenseReport
        fields = ['employee', 'period_start', 'period_end', 'description']
        widgets = {
            'employee': forms.HiddenInput(),  # Hidden field
            'period_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'period_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes about this expense report'
            }),
        }
    
    def __init__(self, *args, entity=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Populate shareholder dropdown from the entity
        if entity:
            stakeholders = Stakeholder.objects.filter(entity=entity).order_by('first_name', 'last_name')
            self.fields['shareholder'].queryset = stakeholders
            
            # Custom label to show full name
            self.fields['shareholder'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}".strip() or str(obj.id)
            
            if not stakeholders.exists():
                self.fields['shareholder'].help_text = 'No shareholders found in this entity'
                self.fields['shareholder'].disabled = True
        else:
            stakeholders = Stakeholder.objects.all().order_by('first_name', 'last_name')
            self.fields['shareholder'].queryset = stakeholders
            self.fields['shareholder'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}".strip() or str(obj.id)
    
    def clean(self):
        cleaned_data = super().clean()
        shareholder = cleaned_data.get('shareholder')
        employee = cleaned_data.get('employee')
        
        # If shareholder is selected, create or find an employee record for them
        if shareholder and not employee:
            # Try to find or create an employee for this shareholder
            try:
                # Check if employee exists for this shareholder
                emp = Employee.objects.filter(
                    user__first_name=shareholder.full_name.split()[0] if shareholder.full_name else '',
                    entity=shareholder.entity
                ).first()
                
                if not emp:
                    # Create a dummy employee record if it doesn't exist
                    from django.contrib.auth.models import User
                    user, created = User.objects.get_or_create(
                        username=f"shareholder_{shareholder.id}",
                        defaults={'first_name': shareholder.full_name, 'last_name': ''}
                    )
                    emp, created = Employee.objects.get_or_create(
                        user=user,
                        entity=shareholder.entity,
                        defaults={'employee_id': f"SH-{shareholder.id}"}
                    )
                
                cleaned_data['employee'] = emp
            except Exception as e:
                raise forms.ValidationError(f"Error linking shareholder: {str(e)}")
        
        if not cleaned_data.get('employee'):
            raise forms.ValidationError("Please select an employee or shareholder")
        
        return cleaned_data


class EmployeeExpenseForm(forms.ModelForm):
    """Form for adding expense items to a report"""
    
    class Meta:
        model = EmployeeExpense
        fields = ['category', 'expense_date', 'description', 'amount', 'receipt', 'receipt_number']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'expense_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Detailed description of expense'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'receipt': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx'
            }),
            'receipt_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Invoice/Receipt number (optional)'
            }),
        }


class ExpenseCategoryForm(forms.ModelForm):
    """Form for managing expense categories"""
    
    class Meta:
        model = ExpenseCategory
        fields = [
            'category_type', 'name', 'description', 'expense_account',
            'daily_limit', 'monthly_limit', 'requires_receipt', 'requires_approval'
        ]
        widgets = {
            'category_type': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category name'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description'
            }),
            'expense_account': forms.Select(attrs={'class': 'form-select'}),
            'daily_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'monthly_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'requires_receipt': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requires_approval': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ExpenseBudgetForm(forms.ModelForm):
    """Form for managing employee expense budgets"""
    
    class Meta:
        model = ExpenseBudget
        fields = ['employee', 'category', 'period', 'budget_amount', 'period_start', 'period_end']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'period': forms.Select(attrs={'class': 'form-select'}),
            'budget_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'period_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'period_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class ExpenseReimbursementForm(forms.ModelForm):
    """Form for processing reimbursements"""
    
    class Meta:
        model = ExpenseReimbursement
        fields = ['method', 'scheduled_date', 'notes']
        widgets = {
            'method': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes'
            }),
        }


class ExpenseApprovalForm(forms.Form):
    """Form for approving/rejecting expenses"""
    
    ACTION_CHOICES = [
        ('approve', 'Approve'),
        ('reject', 'Reject'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Approval or rejection notes'
        }),
        required=False
    )
