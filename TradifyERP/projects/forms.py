"""
Project Management Module Forms
Forms for projects, phases, tasks, time tracking, budgets, etc.
"""

from django import forms
from .models import Project, ProjectPhase, Task, TimeEntry, ResourceAllocation, ProjectBudget, ProjectKPI


class ProjectForm(forms.ModelForm):
    """Form for creating/editing projects."""
    
    class Meta:
        model = Project
        fields = ['project_code', 'project_name', 'description', 'start_date', 'planned_end_date', 
                  'status', 'priority', 'project_manager', 'department', 'budgeted_amount']
        widgets = {
            'project_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Project code',
                'required': 'required'
            }),
            'project_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Project name',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Project description and objectives'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'planned_end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'project_manager': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'department': forms.Select(attrs={
                'class': 'form-select'
            }),
            'budgeted_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'required': 'required'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        planned_end_date = cleaned_data.get('planned_end_date')
        
        if start_date and planned_end_date and planned_end_date < start_date:
            raise forms.ValidationError("End date cannot be before start date.")
        
        return cleaned_data


class ProjectPhaseForm(forms.ModelForm):
    """Form for creating/editing project phases."""
    
    class Meta:
        model = ProjectPhase
        fields = ['phase_name', 'description', 'sequence', 'start_date', 
                  'end_date', 'status']
        widgets = {
            'phase_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phase name',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Phase description'
            }),
            'sequence': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '1',
                'min': '1',
                'required': 'required'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class TaskForm(forms.ModelForm):
    """Form for creating/editing project tasks."""
    
    class Meta:
        model = Task
        fields = ['project', 'phase', 'task_name', 'description', 'assigned_to', 'start_date', 
                  'due_date', 'estimated_hours', 'status', 'depends_on']
        widgets = {
            'project': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'phase': forms.Select(attrs={
                'class': 'form-select'
            }),
            'task_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Task name',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Task description'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-select'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'estimated_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0',
                'step': '0.5',
                'required': 'required'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'depends_on': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class TimeEntryForm(forms.ModelForm):
    """Form for time tracking and timesheets."""
    
    class Meta:
        model = TimeEntry
        fields = ['project', 'task', 'employee', 'entry_date', 'hours_worked', 
                  'description', 'is_billable']
        widgets = {
            'project': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'task': forms.Select(attrs={
                'class': 'form-select'
            }),
            'employee': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'entry_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'hours_worked': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.25',
                'min': '0',
                'max': '24',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'What work was done?'
            }),
            'is_billable': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class ResourceAllocationForm(forms.ModelForm):
    """Form for allocating resources to projects."""
    
    class Meta:
        model = ResourceAllocation
        fields = ['project', 'task', 'employee', 'allocation_start_date', 
                  'allocation_end_date', 'hours_per_week', 'hourly_rate', 'is_active']
        widgets = {
            'project': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'task': forms.Select(attrs={
                'class': 'form-select'
            }),
            'employee': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'allocation_start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'allocation_end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'hours_per_week': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '40',
                'min': '0',
                'max': '168',
                'step': '0.5',
                'required': 'required'
            }),
            'hourly_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'required': 'required'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class ProjectBudgetForm(forms.ModelForm):
    """Form for project budget lines and cost tracking."""
    
    class Meta:
        model = ProjectBudget
        fields = ['project', 'category', 'description', 'budgeted_amount', 
                  'committed_amount', 'gl_account']
        widgets = {
            'project': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Budget line description'
            }),
            'budgeted_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'required': 'required'
            }),
            'committed_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'gl_account': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class ProjectKPIForm(forms.ModelForm):
    """Form for tracking project key performance indicators."""
    
    class Meta:
        model = ProjectKPI
        fields = ['project', 'kpi_name', 'description', 'target_value', 'actual_value', 
                  'unit', 'measurement_date', 'status']
        widgets = {
            'project': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'kpi_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'KPI name',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'KPI description'
            }),
            'target_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'required': 'required'
            }),
            'actual_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'unit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '%,hours,etc.',
                'required': 'required'
            }),
            'measurement_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class BulkTimeEntryForm(forms.Form):
    """Form for bulk time entry via CSV/Excel."""
    
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx',
            'required': 'required'
        }),
        label='Upload CSV/Excel file',
        help_text='File should contain: EmployeeID, ProjectCode, TaskName, Date, HoursWorked'
    )
    
    billable = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Mark all entries as billable'
    )
