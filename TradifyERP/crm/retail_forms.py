"""
Retail & E-commerce Forms
Forms for loyalty programs, POS transactions, promotions, and customer segments
"""

from django import forms
from .retail_models import (
    LoyaltyProgram, LoyaltyMember, PointTransaction, POSTransaction,
    Promotion, PromotionUsage, CustomerSegment
)


class LoyaltyProgramForm(forms.ModelForm):
    """Form for creating/editing loyalty programs."""
    
    class Meta:
        model = LoyaltyProgram
        fields = ['program_name', 'program_code', 'description', 'loyalty_type', 'status',
                  'points_per_currency', 'point_expiry_days', 'points_per_reward',
                  'reward_value', 'minimum_enrollment_purchase', 'enable_tiers',
                  'launch_date', 'end_date', 'gl_account']
        widgets = {
            'program_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Program name',
                'required': 'required'
            }),
            'program_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unique code',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Program description'
            }),
            'loyalty_type': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'points_per_currency': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '1.0',
                'step': '0.0001',
                'required': 'required'
            }),
            'point_expiry_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '365',
                'min': '0',
                'required': 'required'
            }),
            'points_per_reward': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '100',
                'min': '1',
                'required': 'required'
            }),
            'reward_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'required': 'required'
            }),
            'minimum_enrollment_purchase': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'enable_tiers': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'launch_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'gl_account': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class LoyaltyMemberForm(forms.ModelForm):
    """Form for enrolling/managing loyalty members."""
    
    class Meta:
        model = LoyaltyMember
        fields = ['program', 'customer', 'status', 'email_opted_in', 'sms_opted_in']
        widgets = {
            'program': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'customer': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'email_opted_in': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'sms_opted_in': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class PointTransactionForm(forms.ModelForm):
    """Form for recording point transactions."""
    
    class Meta:
        model = PointTransaction
        fields = ['member', 'transaction_type', 'points', 'reason', 'sale_order_id',
                  'reference_number', 'expiry_date']
        widgets = {
            'member': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'transaction_type': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'points': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'required': 'required'
            }),
            'reason': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Reason for transaction'
            }),
            'sale_order_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Order number'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Reference'
            }),
            'expiry_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }


class POSTransactionForm(forms.ModelForm):
    """Form for recording POS transactions."""
    
    class Meta:
        model = POSTransaction
        fields = ['receipt_number', 'transaction_date', 'customer', 'loyalty_member',
                  'subtotal', 'tax_amount', 'discount_amount', 'total_amount',
                  'payment_method', 'store_location', 'terminal_id', 'status']
        widgets = {
            'receipt_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Receipt number',
                'required': 'required'
            }),
            'transaction_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'required': 'required'
            }),
            'customer': forms.Select(attrs={
                'class': 'form-select'
            }),
            'loyalty_member': forms.Select(attrs={
                'class': 'form-select'
            }),
            'subtotal': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'required': 'required'
            }),
            'tax_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'discount_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'required': 'required'
            }),
            'payment_method': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cash, Card, etc.',
                'required': 'required'
            }),
            'store_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Store location'
            }),
            'terminal_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Terminal ID'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class PromotionForm(forms.ModelForm):
    """Form for creating/editing promotions."""
    
    class Meta:
        model = Promotion
        fields = ['promotion_name', 'promotion_code', 'description', 'promotion_type',
                  'discount_value', 'status', 'target_customers', 'target_tier',
                  'minimum_purchase', 'maximum_discount', 'usage_limit',
                  'start_date', 'end_date', 'is_personalized',
                  'personalization_criteria']
        widgets = {
            'promotion_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Promotion name',
                'required': 'required'
            }),
            'promotion_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Code',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Description'
            }),
            'promotion_type': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'discount_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'required': 'required'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'target_customers': forms.Select(attrs={
                'class': 'form-select'
            }),
            'target_tier': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Target tier'
            }),
            'minimum_purchase': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'maximum_discount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'usage_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Max uses'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'required': 'required'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'required': 'required'
            }),
            'is_personalized': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'personalization_criteria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Personalization criteria'
            }),
        }


class CustomerSegmentForm(forms.ModelForm):
    """Form for creating customer segments."""
    
    class Meta:
        model = CustomerSegment
        fields = ['segment_name', 'description', 'criteria_type', 'min_purchase_amount',
                  'max_purchase_amount', 'min_loyalty_tier', 'geographic_region',
                  'customers', 'is_active']
        widgets = {
            'segment_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Segment name',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Segment description'
            }),
            'criteria_type': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'min_purchase_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'max_purchase_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'min_loyalty_tier': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Minimum tier'
            }),
            'geographic_region': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Region'
            }),
            'customers': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
