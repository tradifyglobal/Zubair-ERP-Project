"""
CRM Module Forms
Forms for leads, opportunities, quotes, activities, and campaigns
"""

from django import forms
from .models import (
    Lead, Opportunity, Quote, Activity, Campaign, SalesStage,
    Territory, CustomerGroup, Contact, Prospect, SalesPerson, LeadSource,
    Contract, Appointment, Communication,
    EmailCampaign, SMSCenter, EmailGroup,
    MaintenanceSchedule, MaintenanceVisit, WarrantyClaim, SMSSettings
)

# Currency choices
CURRENCY_CHOICES = [
    ('USD', 'US Dollar (USD)'),
    ('EUR', 'Euro (EUR)'),
    ('GBP', 'British Pound (GBP)'),
    ('JPY', 'Japanese Yen (JPY)'),
    ('CAD', 'Canadian Dollar (CAD)'),
    ('AUD', 'Australian Dollar (AUD)'),
    ('CHF', 'Swiss Franc (CHF)'),
    ('CNY', 'Chinese Yuan (CNY)'),
    ('INR', 'Indian Rupee (INR)'),
    ('MXN', 'Mexican Peso (MXN)'),
    ('SGD', 'Singapore Dollar (SGD)'),
    ('HKD', 'Hong Kong Dollar (HKD)'),
    ('NZD', 'New Zealand Dollar (NZD)'),
    ('SAR', 'Saudi Riyal (SAR)'),
    ('AED', 'UAE Dirham (AED)'),
]

# Payment terms choices
PAYMENT_TERMS_CHOICES = [
    ('Net 15', 'Net 15'),
    ('Net 30', 'Net 30'),
    ('Net 45', 'Net 45'),
    ('Net 60', 'Net 60'),
    ('Net 90', 'Net 90'),
    ('2/10 Net 30', '2/10 Net 30 (2% discount if paid within 10 days)'),
    ('Due Upon Receipt', 'Due Upon Receipt'),
    ('Half Upfront', 'Half Upfront, Half on Delivery'),
    ('Deposit Required', 'Deposit Required (25%)'),
    ('COD', 'Cash On Delivery'),
    ('Custom', 'Custom Terms'),
]

# Delivery terms choices
DELIVERY_TERMS_CHOICES = [
    ('FOB Shipping Point', 'FOB Shipping Point'),
    ('FOB Destination', 'FOB Destination'),
    ('CIF', 'Cost Insurance Freight (CIF)'),
    ('EXW', 'Ex Works (EXW)'),
    ('DDP', 'Delivered Duty Paid (DDP)'),
    ('DDU', 'Delivered Duty Unpaid (DDU)'),
    ('Express Shipping', 'Express Shipping'),
    ('Standard Shipping', 'Standard Shipping'),
    ('Overnight', 'Overnight Delivery'),
    ('Pick Up', 'Pick Up'),
    ('Local Delivery', 'Local Delivery'),
    ('International', 'International Shipping'),
]



class LeadForm(forms.ModelForm):
    """Form for creating/editing leads."""
    
    class Meta:
        model = Lead
        fields = ['lead_name', 'email', 'phone', 'company_name', 'address', 'city', 
                  'state', 'postal_code', 'country', 'source', 'lead_score', 'assigned_to', 'notes']
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
            'assigned_to': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Lead notes'
            }),
        }


class OpportunityForm(forms.ModelForm):
    """Form for creating/editing opportunities."""
    
    class Meta:
        model = Opportunity
        fields = ['opportunity_name', 'customer', 'lead', 'stage', 'status', 'deal_amount', 
                  'currency', 'expected_close_date', 'description']
        widgets = {
            'opportunity_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Opportunity name',
                'required': 'required'
            }),
            'customer': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'lead': forms.Select(attrs={
                'class': 'form-select'
            }),
            'stage': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'deal_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'required': 'required'
            }),
            'currency': forms.Select(choices=CURRENCY_CHOICES, attrs={
                'class': 'form-select',
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
        fields = ['opportunity', 'customer', 'quote_date', 'valid_until', 'status', 
                  'subtotal', 'tax_amount', 'total_amount', 'payment_terms', 'delivery_terms', 'notes']
        widgets = {
            'opportunity': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'customer': forms.Select(attrs={
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
                'step': '0.01',
                'id': 'id_tax_amount'
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'required': 'required',
                'id': 'id_total_amount',
                'readonly': 'readonly'
            }),
            'payment_terms': forms.Select(choices=PAYMENT_TERMS_CHOICES, attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'delivery_terms': forms.Select(choices=DELIVERY_TERMS_CHOICES, attrs={
                'class': 'form-select',
                'required': 'required'
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
                  'activity_date', 'assigned_to', 'is_completed', 'priority']
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
                'placeholder': 'Activity details/notes',
                'required': 'required'
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
            'priority': forms.Select(attrs={
                'class': 'form-select'
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
        fields = ['stage_name', 'sequence', 'win_probability', 'description', 'is_final_stage']
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
                'required': 'required',
                'step': '0.01'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Stage description'
            }),
            'is_final_stage': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


# ===== MASTERS FORMS =====

class TerritoryForm(forms.ModelForm):
    """Form for Territory management."""
    
    class Meta:
        model = Territory
        fields = ['territory_name', 'description', 'region', 'manager', 'annual_target', 'is_active']
        widgets = {
            'territory_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Territory name',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Territory description'
            }),
            'region': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Region (e.g., North America, Europe)'
            }),
            'manager': forms.Select(attrs={
                'class': 'form-select'
            }),
            'annual_target': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class CustomerGroupForm(forms.ModelForm):
    """Form for Customer Group management."""
    
    class Meta:
        model = CustomerGroup
        fields = ['group_name', 'description', 'group_code', 'is_active']
        widgets = {
            'group_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Group name',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Group description'
            }),
            'group_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unique code',
                'required': 'required'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class ContactForm(forms.ModelForm):
    """Form for Contact management."""
    
    class Meta:
        model = Contact
        fields = ['contact_name', 'email', 'phone', 'mobile', 'company', 'designation', 
                  'department', 'address', 'city', 'state', 'postal_code', 'country', 'notes']
        widgets = {
            'contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name',
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
                'type': 'tel',
                'required': 'required'
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mobile number',
                'type': 'tel'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company name',
                'required': 'required'
            }),
            'designation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Job title'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Department'
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
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes'
            }),
        }


class ProspectForm(forms.ModelForm):
    """Form for Prospect management."""
    
    class Meta:
        model = Prospect
        fields = ['prospect_name', 'company', 'email', 'phone', 'status', 'probability', 
                  'estimated_value', 'assigned_to']
        widgets = {
            'prospect_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prospect name',
                'required': 'required'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company name',
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
                'type': 'tel',
                'required': 'required'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'probability': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0-100 %',
                'min': '0',
                'max': '100',
                'required': 'required'
            }),
            'estimated_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class SalesPersonForm(forms.ModelForm):
    """Form for Sales Person management."""
    
    class Meta:
        model = SalesPerson
        fields = ['user', 'employee_id', 'territory', 'manager', 'monthly_target', 'annual_target', 'is_active']
        widgets = {
            'user': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'employee_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Employee ID',
                'required': 'required'
            }),
            'territory': forms.Select(attrs={
                'class': 'form-select'
            }),
            'manager': forms.Select(attrs={
                'class': 'form-select'
            }),
            'monthly_target': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'annual_target': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class LeadSourceForm(forms.ModelForm):
    """Form for Lead Source management."""
    
    class Meta:
        model = LeadSource
        fields = ['source_name', 'source_code', 'description', 'is_active']
        widgets = {
            'source_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Source name',
                'required': 'required'
            }),
            'source_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unique code',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Source description'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


# ===== SALES PIPELINE FORMS =====

class ContractForm(forms.ModelForm):
    """Form for Contract management."""
    
    class Meta:
        model = Contract
        fields = ['contract_name', 'opportunity', 'customer', 'status', 'contract_value', 
                  'currency', 'start_date', 'end_date', 'renewal_date', 'terms', 'notes']
        widgets = {
            'contract_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contract name'
            }),
            'opportunity': forms.Select(attrs={
                'class': 'form-select'
            }),
            'customer': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'contract_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'currency': forms.Select(choices=CURRENCY_CHOICES, attrs={
                'class': 'form-select'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'renewal_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'terms': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Contract terms'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes'
            }),
        }


class AppointmentForm(forms.ModelForm):
    """Form for Appointment management."""
    
    class Meta:
        model = Appointment
        fields = ['title', 'description', 'lead', 'opportunity', 'customer', 'appointment_date', 
                  'duration_minutes', 'assigned_to', 'location', 'status', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Appointment title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Appointment description'
            }),
            'lead': forms.Select(attrs={
                'class': 'form-select'
            }),
            'opportunity': forms.Select(attrs={
                'class': 'form-select'
            }),
            'customer': forms.Select(attrs={
                'class': 'form-select'
            }),
            'appointment_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '30',
                'min': '5',
                'step': '5'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-select'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Meeting location'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Meeting notes'
            }),
        }


class CommunicationForm(forms.ModelForm):
    """Form for Communication management."""
    
    class Meta:
        model = Communication
        fields = ['communication_type', 'lead', 'opportunity', 'customer', 'subject', 'message', 
                  'recipient_name', 'recipient_email', 'outcome', 'next_follow_up']
        widgets = {
            'communication_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'lead': forms.Select(attrs={
                'class': 'form-select'
            }),
            'opportunity': forms.Select(attrs={
                'class': 'form-select'
            }),
            'customer': forms.Select(attrs={
                'class': 'form-select'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Communication subject'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Message content'
            }),
            'recipient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Recipient name'
            }),
            'recipient_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Recipient email'
            }),
            'outcome': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Communication outcome'
            }),
            'next_follow_up': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
        }


# ===== CAMPAIGN FORMS =====

class EmailCampaignForm(forms.ModelForm):
    """Form for Email Campaign management."""
    
    class Meta:
        model = EmailCampaign
        fields = ['campaign_name', 'subject', 'from_email', 'recipient_list', 'email_body', 
                  'template', 'scheduled_date', 'status']
        widgets = {
            'campaign_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Campaign name'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email subject'
            }),
            'from_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'From email address'
            }),
            'recipient_list': forms.SelectMultiple(attrs={
                'class': 'form-select'
            }),
            'email_body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Email content'
            }),
            'template': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Template name'
            }),
            'scheduled_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class SMSCenterForm(forms.ModelForm):
    """Form for SMS Campaign management."""
    
    class Meta:
        model = SMSCenter
        fields = ['campaign_name', 'message', 'recipient_list', 'scheduled_date', 'status']
        widgets = {
            'campaign_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Campaign name'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'SMS message (max 160 characters)'
            }),
            'recipient_list': forms.SelectMultiple(attrs={
                'class': 'form-select'
            }),
            'scheduled_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class EmailGroupForm(forms.ModelForm):
    """Form for Email Group management."""
    
    class Meta:
        model = EmailGroup
        fields = ['group_name', 'description', 'members', 'is_active']
        widgets = {
            'group_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Group name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Group description'
            }),
            'members': forms.SelectMultiple(attrs={
                'class': 'form-select'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


# ===== MAINTENANCE FORMS =====

class MaintenanceScheduleForm(forms.ModelForm):
    """Form for Maintenance Schedule management."""
    
    class Meta:
        model = MaintenanceSchedule
        fields = ['schedule_name', 'description', 'customer', 'frequency', 'last_maintenance_date', 
                  'next_maintenance_date', 'assigned_to', 'notes', 'is_active']
        widgets = {
            'schedule_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Schedule name',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Schedule description'
            }),
            'customer': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'frequency': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'last_maintenance_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'next_maintenance_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class MaintenanceVisitForm(forms.ModelForm):
    """Form for Maintenance Visit record."""
    
    class Meta:
        model = MaintenanceVisit
        fields = ['maintenance_schedule', 'visit_date', 'status', 'technician', 'work_description', 
                  'findings', 'hours_spent', 'parts_replaced', 'parts_cost', 'labor_cost', 'next_visit_date']
        widgets = {
            'maintenance_schedule': forms.Select(attrs={
                'class': 'form-select'
            }),
            'visit_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'technician': forms.Select(attrs={
                'class': 'form-select'
            }),
            'work_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Work performed'
            }),
            'findings': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Findings and observations'
            }),
            'hours_spent': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '1.0',
                'step': '0.5',
                'min': '0'
            }),
            'parts_replaced': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Parts replaced'
            }),
            'parts_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'labor_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'next_visit_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make maintenance_schedule required (user must select one)
        self.fields['maintenance_schedule'].required = True


class WarrantyClaimForm(forms.ModelForm):
    """Form for Warranty Claim management."""
    
    class Meta:
        model = WarrantyClaim
        fields = ['customer', 'product_description', 'purchase_date', 'issue_description', 'status', 
                  'claimed_amount', 'approved_amount', 'assigned_to', 'resolution', 'resolution_date']
        widgets = {
            'customer': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'product_description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product name',
                'required': 'required'
            }),
            'purchase_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'issue_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Issue description',
                'required': 'required'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'claimed_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'required': 'required'
            }),
            'approved_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-select'
            }),
            'resolution': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Resolution details'
            }),
            'resolution_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }


class SMSSettingsForm(forms.ModelForm):
    """Form for SMS Settings configuration."""
    
    class Meta:
        model = SMSSettings
        fields = ['sms_provider', 'api_key', 'api_secret', 'sender_id', 'is_enabled']
        widgets = {
            'sms_provider': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Twilio, AWS SNS',
                'required': 'required'
            }),
            'api_key': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'API Key'
            }),
            'api_secret': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'API Secret'
            }),
            'sender_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sender ID'
            }),
            'is_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

