"""
Import/Export implementations for Accounting module models.
"""

from accounting.models import (
    Account, Customer, Vendor, LedgerEntry
)
from accounting.import_export_utils import BaseImporter, BaseExporter


# =====================
# ACCOUNT IMPORT/EXPORT
# =====================

class AccountImporter(BaseImporter):
    """Importer for Account model"""
    
    model_class = Account
    required_fields = ['account_number', 'account_name', 'account_type']
    optional_fields = ['description', 'parent_account', 'is_active']
    unique_fields = ['account_number']
    
    def clean_row_data(self, row_data):
        """Clean and validate account data"""
        cleaned_data = super().clean_row_data(row_data)
        
        # Handle parent account
        if 'parent_account' in cleaned_data and cleaned_data['parent_account']:
            try:
                parent_account_num = cleaned_data['parent_account']
                parent = Account.objects.get(account_number=parent_account_num)
                cleaned_data['parent_account'] = parent
            except Account.DoesNotExist:
                self.warnings.append(f"Parent account {parent_account_num} not found, skipping parent")
                cleaned_data.pop('parent_account', None)
        
        # Convert is_active string to boolean
        if 'is_active' in cleaned_data:
            is_active = cleaned_data.get('is_active', 'True')
            if isinstance(is_active, str):
                cleaned_data['is_active'] = is_active.lower() in ('true', '1', 'yes', 't')
        
        return cleaned_data


class AccountExporter(BaseExporter):
    """Exporter for Account model"""
    
    model_class = Account
    export_fields = [
        'account_number', 'account_name', 'account_type',
        'description', 'parent_account__account_number',
        'is_active', 'created_at', 'updated_at'
    ]
    export_headers = {
        'account_number': 'Account Number',
        'account_name': 'Account Name',
        'account_type': 'Type',
        'description': 'Description',
        'parent_account__account_number': 'Parent Account',
        'is_active': 'Active',
        'created_at': 'Created Date',
        'updated_at': 'Last Updated'
    }


# =======================
# CUSTOMER IMPORT/EXPORT
# =======================

class CustomerImporter(BaseImporter):
    """Importer for Customer model"""
    
    model_class = Customer
    required_fields = ['name', 'email']
    optional_fields = [
        'phone', 'address', 'city', 'state', 'country',
        'postal_code', 'tax_id', 'credit_limit', 'is_active'
    ]
    unique_fields = ['email']
    
    def clean_row_data(self, row_data):
        """Clean and validate customer data"""
        cleaned_data = super().clean_row_data(row_data)
        
        # Convert credit_limit to decimal
        if 'credit_limit' in cleaned_data and cleaned_data['credit_limit']:
            try:
                cleaned_data['credit_limit'] = float(cleaned_data['credit_limit'])
            except (ValueError, TypeError):
                self.warnings.append(f"Invalid credit limit value, using default")
                cleaned_data.pop('credit_limit', None)
        
        # Convert is_active
        if 'is_active' in cleaned_data:
            is_active = cleaned_data.get('is_active', 'True')
            if isinstance(is_active, str):
                cleaned_data['is_active'] = is_active.lower() in ('true', '1', 'yes', 't')
        
        return cleaned_data


class CustomerExporter(BaseExporter):
    """Exporter for Customer model"""
    
    model_class = Customer
    export_fields = [
        'customer_code', 'name', 'email', 'phone', 'address', 'city',
        'state', 'country', 'postal_code', 'tax_id',
        'credit_limit', 'is_active', 'created_at'
    ]
    export_headers = {
        'customer_code': 'Customer Code',
        'name': 'Customer Name',
        'email': 'Email',
        'phone': 'Phone',
        'address': 'Address',
        'city': 'City',
        'state': 'State',
        'country': 'Country',
        'postal_code': 'Postal Code',
        'tax_id': 'Tax ID',
        'credit_limit': 'Credit Limit',
        'is_active': 'Active',
        'created_at': 'Created Date'
    }


# =====================
# VENDOR IMPORT/EXPORT
# =====================

class VendorImporter(BaseImporter):
    """Importer for Vendor model"""
    
    model_class = Vendor
    required_fields = ['name', 'email']
    optional_fields = [
        'phone', 'address', 'city', 'state', 'country',
        'postal_code', 'tax_id', 'payment_terms', 'is_active'
    ]
    unique_fields = ['email']
    
    def clean_row_data(self, row_data):
        """Clean and validate vendor data"""
        cleaned_data = super().clean_row_data(row_data)
        
        # Convert is_active
        if 'is_active' in cleaned_data:
            is_active = cleaned_data.get('is_active', 'True')
            if isinstance(is_active, str):
                cleaned_data['is_active'] = is_active.lower() in ('true', '1', 'yes', 't')
        
        return cleaned_data


class VendorExporter(BaseExporter):
    """Exporter for Vendor model"""
    
    model_class = Vendor
    export_fields = [
        'name', 'email', 'phone', 'address', 'city',
        'state', 'country', 'postal_code', 'tax_id',
        'payment_terms', 'is_active', 'created_at'
    ]
    export_headers = {
        'name': 'Vendor Name',
        'email': 'Email',
        'phone': 'Phone',
        'address': 'Address',
        'city': 'City',
        'state': 'State',
        'country': 'Country',
        'postal_code': 'Postal Code',
        'tax_id': 'Tax ID',
        'payment_terms': 'Payment Terms',
        'is_active': 'Active',
        'created_at': 'Created Date'
    }


# ===========================
# LEDGER ENTRY IMPORT/EXPORT
# ===========================

class LedgerEntryExporter(BaseExporter):
    """Exporter for Ledger Entry model (Export only)"""
    
    model_class = LedgerEntry
    export_fields = [
        'entry_date',
        'account__account_number', 'account__account_name',
        'debit_amount', 'credit_amount', 'description',
        'created_at'
    ]
    export_headers = {
        'entry_date': 'Entry Date',
        'account__account_number': 'Account Number',
        'account__account_name': 'Account Name',
        'debit_amount': 'Debit',
        'credit_amount': 'Credit',
        'description': 'Description',
        'created_at': 'Created Date'
    }
