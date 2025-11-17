from django import forms
from accounting.models import Stakeholder, CapitalContribution, Shareholding
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, Fieldset, HTML


class StakeholderForm(forms.ModelForm):
    """Form for creating/editing stakeholders."""
    
    class Meta:
        model = Stakeholder
        fields = [
            'stakeholder_type', 'status', 
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
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Basic Information',
                Row(
                    Column('stakeholder_type', css_class='col-md-4'),
                    Column('status', css_class='col-md-4'),
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
            'contribution_date', 'status', 'amount', 'currency', 'currency_destination', 'exchange_rate',
            'payment_mode', 'reference_number', 'payment_bank_account', 'payment_method_details',
            'paying_bank_name', 'paying_account_number', 'paying_account_holder',
            'document_file', 'notes'
        ]
        widgets = {
            'contribution_date': forms.DateInput(attrs={'type': 'date'}),
            'payment_method_details': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Contribution Details',
                Row(
                    Column('contribution_date', css_class='col-md-4'),
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
            'share_type', 'share_class', 'number_of_shares', 'par_value',
            'acquisition_date', 'acquisition_price', 'acquisition_currency',
            'vesting_schedule', 'vesting_start_date', 'vesting_end_date',
            'voting_rights_percentage', 'dividend_rights_percentage', 'is_active',
            'is_transferable', 'is_redeemable', 'redemption_price',
            'certificate_number', 'certificate_file', 'notes'
        ]
        widgets = {
            'acquisition_date': forms.DateInput(attrs={'type': 'date'}),
            'vesting_start_date': forms.DateInput(attrs={'type': 'date'}),
            'vesting_end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Share Details',
                Row(
                    Column('share_type', css_class='col-md-4'),
                    Column('share_class', css_class='col-md-4'),
                    Column('number_of_shares', css_class='col-md-4'),
                ),
                Row(
                    Column('par_value', css_class='col-md-12'),
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
                'Vesting Schedule',
                Row(
                    Column('vesting_schedule', css_class='col-md-12'),
                ),
                Row(
                    Column('vesting_start_date', css_class='col-md-6'),
                    Column('vesting_end_date', css_class='col-md-6'),
                )
            ),
            Fieldset(
                'Rights & Terms',
                Row(
                    Column('voting_rights_percentage', css_class='col-md-6'),
                    Column('dividend_rights_percentage', css_class='col-md-6'),
                ),
                Row(
                    Column('is_active', css_class='col-md-4'),
                    Column('is_transferable', css_class='col-md-4'),
                    Column('is_redeemable', css_class='col-md-4'),
                ),
                Row(
                    Column('redemption_price', css_class='col-md-12'),
                )
            ),
            Fieldset(
                'Certification & Documentation',
                Row(
                    Column('certificate_number', css_class='col-md-6'),
                    Column('certificate_file', css_class='col-md-6'),
                ),
                Row(
                    Column('notes', css_class='col-md-12'),
                )
            ),
        )
