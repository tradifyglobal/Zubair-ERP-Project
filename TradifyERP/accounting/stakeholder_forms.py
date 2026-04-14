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
            'first_name', 'last_name', 'middle_name', 'father_name', 'date_of_birth', 'gender',
            'company_name', 'registration_number', 'company_type',
            'email', 'phone_number', 'secondary_phone', 'fax',
            'passport_number', 'aadhar_number', 'pan_sin_number',
            'permanent_address_line_1', 'permanent_address_line_2', 'permanent_city', 'permanent_state_province', 'permanent_postal_code', 'permanent_country',
            'address_line_1', 'address_line_2', 'city', 'state_province', 'postal_code', 'country', 'same_as_permanent',
            'tax_identification_number', 'tax_id_type',
            'nationality', 'occupation', 'relationship_to_company', 'notes', 'joined_date', 'start_date', 'end_date'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'joined_date': forms.DateInput(attrs={'type': 'date'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Dynamically add start_date and end_date fields if they exist on the model
        model_field_names = [f.name for f in self.Meta.model._meta.get_fields()]
        if 'start_date' in model_field_names:
            self.fields['start_date'] = forms.DateField(
                required=False,
                widget=forms.DateInput(attrs={'type': 'date'}),
                label='Start Date'
            )
        if 'end_date' in model_field_names:
            self.fields['end_date'] = forms.DateField(
                required=False,
                widget=forms.DateInput(attrs={'type': 'date'}),
                label='End Date'
            )
        
        # Set default joined_date if not editing an existing instance
        if not self.instance.pk and 'joined_date' in self.fields:
            from django.utils import timezone
            self.fields['joined_date'].initial = timezone.now().date()
            # Make the field not required since we have a default
            self.fields['joined_date'].required = False
        
        # Make start_date and end_date optional
        if 'start_date' in self.fields:
            self.fields['start_date'].required = False
        if 'end_date' in self.fields:
            self.fields['end_date'].required = False
        
        # Make current address fields optional - they'll be validated in clean() based on checkbox
        current_address_fields = ['address_line_1', 'address_line_2', 'city', 'state_province', 'postal_code', 'country']
        for field_name in current_address_fields:
            if field_name in self.fields:
                self.fields[field_name].required = False
        
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
                    Column('father_name', css_class='col-md-12'),
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
                'Identity Documents',
                Row(
                    Column('passport_number', css_class='col-md-4'),
                    Column('aadhar_number', css_class='col-md-4'),
                    Column('pan_sin_number', css_class='col-md-4'),
                )
            ),
            Fieldset(
                'Permanent Address',
                Row(
                    Column('permanent_address_line_1', css_class='col-md-12'),
                    Column('permanent_address_line_2', css_class='col-md-12'),
                ),
                Row(
                    Column('permanent_city', css_class='col-md-4'),
                    Column('permanent_state_province', css_class='col-md-4'),
                    Column('permanent_postal_code', css_class='col-md-4'),
                ),
                Row(
                    Column('permanent_country', css_class='col-md-12'),
                )
            ),
            Fieldset(
                'Current Address',
                Row(
                    Column('same_as_permanent', css_class='col-md-12'),
                ),
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
        
        # Dynamically add Profit Calculation Period section if fields were added
        if 'start_date' in self.fields or 'end_date' in self.fields:
            row_columns = []
            if 'start_date' in self.fields:
                row_columns.append(Column('start_date', css_class='col-md-6'))
            if 'end_date' in self.fields:
                row_columns.append(Column('end_date', css_class='col-md-6'))
            
            profit_fieldset = Fieldset(
                'Profit Calculation Period (Optional)',
                Row(*row_columns) if row_columns else None,
                HTML('<p class="text-muted small">Set the date range for profit calculation purposes. Leave blank for ongoing.</p>')
            )
            # Insert before Additional Information
            self.helper.layout.fields.insert(-1, profit_fieldset)
    
    def clean(self):
        """Validate that current address is filled when not using same as permanent."""
        cleaned_data = super().clean()
        same_as_permanent = cleaned_data.get('same_as_permanent')
        
        # If NOT checking "same as permanent", require current address fields
        if not same_as_permanent:
            required_fields = ['address_line_1', 'city', 'postal_code', 'country']
            for field_name in required_fields:
                value = cleaned_data.get(field_name)
                if not value or str(value).strip() == '':
                    self.add_error(field_name, 'This field is required.')
        
        return cleaned_data


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
        labels = {
            'stakeholder': 'Shareholder',
            'approver_group': 'Approver Group',
        }
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
        
        # Get entity_id from instance, initial data, or form data
        entity_id = None
        if self.instance and hasattr(self.instance, 'entity_id'):
            entity_id = self.instance.entity_id
        elif self.initial and 'entity' in self.initial:
            entity = self.initial.get('entity')
            entity_id = entity.id if hasattr(entity, 'id') else entity
        
        # If still no entity, try to get the first active entity
        if not entity_id:
            from accounting.models import Entity
            active_entity = Entity.objects.filter(is_active=True).first()
            if active_entity:
                entity_id = active_entity.id
        
        # Filter stakeholder and bank profiles by entity
        if entity_id:
            # Filter stakeholders to only show active stakeholders from the current entity
            if 'stakeholder' in self.fields:
                self.fields['stakeholder'].queryset = Stakeholder.objects.filter(
                    entity_id=entity_id,
                    status='ACTIVE'
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
        
        # Add data attributes for currency matching
        if 'currency' in self.fields:
            self.fields['currency'].widget.attrs['data-toggle-field'] = 'exchange_rate'
        if 'currency_destination' in self.fields:
            self.fields['currency_destination'].widget.attrs['data-toggle-field'] = 'exchange_rate'
        if 'exchange_rate' in self.fields:
            self.fields['exchange_rate'].widget.attrs['id'] = 'id_exchange_rate'
            # Make exchange_rate not required since we handle it in clean()
            self.fields['exchange_rate'].required = False
            
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
    
    def clean(self):
        """Validate and set exchange_rate based on currency matching."""
        cleaned_data = super().clean()
        currency = cleaned_data.get('currency')
        currency_destination = cleaned_data.get('currency_destination')
        exchange_rate = cleaned_data.get('exchange_rate')
        
        # If currencies are the same, set exchange_rate to 1.0
        if currency and currency_destination and currency == currency_destination:
            cleaned_data['exchange_rate'] = 1.0
        else:
            # If currencies are different, exchange_rate is required
            if not exchange_rate:
                raise forms.ValidationError(
                    "Exchange rate is required when currencies are different."
                )
        
        return cleaned_data



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


class InternationalTransferTrackingForm(forms.ModelForm):
    """Form for creating/editing international transfer tracking."""
    
    # Add editable entity field dropdown to select which entity this transfer belongs to
    entity = forms.ModelChoiceField(
        label='Transfer Entity',
        queryset=None,  # Will be set in __init__
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text='The business entity that this international transfer belongs to. Select the correct entity if different from contribution.'
    )
    
    class Meta:
        from accounting.models import InternationalTransferTracking
        model = InternationalTransferTracking
        fields = [
            'capital_contribution',
            'source_country', 'source_bank_name', 'source_bank_account', 
            'source_currency_code', 'source_amount',
            'destination_country', 'destination_bank_name', 'destination_bank_account',
            'destination_currency_code', 'destination_amount',
            'exchange_rate_used', 'conversion_date',
            'date_sent_from_shareholder', 'date_received_in_foreign_bank',
            'date_transferred_to_local_bank', 'date_posted_to_gl',
            'transfer_status', 'transfer_reference', 'intermediary_bank_name',
            'intermediary_reference', 'remittance_proof', 'conversion_receipt', 'notes'
        ]
        widgets = {
            'capital_contribution': forms.Select(attrs={'class': 'form-control'}),
            'source_country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Canada, USA'}),
            'source_bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'source_bank_account': forms.TextInput(attrs={'class': 'form-control'}),
            'source_currency_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CAD, USD'}),
            'source_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'destination_country': forms.TextInput(attrs={'class': 'form-control', 'value': 'India'}),
            'destination_bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'destination_bank_account': forms.TextInput(attrs={'class': 'form-control'}),
            'destination_currency_code': forms.TextInput(attrs={'class': 'form-control', 'value': 'INR'}),
            'destination_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'exchange_rate_used': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'conversion_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_sent_from_shareholder': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_received_in_foreign_bank': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_transferred_to_local_bank': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_posted_to_gl': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'transfer_status': forms.Select(attrs={'class': 'form-control'}),
            'transfer_reference': forms.TextInput(attrs={'class': 'form-control'}),
            'intermediary_bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'intermediary_reference': forms.TextInput(attrs={'class': 'form-control'}),
            'remittance_proof': forms.FileInput(attrs={'class': 'form-control'}),
            'conversion_receipt': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from accounting.models import Entity
        
        # Make capital_contribution optional - will be set by view when creating from contribution detail
        if 'capital_contribution' in self.fields:
            self.fields['capital_contribution'].required = False
        
        # Set entity queryset to all active entities
        if 'entity' in self.fields:
            self.fields['entity'].queryset = Entity.objects.filter(is_active=True).order_by('name')
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Investment Link',
                Row(
                    Column('capital_contribution', css_class='col-md-12'),
                ),
                Row(
                    Column('entity', css_class='col-md-12'),
                )
            ),
            Fieldset(
                'Source Information (Shareholder\'s Country)',
                Row(
                    Column('source_country', css_class='col-md-6'),
                    Column('source_currency_code', css_class='col-md-6'),
                ),
                Row(
                    Column('source_bank_name', css_class='col-md-6'),
                    Column('source_bank_account', css_class='col-md-6'),
                ),
                Row(
                    Column('source_amount', css_class='col-md-12'),
                )
            ),
            Fieldset(
                'Destination Information (Local)',
                Row(
                    Column('destination_country', css_class='col-md-6'),
                    Column('destination_currency_code', css_class='col-md-6'),
                ),
                Row(
                    Column('destination_bank_name', css_class='col-md-6'),
                    Column('destination_bank_account', css_class='col-md-6'),
                ),
                Row(
                    Column('destination_amount', css_class='col-md-12'),
                )
            ),
            Fieldset(
                'Conversion Details',
                Row(
                    Column('exchange_rate_used', css_class='col-md-4'),
                    Column('conversion_date', css_class='col-md-8'),
                )
            ),
            Fieldset(
                'Transfer Timeline',
                Row(
                    Column('date_sent_from_shareholder', css_class='col-md-6'),
                    Column('date_received_in_foreign_bank', css_class='col-md-6'),
                ),
                Row(
                    Column('date_transferred_to_local_bank', css_class='col-md-6'),
                    Column('date_posted_to_gl', css_class='col-md-6'),
                )
            ),
            Fieldset(
                'Transfer Status & Reference',
                Row(
                    Column('transfer_status', css_class='col-md-6'),
                    Column('transfer_reference', css_class='col-md-6'),
                ),
                Row(
                    Column('intermediary_bank_name', css_class='col-md-6'),
                    Column('intermediary_reference', css_class='col-md-6'),
                )
            ),
            Fieldset(
                'Documentation',
                Row(
                    Column('remittance_proof', css_class='col-md-6'),
                    Column('conversion_receipt', css_class='col-md-6'),
                ),
                Row(
                    Column('notes', css_class='col-md-12'),
                )
            ),
            HTML('''
            <div class="row mt-4">
                <div class="col-12">
                    <button type="submit" class="btn btn-primary">
                        <i class="mdi mdi-content-save"></i> Create Transfer Tracking
                    </button>
                    <a href="{% url 'accounting:international_capital_report' %}" class="btn btn-secondary ms-2">
                        <i class="mdi mdi-arrow-left"></i> Cancel
                    </a>
                </div>
            </div>
            '''),
        )


# ==================== Capital Contribution Workflow Forms ====================
# DEPRECATED: Workflow moved to transaction level (CashReceiptLine/BankReceiptLine)
#
# The following form classes have been removed:
# - CapitalContributionSubmitForm (line ~472)
# - CapitalContributionReviewForm (line ~549)
# - CapitalContributionApprovalForm (line ~644)
#
# Capital contributions are now auto-created and posted when source transaction is approved.
# No manual submission/review/approval needed at contribution level.
# See REFACTORING_PLAN.md for complete migration information.
