"""
Employee Expense Module Forms
"""

from django import forms
from django.db.models import Q
from django.utils import timezone
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
        widget=forms.Select(attrs={
            'class': 'form-select', 
            'id': 'id_shareholder',
            'data-placeholder': 'Select Employee/Shareholder'
        }),
        label='Employee/Shareholder',
        help_text='Select an employee or shareholder. If shareholder has capital account, it will be shown for GL linking.',
        required=True
    )
    
    class Meta:
        model = EmployeeExpenseReport
        fields = ['employee', 'period_start', 'period_end', 'description']
        widgets = {
            'employee': forms.HiddenInput(),  # Hidden field - will be auto-filled based on shareholder selection
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
        
        # Make employee field not required since it will be populated by clean()
        self.fields['employee'].required = False
        
        # Populate shareholder dropdown from the entity
        if entity:
            stakeholders = Stakeholder.objects.filter(
                entity=entity,
                status='ACTIVE'
            ).select_related('entity').order_by('first_name', 'last_name', 'company_name')
            
            self.fields['shareholder'].queryset = stakeholders
            
            # Custom label to show full name and any capital account info
            def get_stakeholder_label(obj):
                if obj.stakeholder_type == 'INDIVIDUAL':
                    name = f"{obj.first_name or ''} {obj.last_name or ''}".strip()
                else:
                    name = obj.company_name or f"Stakeholder {obj.id}"
                
                # Try to find associated capital account
                capital_contrib = obj.capital_contributions.filter(
                    workflow_status='APPROVED',
                    equity_account__isnull=False
                ).first()
                
                if capital_contrib and capital_contrib.equity_account:
                    return f"{name} (Account: {capital_contrib.equity_account.account_number} - {capital_contrib.equity_account.name})"
                else:
                    return name
            
            self.fields['shareholder'].label_from_instance = get_stakeholder_label
            
            if not stakeholders.exists():
                self.fields['shareholder'].help_text = 'No active stakeholders found in this entity. Please create a stakeholder first.'
                self.fields['shareholder'].disabled = True
        else:
            self.fields['shareholder'].queryset = Stakeholder.objects.none()
            self.fields['shareholder'].help_text = 'Please select an entity first'
    
    def clean(self):
        cleaned_data = super().clean()
        shareholder = cleaned_data.get('shareholder')
        employee = cleaned_data.get('employee')
        
        if not shareholder:
            raise forms.ValidationError("Please select an employee or shareholder")
        
        # If shareholder is selected, create or find an employee record for them
        if shareholder and not employee:
            # Try to find existing employee linked to this shareholder
            try:
                from django.contrib.auth.models import User
                
                # Look for employee with matching stakeholder info
                emp = Employee.objects.filter(
                    entity=shareholder.entity
                ).filter(
                    Q(user__first_name__icontains=shareholder.first_name or '') |
                    Q(user__email=shareholder.email) |
                    Q(employee_id=f"SH-{shareholder.id}")
                ).first()
                
                if not emp:
                    # Create a new employee record linked to this shareholder
                    # First create or get user account
                    username = f"shareholder_{shareholder.id}_{shareholder.entity.id}"
                    user, created = User.objects.get_or_create(
                        username=username[:150],  # Username max length
                        defaults={
                            'first_name': (shareholder.first_name or '')[:150],
                            'last_name': (shareholder.last_name or '')[:150],
                            'email': shareholder.email,
                            'is_active': True
                        }
                    )
                    
                    # Create employee record
                    # Note: Employee model uses 'position' (FK) and 'department' (FK), not text fields
                    emp, created = Employee.objects.get_or_create(
                        user=user,
                        entity=shareholder.entity,
                        defaults={
                            'employee_id': f"SH-{shareholder.id}",
                            'first_name': shareholder.first_name or '',
                            'last_name': shareholder.last_name or '',
                            'email': shareholder.email,
                            'status': 'ACTIVE',
                            'hire_date': timezone.now().date()
                        }
                    )
                    
                    # Store stakeholder reference in employee for future GL account linking
                    if hasattr(emp, 'stakeholder_id'):
                        emp.stakeholder_id = shareholder.id
                        emp.save()
                
                cleaned_data['employee'] = emp
                
            except Exception as e:
                raise forms.ValidationError(f"Error linking shareholder to employee record: {str(e)}")
        
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
    
    def __init__(self, *args, entity=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter categories by entity
        if entity:
            self.fields['category'].queryset = ExpenseCategory.objects.filter(entity=entity)
        else:
            self.fields['category'].queryset = ExpenseCategory.objects.none()


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


class ExpenseBudgetForm(forms.ModelForm):
    """Form for creating/editing expense budgets"""
    
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
                'placeholder': '0.00'
            }),
            'period_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'period_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, entity=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if entity:
            # Filter employees and categories by entity
            self.fields['employee'].queryset = Employee.objects.filter(entity=entity)
            self.fields['category'].queryset = ExpenseCategory.objects.filter(entity=entity, is_active=True)
    
    def clean(self):
        cleaned_data = super().clean()
        period_start = cleaned_data.get('period_start')
        period_end = cleaned_data.get('period_end')
        
        if period_start and period_end and period_start > period_end:
            raise forms.ValidationError("Period end date must be after period start date.")
        
        return cleaned_data
