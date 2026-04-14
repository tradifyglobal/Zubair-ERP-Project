"""
Journal Voucher Forms with Inline Formsets for Line Items
"""
from django import forms
from django.forms import inlineformset_factory
from decimal import Decimal
from .models import JournalVoucher, JournalVoucherLine, Account, Stakeholder
from django.contrib.auth.models import User


class JournalVoucherForm(forms.ModelForm):
    """Form for Journal Voucher header"""
    
    class Meta:
        model = JournalVoucher
        fields = [
            'voucher_number', 'voucher_date', 'voucher_type', 
            'reference_number', 'reference_type', 'description',
            'attachment', 'notes'
        ]
        widgets = {
            'voucher_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Auto-generated',
                'readonly': 'readonly'
            }),
            'voucher_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'voucher_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'External reference (optional)'
            }),
            'reference_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Invoice, Receipt (optional)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Voucher description/narration'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes (optional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.entity = kwargs.pop('entity', None)
        super().__init__(*args, **kwargs)
        
        # Voucher number is auto-generated
        self.fields['voucher_number'].required = False
        
        # Make some fields optional
        self.fields['reference_number'].required = False
        self.fields['reference_type'].required = False
        self.fields['attachment'].required = False
        self.fields['notes'].required = False


class JournalVoucherLineForm(forms.ModelForm):
    """Form for individual Journal Voucher lines"""
    
    class Meta:
        model = JournalVoucherLine
        fields = [
            'line_number', 'account', 'entry_type', 'amount', 
            'description',
            'cost_center', 'project', 'department'
        ]
        widgets = {
            'line_number': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'min': '1'
            }),
            'account': forms.Select(attrs={
                'class': 'form-select form-select-sm'
            }),
            'entry_type': forms.Select(attrs={
                'class': 'form-select form-select-sm'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'step': '0.01',
                'min': '0.01'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Line description (optional)'
            }),
            'cost_center': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Cost center (optional)'
            }),
            'project': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Project (optional)'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Department (optional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.entity = kwargs.pop('entity', None)
        super().__init__(*args, **kwargs)
        
        # Filter accounts by entity if provided
        if self.entity:
            self.fields['account'].queryset = Account.objects.filter(
                entity=self.entity, 
                is_active=True
            ).order_by('account_number')
        
        # Make optional fields not required
        self.fields['description'].required = False
        self.fields['cost_center'].required = False
        self.fields['project'].required = False
        self.fields['department'].required = False


# Create the inline formset for voucher lines
JournalVoucherLineFormSet = inlineformset_factory(
    JournalVoucher,
    JournalVoucherLine,
    form=JournalVoucherLineForm,
    extra=6,  # Number of empty forms to display (8 total with min_num=2)
    can_delete=True,
    min_num=2,  # Minimum 2 lines (at least 1 debit and 1 credit)
    validate_min=True,
)


class JournalVoucherFilterForm(forms.Form):
    """Form for filtering journal vouchers"""
    
    voucher_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(JournalVoucher.VOUCHER_TYPE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + list(JournalVoucher.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search voucher number or description...'
        })
    )
