"""
Generic Import/Export Views for TradifyERP
Provides reusable class-based views for handling import and export operations.
"""

from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django import forms

from .import_export_utils import (
    BaseImporter, BaseExporter, ImportExportException,
    get_import_template_response
)
from .module_permissions import ModulePermission


class ImportUploadForm(forms.Form):
    """Form for uploading import files"""
    
    file = forms.FileField(
        label='Select File',
        help_text='Upload CSV or Excel file (.csv, .xlsx, .xls)',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx,.xls'
        })
    )
    
    update_existing = forms.BooleanField(
        label='Update Existing Records',
        required=False,
        initial=False,
        help_text='If checked, existing records will be updated. Otherwise, duplicates will be skipped.',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class BaseImportView(LoginRequiredMixin, FormView):
    """
    Base view for importing data.
    
    Usage:
        class CustomerImportView(BaseImportView):
            importer_class = CustomerImporter
            module_name = 'sales'
            template_name = 'sales/customer_import.html'
            success_url = reverse_lazy('sales:customer-list')
    """
    
    form_class = ImportUploadForm
    template_name = 'accounting/generic_import.html'
    importer_class = None
    module_name = None
    success_url = None
    
    def dispatch(self, request, *args, **kwargs):
        """Check if user has permission to import"""
        if not self.module_name:
            raise NotImplementedError("module_name must be defined")
        
        if not ModulePermission.user_can_perform_action(request.user, self.module_name, 'add'):
            messages.error(request, "You don't have permission to import data to this module.")
            return redirect(self.get_success_url())
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_importer(self):
        """Get importer instance"""
        if not self.importer_class:
            raise NotImplementedError("importer_class must be defined")
        return self.importer_class(self.request.user, self.module_name)
    
    def form_valid(self, form):
        """Process the uploaded file"""
        file = form.cleaned_data['file']
        update_existing = form.cleaned_data['update_existing']
        
        try:
            importer = self.get_importer()
            result = importer.import_data(file, update_existing=update_existing)
            
            if result['success']:
                messages.success(
                    self.request,
                    f"Import completed successfully! "
                    f"Created: {result['created']}, "
                    f"Updated: {result['updated']}, "
                    f"Skipped: {result['skipped']}"
                )
            else:
                messages.warning(
                    self.request,
                    f"Import completed with errors. "
                    f"Created: {result['created']}, "
                    f"Updated: {result['updated']}, "
                    f"Skipped: {result['skipped']}"
                )
                
                # Show first few errors
                for error in result['errors'][:5]:
                    messages.error(self.request, error)
                
                if len(result['errors']) > 5:
                    messages.error(
                        self.request,
                        f"... and {len(result['errors']) - 5} more errors"
                    )
            
            # Store result in session for result page
            self.request.session['import_result'] = result
            
        except ImportExportException as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"Unexpected error: {str(e)}")
            return self.form_invalid(form)
        
        return redirect(self.get_success_url())
    
    def get_context_data(self, **kwargs):
        """Add additional context"""
        context = super().get_context_data(**kwargs)
        context['module_name'] = self.module_name
        context['can_import'] = True  # Already checked in dispatch
        return context


class BaseExportView(LoginRequiredMixin, TemplateView):
    """
    Base view for exporting data.
    
    Usage:
        class CustomerExportView(BaseExportView):
            exporter_class = CustomerExporter
            module_name = 'sales'
    """
    
    exporter_class = None
    module_name = None
    export_format = 'csv'  # Default format: csv, excel, json
    
    def dispatch(self, request, *args, **kwargs):
        """Check if user has permission to export"""
        if not self.module_name:
            raise NotImplementedError("module_name must be defined")
        
        if not ModulePermission.user_can_perform_action(request.user, self.module_name, 'export'):
            messages.error(request, "You don't have permission to export data from this module.")
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_exporter(self):
        """Get exporter instance"""
        if not self.exporter_class:
            raise NotImplementedError("exporter_class must be defined")
        return self.exporter_class(self.request.user, self.module_name)
    
    def get_export_format(self):
        """Get export format from request or default"""
        return self.request.GET.get('format', self.export_format)
    
    def get_filters(self):
        """
        Get filters from request.
        Override this method to implement custom filtering.
        """
        filters = {}
        # Example: if 'status' in self.request.GET:
        #     filters['status'] = self.request.GET['status']
        return filters
    
    def get(self, request, *args, **kwargs):
        """Handle GET request and export data"""
        try:
            exporter = self.get_exporter()
            filters = self.get_filters()
            queryset = exporter.get_queryset(filters)
            
            export_format = self.get_export_format()
            
            if export_format == 'excel' or export_format == 'xlsx':
                return exporter.export_excel(queryset)
            elif export_format == 'json':
                return exporter.export_json(queryset)
            else:  # Default to CSV
                return exporter.export_csv(queryset)
                
        except ImportExportException as e:
            messages.error(request, str(e))
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            messages.error(request, f"Export error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)


class ImportTemplateDownloadView(LoginRequiredMixin, TemplateView):
    """
    View for downloading import templates.
    
    Usage:
        class CustomerImportTemplateView(ImportTemplateDownloadView):
            model_class = Customer
            template_fields = ['name', 'email', 'phone', 'address']
            module_name = 'sales'
    """
    
    model_class = None
    template_fields = []
    module_name = None
    
    def dispatch(self, request, *args, **kwargs):
        """Check if user has permission"""
        if not self.module_name:
            raise NotImplementedError("module_name must be defined")
        
        if not ModulePermission.user_can_perform_action(request.user, self.module_name, 'add'):
            messages.error(request, "You don't have permission to access import templates.")
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        """Generate and return template file"""
        if not self.model_class:
            raise NotImplementedError("model_class must be defined")
        
        if not self.template_fields:
            raise NotImplementedError("template_fields must be defined")
        
        return get_import_template_response(
            self.model_class,
            self.template_fields
        )


class ImportExportDashboardView(LoginRequiredMixin, TemplateView):
    """
    Dashboard view showing available import/export options for a module.
    """
    
    template_name = 'accounting/import_export_dashboard.html'
    module_name = None
    available_models = []  # List of dicts with model info
    
    def get_context_data(self, **kwargs):
        """Add context data"""
        context = super().get_context_data(**kwargs)
        
        can_import = ModulePermission.user_can_perform_action(
            self.request.user, self.module_name, 'add'
        )
        
        can_export = ModulePermission.user_can_perform_action(
            self.request.user, self.module_name, 'export'
        )
        
        context.update({
            'module_name': self.module_name,
            'can_import': can_import,
            'can_export': can_export,
            'available_models': self.available_models,
        })
        
        return context


# AJAX view for quick export
class QuickExportView(LoginRequiredMixin, TemplateView):
    """
    Quick export view that returns JSON response with download URL.
    Useful for AJAX export requests.
    """
    
    exporter_class = None
    module_name = None
    
    def post(self, request, *args, **kwargs):
        """Handle POST request for export"""
        
        if not ModulePermission.user_can_perform_action(request.user, self.module_name, 'export'):
            return JsonResponse({
                'success': False,
                'error': 'Permission denied'
            }, status=403)
        
        try:
            export_format = request.POST.get('format', 'csv')
            
            exporter = self.exporter_class(request.user, self.module_name)
            queryset = exporter.get_queryset()
            
            if export_format == 'excel':
                response = exporter.export_excel(queryset)
            elif export_format == 'json':
                response = exporter.export_json(queryset)
            else:
                response = exporter.export_csv(queryset)
            
            return response
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
