"""
Shareholder Investment Forms
Forms for tracking and managing shareholder investments
"""

from django import forms
from accounting.models import ShareholderInvestmentLimit, ShareholderPaymentCommitment, Stakeholder


class ShareholderInvestmentLimitForm(forms.ModelForm):
    """Form for setting shareholder investment limits."""
    
    class Meta:
        model = ShareholderInvestmentLimit
        fields = ['stakeholder', 'currency', 'target_investment_amount', 'is_active']
        widgets = {
            'stakeholder': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
                'title': 'Select shareholder'
            }),
            'currency': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
                'title': 'Currency for investment'
            }),
            'target_investment_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '1000000',
                'step': '0.01',
                'required': 'required',
                'title': 'Target investment amount per shareholder (e.g., 10 Lacs = 1000000)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'title': 'Is this investment limit active?'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter stakeholder by entity
        if 'stakeholder' in self.fields and self.instance:
            entity_id = getattr(self.instance, 'entity_id', None)
            if entity_id:
                self.fields['stakeholder'].queryset = Stakeholder.objects.filter(
                    entity_id=entity_id
                ).order_by('first_name', 'last_name')


class ShareholderPaymentCommitmentForm(forms.ModelForm):
    """Form for tracking shareholder payment commitments."""
    
    class Meta:
        model = ShareholderPaymentCommitment
        fields = ['stakeholder', 'committed_amount', 'currency', 'promised_payment_date', 'status', 'actual_payment_date', 'notes']
        widgets = {
            'stakeholder': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
                'title': 'Select shareholder'
            }),
            'committed_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'required': 'required',
                'title': 'Amount promised to be invested'
            }),
            'currency': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
                'title': 'Currency for committed amount'
            }),
            'promised_payment_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required',
                'title': 'Date shareholder promised to make payment'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
                'title': 'Payment status: Pending/Paid/Overdue/Rescheduled/Cancelled'
            }),
            'actual_payment_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'title': 'Actual date payment was received (if paid)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Additional notes about the commitment',
                'rows': 3,
                'title': 'Any additional notes or details'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter stakeholder by entity
        if 'stakeholder' in self.fields and self.instance:
            entity_id = getattr(self.instance, 'entity_id', None)
            if entity_id:
                self.fields['stakeholder'].queryset = Stakeholder.objects.filter(
                    entity_id=entity_id
                ).order_by('first_name', 'last_name')

