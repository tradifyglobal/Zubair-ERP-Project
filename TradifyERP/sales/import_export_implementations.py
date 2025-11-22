"""
Import/Export implementations for Sales module models.
"""

from sales.models import Customer, SalesOrder, Product
from accounting.import_export_utils import BaseImporter, BaseExporter
from accounting.models import Entity


# =====================
# CUSTOMER IMPORT/EXPORT (Sales specific)
# =====================

class SalesCustomerImporter(BaseImporter):
    """Importer for Sales Customer model"""
    
    model_class = Customer
    required_fields = ['customer_code', 'customer_name', 'entity']
    optional_fields = [
        'customer_type', 'email', 'phone', 'website',
        'billing_address', 'shipping_address', 'city',
        'state', 'postal_code', 'country', 'credit_limit',
        'tax_id', 'is_tax_exempt', 'status', 'notes'
    ]
    unique_fields = ['customer_code']
    
    def clean_row_data(self, row_data):
        """Clean and validate customer data"""
        cleaned_data = super().clean_row_data(row_data)
        
        # Handle entity - assume it's the entity code
        if 'entity' in cleaned_data and cleaned_data['entity']:
            try:
                entity = Entity.objects.get(entity_code=cleaned_data['entity'])
                cleaned_data['entity'] = entity
            except Entity.DoesNotExist:
                # Try to get the first entity as fallback
                try:
                    entity = Entity.objects.first()
                    cleaned_data['entity'] = entity
                    self.warnings.append(f"Entity {row_data['entity']} not found, using {entity.entity_code}")
                except:
                    raise ValueError(f"No entity found in system")
        
        # Convert credit_limit to decimal
        if 'credit_limit' in cleaned_data and cleaned_data['credit_limit']:
            try:
                cleaned_data['credit_limit'] = float(cleaned_data['credit_limit'])
            except (ValueError, TypeError):
                self.warnings.append(f"Invalid credit limit value, using 0")
                cleaned_data['credit_limit'] = 0
        
        # Convert boolean fields
        if 'is_tax_exempt' in cleaned_data:
            value = str(cleaned_data.get('is_tax_exempt', 'False'))
            cleaned_data['is_tax_exempt'] = value.lower() in ('true', '1', 'yes', 't')
        
        # Set created_by if creating new record
        if not self.check_duplicate(cleaned_data):
            cleaned_data['created_by'] = self.user
        
        return cleaned_data


class SalesCustomerExporter(BaseExporter):
    """Exporter for Sales Customer model"""
    
    model_class = Customer
    export_fields = [
        'customer_code', 'customer_name', 'customer_type',
        'email', 'phone', 'website',
        'billing_address', 'shipping_address',
        'city', 'state', 'postal_code', 'country',
        'credit_limit', 'tax_id', 'is_tax_exempt',
        'status', 'created_at'
    ]
    export_headers = {
        'customer_code': 'Customer Code',
        'customer_name': 'Customer Name',
        'customer_type': 'Type',
        'email': 'Email',
        'phone': 'Phone',
        'website': 'Website',
        'billing_address': 'Billing Address',
        'shipping_address': 'Shipping Address',
        'city': 'City',
        'state': 'State',
        'postal_code': 'Postal Code',
        'country': 'Country',
        'credit_limit': 'Credit Limit',
        'tax_id': 'Tax ID',
        'is_tax_exempt': 'Tax Exempt',
        'status': 'Status',
        'created_at': 'Created Date'
    }


# =========================
# SALES ORDER EXPORT (Export only - too complex for import)
# =========================

class SalesOrderExporter(BaseExporter):
    """Exporter for Sales Order model (Export only)"""
    
    model_class = SalesOrder
    export_fields = [
        'order_number', 'order_date',
        'customer__customer_code', 'customer__customer_name',
        'status', 'payment_status',
        'subtotal', 'tax_amount', 'total_amount',
        'created_by__username', 'created_at'
    ]
    export_headers = {
        'order_number': 'Order Number',
        'order_date': 'Order Date',
        'customer__customer_code': 'Customer Code',
        'customer__customer_name': 'Customer Name',
        'status': 'Order Status',
        'payment_status': 'Payment Status',
        'subtotal': 'Subtotal',
        'tax_amount': 'Tax',
        'total_amount': 'Total',
        'created_by__username': 'Created By',
        'created_at': 'Created Date'
    }


# =====================
# PRODUCT IMPORT/EXPORT
# =====================

class ProductImporter(BaseImporter):
    """Importer for Product model"""
    
    model_class = Product
    required_fields = ['product_code', 'product_name', 'entity']
    optional_fields = [
        'description', 'category', 'unit_of_measure',
        'unit_price', 'cost_price', 'stock_quantity',
        'reorder_level', 'is_active'
    ]
    unique_fields = ['product_code']
    
    def clean_row_data(self, row_data):
        """Clean and validate product data"""
        cleaned_data = super().clean_row_data(row_data)
        
        # Handle entity
        if 'entity' in cleaned_data and cleaned_data['entity']:
            try:
                entity = Entity.objects.get(entity_code=cleaned_data['entity'])
                cleaned_data['entity'] = entity
            except Entity.DoesNotExist:
                entity = Entity.objects.first()
                cleaned_data['entity'] = entity
                self.warnings.append(f"Entity not found, using {entity.entity_code}")
        
        # Convert numeric fields
        numeric_fields = ['unit_price', 'cost_price', 'stock_quantity', 'reorder_level']
        for field in numeric_fields:
            if field in cleaned_data and cleaned_data[field]:
                try:
                    cleaned_data[field] = float(cleaned_data[field])
                except (ValueError, TypeError):
                    self.warnings.append(f"Invalid {field} value, using 0")
                    cleaned_data[field] = 0
        
        # Convert is_active
        if 'is_active' in cleaned_data:
            value = str(cleaned_data.get('is_active', 'True'))
            cleaned_data['is_active'] = value.lower() in ('true', '1', 'yes', 't')
        
        # Set created_by
        if not self.check_duplicate(cleaned_data):
            cleaned_data['created_by'] = self.user
        
        return cleaned_data


class ProductExporter(BaseExporter):
    """Exporter for Product model"""
    
    model_class = Product
    export_fields = [
        'product_code', 'product_name', 'description',
        'category', 'unit_of_measure',
        'unit_price', 'cost_price',
        'stock_quantity', 'reorder_level',
        'is_active', 'created_at'
    ]
    export_headers = {
        'product_code': 'Product Code',
        'product_name': 'Product Name',
        'description': 'Description',
        'category': 'Category',
        'unit_of_measure': 'Unit',
        'unit_price': 'Unit Price',
        'cost_price': 'Cost Price',
        'stock_quantity': 'Stock Qty',
        'reorder_level': 'Reorder Level',
        'is_active': 'Active',
        'created_at': 'Created Date'
    }
