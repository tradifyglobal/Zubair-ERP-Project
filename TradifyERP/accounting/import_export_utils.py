"""
Import/Export Utilities for TradifyERP
Provides base classes and utilities for importing and exporting data across all modules.
Includes permission checking based on ModulePermission.
"""

import csv
import io
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Type

from django.db import models, transaction
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

from .module_permissions import ModulePermission


class ImportExportException(Exception):
    """Custom exception for import/export operations"""
    pass


class BaseImporter:
    """
    Base class for importing data from CSV or Excel files.
    Handles validation, duplicate detection, and bulk creation.
    """
    
    model_class: Type[models.Model] = None
    required_fields: List[str] = []
    optional_fields: List[str] = []
    unique_fields: List[str] = []  # Fields used to detect duplicates
    
    def __init__(self, user: User, module_name: str):
        self.user = user
        self.module_name = module_name
        self.errors = []
        self.warnings = []
        self.created_count = 0
        self.updated_count = 0
        self.skipped_count = 0
        
        if not self.model_class:
            raise NotImplementedError("model_class must be defined")
    
    def check_permission(self) -> bool:
        """Check if user has permission to import data"""
        return ModulePermission.user_can_perform_action(
            self.user, self.module_name, 'add'
        )
    
    def validate_headers(self, headers: List[str]) -> bool:
        """Validate that all required fields are present in headers"""
        missing_fields = set(self.required_fields) - set(headers)
        if missing_fields:
            self.errors.append(f"Missing required fields: {', '.join(missing_fields)}")
            return False
        return True
    
    def parse_csv(self, file) -> List[Dict[str, Any]]:
        """Parse CSV file and return list of dictionaries"""
        try:
            decoded_file = file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            return list(reader)
        except Exception as e:
            raise ImportExportException(f"Error parsing CSV: {str(e)}")
    
    def parse_excel(self, file) -> List[Dict[str, Any]]:
        """Parse Excel file and return list of dictionaries"""
        if not EXCEL_AVAILABLE:
            raise ImportExportException("openpyxl is not installed. Please install it to import Excel files.")
        
        try:
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active
            
            headers = [cell.value for cell in sheet[1]]
            data = []
            
            for row in sheet.iter_rows(min_row=2, values_only=True):
                row_data = dict(zip(headers, row))
                # Skip empty rows
                if any(row_data.values()):
                    data.append(row_data)
            
            return data
        except Exception as e:
            raise ImportExportException(f"Error parsing Excel: {str(e)}")
    
    def parse_file(self, file) -> List[Dict[str, Any]]:
        """Parse file based on extension"""
        filename = file.name.lower()
        
        if filename.endswith('.csv'):
            return self.parse_csv(file)
        elif filename.endswith(('.xlsx', '.xls')):
            return self.parse_excel(file)
        else:
            raise ImportExportException("Unsupported file format. Please upload CSV or Excel file.")
    
    def clean_row_data(self, row_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and validate row data.
        Override this method to implement custom cleaning logic.
        """
        cleaned_data = {}
        
        for field in self.required_fields + self.optional_fields:
            value = row_data.get(field)
            
            # Skip None or empty string values for optional fields
            if field in self.optional_fields and (value is None or value == ''):
                continue
            
            cleaned_data[field] = value
        
        return cleaned_data
    
    def get_or_create_related_object(self, model_class, field_name, value):
        """
        Helper method to get or create related objects.
        Override this to handle specific related objects.
        """
        return None
    
    def check_duplicate(self, cleaned_data: Dict[str, Any]) -> Optional[models.Model]:
        """Check if record already exists based on unique_fields"""
        if not self.unique_fields:
            return None
        
        filter_kwargs = {
            field: cleaned_data.get(field)
            for field in self.unique_fields
            if field in cleaned_data
        }
        
        if not filter_kwargs:
            return None
        
        try:
            return self.model_class.objects.get(**filter_kwargs)
        except self.model_class.DoesNotExist:
            return None
        except self.model_class.MultipleObjectsReturned:
            self.warnings.append(f"Multiple records found for {filter_kwargs}")
            return None
    
    def create_object(self, cleaned_data: Dict[str, Any]) -> models.Model:
        """Create a model instance from cleaned data"""
        return self.model_class.objects.create(**cleaned_data)
    
    def update_object(self, obj: models.Model, cleaned_data: Dict[str, Any]) -> models.Model:
        """Update an existing model instance"""
        for field, value in cleaned_data.items():
            setattr(obj, field, value)
        obj.save()
        return obj
    
    @transaction.atomic
    def import_data(self, file, update_existing: bool = False) -> Dict[str, Any]:
        """
        Main import method. Parses file and creates/updates records.
        
        Args:
            file: Uploaded file object
            update_existing: If True, update existing records; if False, skip duplicates
        
        Returns:
            Dictionary with import results
        """
        if not self.check_permission():
            raise ImportExportException("You don't have permission to import data to this module")
        
        # Parse file
        try:
            data = self.parse_file(file)
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'created': 0,
                'updated': 0,
                'skipped': 0,
                'errors': self.errors
            }
        
        if not data:
            return {
                'success': False,
                'error': 'No data found in file',
                'created': 0,
                'updated': 0,
                'skipped': 0,
                'errors': self.errors
            }
        
        # Validate headers
        headers = list(data[0].keys())
        if not self.validate_headers(headers):
            return {
                'success': False,
                'error': 'Invalid headers',
                'created': 0,
                'updated': 0,
                'skipped': 0,
                'errors': self.errors
            }
        
        # Process each row
        for idx, row_data in enumerate(data, start=2):  # Start at 2 (1 is header)
            try:
                # Clean data
                cleaned_data = self.clean_row_data(row_data)
                
                # Check for duplicates
                existing_obj = self.check_duplicate(cleaned_data)
                
                if existing_obj:
                    if update_existing:
                        self.update_object(existing_obj, cleaned_data)
                        self.updated_count += 1
                    else:
                        self.skipped_count += 1
                        self.warnings.append(f"Row {idx}: Duplicate record skipped")
                else:
                    # Create new record
                    self.create_object(cleaned_data)
                    self.created_count += 1
                    
            except ValidationError as e:
                self.errors.append(f"Row {idx}: Validation error - {str(e)}")
            except Exception as e:
                self.errors.append(f"Row {idx}: Error - {str(e)}")
        
        return {
            'success': len(self.errors) == 0,
            'created': self.created_count,
            'updated': self.updated_count,
            'skipped': self.skipped_count,
            'errors': self.errors,
            'warnings': self.warnings,
            'total_rows': len(data)
        }


class BaseExporter:
    """
    Base class for exporting data to CSV or Excel files.
    Handles field selection, filtering, and formatting.
    """
    
    model_class: Type[models.Model] = None
    export_fields: List[str] = []  # Fields to export
    export_headers: Dict[str, str] = {}  # Custom headers for fields
    
    def __init__(self, user: User, module_name: str):
        self.user = user
        self.module_name = module_name
        
        if not self.model_class:
            raise NotImplementedError("model_class must be defined")
    
    def check_permission(self) -> bool:
        """Check if user has permission to export data"""
        return ModulePermission.user_can_perform_action(
            self.user, self.module_name, 'export'
        )
    
    def get_queryset(self, filters: Optional[Dict[str, Any]] = None):
        """
        Get queryset for export. Apply filters if provided.
        Override this method to implement custom filtering.
        """
        queryset = self.model_class.objects.all()
        
        if filters:
            queryset = queryset.filter(**filters)
        
        return queryset
    
    def get_field_value(self, obj: models.Model, field: str) -> Any:
        """
        Get field value from object. Handle related fields and custom formatting.
        Override this method to implement custom field value extraction.
        """
        try:
            # Handle foreign keys and related objects
            if '__' in field:
                parts = field.split('__')
                value = obj
                for part in parts:
                    value = getattr(value, part, '')
                    if value is None:
                        return ''
                return value
            
            value = getattr(obj, field, '')
            
            # Format dates
            if isinstance(value, datetime):
                return value.strftime('%Y-%m-%d %H:%M:%S')
            
            # Handle None values
            if value is None:
                return ''
            
            return value
        except Exception:
            return ''
    
    def get_headers(self) -> List[str]:
        """Get export headers"""
        headers = []
        for field in self.export_fields:
            header = self.export_headers.get(field, field.replace('_', ' ').title())
            headers.append(header)
        return headers
    
    def export_csv(self, queryset, filename: str = None) -> HttpResponse:
        """Export queryset to CSV file"""
        if not self.check_permission():
            raise ImportExportException("You don't have permission to export data from this module")
        
        if filename is None:
            filename = f"{self.model_class._meta.verbose_name_plural}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        
        # Write headers
        writer.writerow(self.get_headers())
        
        # Write data rows
        for obj in queryset:
            row = [self.get_field_value(obj, field) for field in self.export_fields]
            writer.writerow(row)
        
        return response
    
    def export_excel(self, queryset, filename: str = None) -> HttpResponse:
        """Export queryset to Excel file"""
        if not EXCEL_AVAILABLE:
            raise ImportExportException("openpyxl is not installed. Please install it to export Excel files.")
        
        if not self.check_permission():
            raise ImportExportException("You don't have permission to export data from this module")
        
        if filename is None:
            filename = f"{self.model_class._meta.verbose_name_plural}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Create workbook
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = self.model_class._meta.verbose_name_plural[:31]  # Excel limit
        
        # Header styling
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        # Write headers
        headers = self.get_headers()
        for col_num, header in enumerate(headers, 1):
            cell = sheet.cell(row=1, column=col_num)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # Write data rows
        for row_num, obj in enumerate(queryset, 2):
            for col_num, field in enumerate(self.export_fields, 1):
                value = self.get_field_value(obj, field)
                sheet.cell(row=row_num, column=col_num).value = value
        
        # Auto-adjust column widths
        for column in sheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            sheet.column_dimensions[column_letter].width = adjusted_width
        
        # Save to response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        workbook.save(response)
        
        return response
    
    def export_json(self, queryset, filename: str = None) -> HttpResponse:
        """Export queryset to JSON file"""
        if not self.check_permission():
            raise ImportExportException("You don't have permission to export data from this module")
        
        if filename is None:
            filename = f"{self.model_class._meta.verbose_name_plural}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert queryset to list of dictionaries
        data = []
        for obj in queryset:
            obj_data = {}
            for field in self.export_fields:
                obj_data[field] = self.get_field_value(obj, field)
            data.append(obj_data)
        
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(json.dumps(data, indent=2, default=str))
        
        return response


class ImportExportMixin:
    """
    Mixin for views that need import/export functionality.
    Provides helper methods for checking permissions and handling requests.
    """
    
    importer_class = None
    exporter_class = None
    module_name = None
    
    def get_importer(self):
        """Get importer instance"""
        if not self.importer_class:
            raise NotImplementedError("importer_class must be defined")
        return self.importer_class(self.request.user, self.module_name)
    
    def get_exporter(self):
        """Get exporter instance"""
        if not self.exporter_class:
            raise NotImplementedError("exporter_class must be defined")
        return self.exporter_class(self.request.user, self.module_name)
    
    def can_import(self):
        """Check if user can import"""
        return ModulePermission.user_can_perform_action(
            self.request.user, self.module_name, 'add'
        )
    
    def can_export(self):
        """Check if user can export"""
        return ModulePermission.user_can_perform_action(
            self.request.user, self.module_name, 'export'
        )


def get_import_template_response(model_class, fields: List[str], filename: str = None) -> HttpResponse:
    """
    Generate a CSV template file for importing data.
    
    Args:
        model_class: The model class
        fields: List of field names to include in template
        filename: Optional filename
    
    Returns:
        HttpResponse with CSV template
    """
    if filename is None:
        filename = f"{model_class._meta.verbose_name_plural}_import_template.csv"
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    
    # Write headers
    headers = [field.replace('_', ' ').title() for field in fields]
    writer.writerow(fields)  # Write field names as headers
    
    # Write example row with field types/hints
    example_row = []
    for field_name in fields:
        try:
            field = model_class._meta.get_field(field_name)
            if isinstance(field, models.CharField):
                example_row.append('Text value')
            elif isinstance(field, models.IntegerField):
                example_row.append('123')
            elif isinstance(field, models.DecimalField):
                example_row.append('123.45')
            elif isinstance(field, models.DateField):
                example_row.append('2025-01-01')
            elif isinstance(field, models.DateTimeField):
                example_row.append('2025-01-01 12:00:00')
            elif isinstance(field, models.BooleanField):
                example_row.append('True/False')
            elif isinstance(field, models.ForeignKey):
                example_row.append('Related ID or Name')
            else:
                example_row.append('')
        except:
            example_row.append('')
    
    writer.writerow(example_row)
    
    return response
