"""
CRM Module Forms
Forms for leads, opportunities, quotes, activities, and campaigns
"""

from django import forms
from .models import Lead, Opportunity, Quote, Activity, Campaign, SalesStage


class LeadForm(forms.ModelForm):
    """Form for creating/editing leads."""
    
    class Meta:
        model = Lead
        fields = ['lead_name', 'email', 'phone', 'company_name', 'address', 'city', 
                  'state', 'postal_code', 'country', 'source', 'lead_score']
        widgets = {
            'lead_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lead name',
                'required': 'required'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email address',
                'required': 'required'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number',
                'type': 'tel'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company name',
                'required': 'required'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Street address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State/Province'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Postal code'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country'
            }),
            'source': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'lead_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0-100',
                'min': '0',
                'max': '100',
                'required': 'required'
            }),
        }


class OpportunityForm(forms.ModelForm):
    """Form for creating/editing opportunities."""
    
    class Meta:
        model = Opportunity
        fields = ['opportunity_name', 'lead', 'customer', 'stage', 'deal_amount', 
                  'win_probability', 'expected_close_date', 'description']
        widgets = {
            'opportunity_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Opportunity name',
                'required': 'required'
            }),
            'lead': forms.Select(attrs={
                'class': 'form-select'
            }),
            'customer': forms.Select(attrs={
                'class': 'form-select'
            }),
            'stage': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'deal_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'required': 'required'
            }),
            'win_probability': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0-100 %',
                'min': '0',
                'max': '100',
                'required': 'required'
            }),
            'expected_close_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Opportunity details'
            }),
        }


class QuoteForm(forms.ModelForm):
    """Form for creating/editing quotes."""
    
    class Meta:
        model = Quote
        fields = ['opportunity', 'quote_date', 'valid_until', 'status', 
                  'subtotal', 'tax_amount', 'payment_terms', 'delivery_terms', 'notes']
        widgets = {
            'opportunity': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'quote_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'valid_until': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'subtotal': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'required': 'required'
            }),
            'tax_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01'
            }),
            'payment_terms': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Net 30'
            }),
            'delivery_terms': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., FOB'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes'
            }),
        }


class ActivityForm(forms.ModelForm):
    """Form for creating/editing activities (calls, emails, meetings)."""
    
    class Meta:
        model = Activity
        fields = ['lead', 'opportunity', 'customer', 'activity_type', 'subject', 'description', 
                  'activity_date', 'assigned_to', 'is_completed']
        widgets = {
            'lead': forms.Select(attrs={
                'class': 'form-select'
            }),
            'opportunity': forms.Select(attrs={
                'class': 'form-select'
            }),
            'customer': forms.Select(attrs={
                'class': 'form-select'
            }),
            'activity_type': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Activity subject',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Activity details/notes'
            }),
            'activity_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'is_completed': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class CampaignForm(forms.ModelForm):
    """Form for creating/editing marketing campaigns."""
    
    class Meta:
        model = Campaign
        fields = ['campaign_name', 'campaign_type', 'description', 'status',
                  'start_date', 'end_date', 'budget', 'campaign_manager']
        widgets = {
            'campaign_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Campaign name',
                'required': 'required'
            }),
            'campaign_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Email, Cold Call, Social Media',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Campaign description'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
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
            'budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'required': 'required'
            }),
            'campaign_manager': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class SalesStageForm(forms.ModelForm):
    """Form for creating/editing sales pipeline stages."""
    
    class Meta:
        model = SalesStage
        fields = ['stage_name', 'sequence', 'win_probability', 'description']
        widgets = {
            'stage_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Stage name',
                'required': 'required'
            }),
            'sequence': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '1',
                'min': '1',
                'required': 'required'
            }),
            'win_probability': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0-100 %',
                'min': '0',
                'max': '100',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Stage description'
            }),
        }
