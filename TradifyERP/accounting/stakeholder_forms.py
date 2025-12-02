from django import forms
from accounting.models import Stakeholder, CapitalContribution, Shareholding, BankProfile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, Fieldset, HTML


class StakeholderForm(forms.ModelForm):
    """Form for creating/editing stakeholders."""
    
    class Meta:
        model = Stakeholder
        fields = [
            'entity', 'stakeholder_type', 'status', 
            'first_name', 'last_name', 'middle_name', 'date_of_birth', 'gender',
            'company_name', 'registration_number', 'company_type',
            'email', 'phone_number', 'secondary_phone', 'fax',
            'address_line_1', 'address_line_2', 'city', 'state_province', 'postal_code', 'country',
            'tax_identification_number', 'tax_id_type',
            'nationality', 'occupation', 'relationship_to_company', 'notes', 'joined_date'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'joined_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default joined_date if not editing an existing instance
        if not self.instance.pk and 'joined_date' in self.fields:
            from django.utils import timezone
            self.fields['joined_date'].initial = timezone.now().date()
            # Make the field not required since we have a default
            self.fields['joined_date'].required = False
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Basic Information',
                Row(
                    Column('entity', css_class='col-md-6'),
                    Column('stakeholder_type', css_class='col-md-3'),
                    Column('status', css_class='col-md-3'),
                ),
                Row(
                    Column('joined_date', css_class='col-md-4'),
                )
            ),
            Fieldset(
                'Individual Details (if applicable)',
                Row(
                    Column('first_name', css_class='col-md-4'),
                    Column('middle_name', css_class='col-md-4'),
                    Column('last_name', css_class='col-md-4'),
                ),
                Row(
                    Column('date_of_birth', css_class='col-md-6'),
                    Column('gender', css_class='col-md-6'),
                ),
                Row(
                    Column('nationality', css_class='col-md-6'),
                    Column('occupation', css_class='col-md-6'),
                )
            ),
            Fieldset(
                'Corporate Details (if applicable)',
                Row(
                    Column('company_name', css_class='col-md-6'),
                    Column('company_type', css_class='col-md-6'),
                ),
                Row(
                    Column('registration_number', css_class='col-md-12'),
                )
            ),
            Fieldset(
                'Contact Information',
                Row(
                    Column('email', css_class='col-md-6'),
                    Column('phone_number', css_class='col-md-6'),
                ),
                Row(
                    Column('secondary_phone', css_class='col-md-6'),
                    Column('fax', css_class='col-md-6'),
                )
            ),
            Fieldset(
                'Address',
                Row(
                    Column('address_line_1', css_class='col-md-12'),
                    Column('address_line_2', css_class='col-md-12'),
                ),
                Row(
                    Column('city', css_class='col-md-4'),
                    Column('state_province', css_class='col-md-4'),
                    Column('postal_code', css_class='col-md-4'),
                ),
                Row(
                    Column('country', css_class='col-md-12'),
                )
            ),
            Fieldset(
                'Tax & Legal Information',
                Row(
                    Column('tax_id_type', css_class='col-md-4'),
                    Column('tax_identification_number', css_class='col-md-8'),
                )
            ),
            Fieldset(
                'Additional Information',
                Row(
                    Column('relationship_to_company', css_class='col-md-12'),
                ),
                Row(
                    Column('notes', css_class='col-md-12'),
                )
            ),
        )


class CapitalContributionForm(forms.ModelForm):
    """Form for recording capital contributions."""
    
    class Meta:
        model = CapitalContribution
        fields = [
            'entity', 'stakeholder', 'contribution_date', 'status', 'amount', 'currency', 'currency_destination', 'exchange_rate',
            'payment_mode', 'reference_number', 'payment_bank_account', 'payment_method_details',
            'paying_bank_name', 'paying_account_number', 'paying_account_holder',
            'document_file', 'notes'
        ]
        widgets = {
            'stakeholder': forms.Select(attrs={'class': 'form-select'}),
            'contribution_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'currency_destination': forms.Select(attrs={'class': 'form-select'}),
            'exchange_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'payment_mode': forms.Select(attrs={'class': 'form-select'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_bank_account': forms.Select(attrs={'class': 'form-select'}),
            'payment_method_details': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'paying_bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'paying_account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'paying_account_holder': forms.TextInput(attrs={'class': 'form-control'}),
            'document_file': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter stakeholder and bank profiles by entity
        if self.instance:
            # Check if instance has entity_id (might be set but not loaded yet)
            entity_id = getattr(self.instance, 'entity_id', None) or (self.instance.entity_id if hasattr(self.instance, 'entity_id') else None)
            if entity_id:
                # Filter stakeholders to only show those from the current entity
                if 'stakeholder' in self.fields:
                    self.fields['stakeholder'].queryset = Stakeholder.objects.filter(
                        entity_id=entity_id
                    ).order_by('first_name', 'last_name')
                
                # Filter bank profiles to only show those from the current entity
                if 'payment_bank_account' in self.fields:
                    self.fields['payment_bank_account'].queryset = BankProfile.objects.filter(
                        entity_id=entity_id,
                        is_active=True
                    ).order_by('bank_name')
        
        # Set default contribution_date if not editing an existing instance
        if not self.instance.pk and 'contribution_date' in self.fields:
            from django.utils import timezone
            self.fields['contribution_date'].initial = timezone.now().date()
            # Make the field not required since we have a default
            self.fields['contribution_date'].required = False
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Shareholder & Contribution Details',
                Row(
                    Column('entity', css_class='col-md-4'),
                    Column('stakeholder', css_class='col-md-4'),
                    Column('contribution_date', css_class='col-md-4'),
                ),
                Row(
                    Column('status', css_class='col-md-4'),
                )
            ),
            Fieldset(
                'Amount',
                Row(
                    Column('amount', css_class='col-md-6'),
                    Column('currency', css_class='col-md-6'),
                ),
                Row(
                    Column('currency_destination', css_class='col-md-6'),
                    Column('exchange_rate', css_class='col-md-6'),
                )
            ),
            Fieldset(
                'Payment Method',
                Row(
                    Column('payment_mode', css_class='col-md-6'),
                    Column('reference_number', css_class='col-md-6'),
                ),
                Row(
                    Column('payment_method_details', css_class='col-md-12'),
                )
            ),
            Fieldset(
                'Bank/Account Information',
                Row(
                    Column('paying_bank_name', css_class='col-md-6'),
                    Column('paying_account_number', css_class='col-md-6'),
                ),
                Row(
                    Column('paying_account_holder', css_class='col-md-12'),
                ),
                Row(
                    Column('payment_bank_account', css_class='col-md-12'),
                )
            ),
            Fieldset(
                'Documentation',
                Row(
                    Column('document_file', css_class='col-md-12'),
                ),
                Row(
                    Column('notes', css_class='col-md-12'),
                )
            ),
        )


class ShareholdingForm(forms.ModelForm):
    """Form for recording shareholdings."""
    
    class Meta:
        model = Shareholding
        fields = [
            'entity', 'stakeholder', 'share_type', 'share_class', 'number_of_shares', 'par_value',
            'acquisition_date', 'acquisition_price', 'acquisition_currency',
            'vesting_schedule', 'vesting_start_date', 'vesting_end_date',
            'voting_rights_percentage', 'dividend_rights_percentage', 'is_active',
            'is_transferable', 'is_redeemable', 'redemption_price',
            'certificate_number', 'certificate_file', 'notes'
        ]
        widgets = {
            'stakeholder': forms.Select(attrs={'class': 'form-select'}),
            'share_type': forms.Select(attrs={'class': 'form-select'}),
            'share_class': forms.TextInput(attrs={'class': 'form-control'}),
            'number_of_shares': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'par_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'acquisition_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'acquisition_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'acquisition_currency': forms.Select(attrs={'class': 'form-select'}),
            'vesting_schedule': forms.TextInput(attrs={'class': 'form-control'}),
            'vesting_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'vesting_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'voting_rights_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'dividend_rights_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_transferable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_redeemable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'redemption_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'certificate_number': forms.TextInput(attrs={'class': 'form-control'}),
            'certificate_file': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default acquisition_date if not editing an existing instance
        if not self.instance.pk and 'acquisition_date' in self.fields:
            from django.utils import timezone
            self.fields['acquisition_date'].initial = timezone.now().date()
            # Make the field not required since we have a default
            self.fields['acquisition_date'].required = False
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Shareholder & Share Details',
                Row(
                    Column('entity', css_class='col-md-4'),
                    Column('stakeholder', css_class='col-md-4'),
                    Column('share_type', css_class='col-md-4'),
                ),
                Row(
                    Column('share_class', css_class='col-md-4'),
                    Column('number_of_shares', css_class='col-md-4'),
                    Column('par_value', css_class='col-md-4'),
                )
            ),
            Fieldset(
                'Acquisition Information',
                Row(
                    Column('acquisition_date', css_class='col-md-4'),
                    Column('acquisition_price', css_class='col-md-4'),
                    Column('acquisition_currency', css_class='col-md-4'),
                )
            ),
            Fieldset(
                'Vesting Details',
                Row(
                    Column('vesting_schedule', css_class='col-md-12'),
                ),
                Row(
                    Column('vesting_start_date', css_class='col-md-6'),
                    Column('vesting_end_date', css_class='col-md-6'),
                )
            ),
            Fieldset(
                'Rights & Restrictions',
                Row(
                    Column('voting_rights_percentage', css_class='col-md-6'),
                    Column('dividend_rights_percentage', css_class='col-md-6'),
                ),
                Row(
                    Column('is_active', css_class='col-md-3'),
                    Column('is_transferable', css_class='col-md-3'),
                    Column('is_redeemable', css_class='col-md-3'),
                ),
                Row(
                    Column('redemption_price', css_class='col-md-6'),
                )
            ),
            Fieldset(
                'Certificate & Documentation',
                Row(
                    Column('certificate_number', css_class='col-md-6'),
                    Column('certificate_file', css_class='col-md-6'),
                ),
                Row(
                    Column('notes', css_class='col-md-12'),
                )
            ),
        )


class CapitalContributionSubmitForm(forms.ModelForm):
    """Form for submitting a contribution and assigning two reviewers."""
    reviewer = forms.ModelChoiceField(
        queryset=None,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Assign First Reviewer',
        help_text='Select the first user who will review this contribution'
    )
    
    reviewer_2 = forms.ModelChoiceField(
        queryset=None,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Assign Second Reviewer',
        help_text='Select the second user who will review this contribution'
    )
    
    class Meta:
        model = CapitalContribution
        fields = ['review_notes']
        widgets = {
            'review_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes for the reviewers'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth.models import User
        # Show all active users as potential reviewers
        active_users = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
        self.fields['reviewer'].queryset = active_users
        self.fields['reviewer_2'].queryset = active_users
    
    def clean(self):
        cleaned_data = super().clean()
        reviewer = cleaned_data.get('reviewer')
        reviewer_2 = cleaned_data.get('reviewer_2')
        
        if reviewer and reviewer_2 and reviewer == reviewer_2:
            raise forms.ValidationError("First and second reviewers must be different users.")
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save the form and assign reviewers to the contribution."""
        instance = super().save(commit=False)
        
        # Save assigned reviewers
        instance.assigned_reviewer_1 = self.cleaned_data.get('reviewer')
        instance.assigned_reviewer_2 = self.cleaned_data.get('reviewer_2')
        
        if commit:
            instance.save()
        
        return instance


class CapitalContributionReviewForm(forms.ModelForm):
    """Form for completing review and moving to approval when both reviewers have reviewed."""
    approver = forms.ModelChoiceField(
        queryset=None,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Assign Approver',
        help_text='Select the user who will approve this contribution'
    )
    
    class Meta:
        model = CapitalContribution
        fields = ['review_notes_2', 'approval_notes']
        widgets = {
            'review_notes_2': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Your review notes as second reviewer'
            }),
            'approval_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes for the approver'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth.models import User
        # Show all active users as potential approvers
        self.fields['approver'].queryset = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
    
    def save(self, commit=True):
        """Save the form and assign approver to the contribution."""
        instance = super().save(commit=False)
        
        # Save assigned approver
        instance.assigned_approver = self.cleaned_data.get('approver')
        
        if commit:
            instance.save()
        
        return instance


class CapitalContributionApprovalForm(forms.ModelForm):
    """Form for approving a contribution."""
    
    class Meta:
        model = CapitalContribution
        fields = ['status', 'approval_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'approval_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Your approval notes'
            }),
        }
