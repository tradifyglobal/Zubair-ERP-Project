from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from .models import (
    MaintenanceAsset, MaintenanceTask, WorkOrder, SparePart,
    MaintenanceVendor, VendorContract, ComplianceStandard,
    ComplianceAudit, MaintenanceCost, DowntimeRecord, WorkOrderSparePart
)
from .forms import (
    MaintenanceAssetForm, MaintenanceTaskForm, WorkOrderForm, SparePartForm,
    MaintenanceVendorForm, VendorContractForm, ComplianceStandardForm,
    MaintenanceCostForm, DowntimeRecordForm
)


# ============================================================================
# MAINTENANCE ASSET VIEWS
# ============================================================================

class MaintenanceAssetListView(LoginRequiredMixin, ListView):
    """Display list of maintenance assets."""
    model = MaintenanceAsset
    template_name = 'maintenance/maintenanceasset_list.html'
    context_object_name = 'assets'
    paginate_by = 20

    def get_queryset(self):
        queryset = MaintenanceAsset.objects.all().order_by('-created_at')
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(asset_code__icontains=search_query) |
                Q(asset_name__icontains=search_query) |
                Q(location__icontains=search_query)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class MaintenanceAssetDetailView(LoginRequiredMixin, DetailView):
    """Display maintenance asset details."""
    model = MaintenanceAsset
    template_name = 'maintenance/maintenanceasset_detail.html'
    context_object_name = 'asset'

    def get_queryset(self):
        return MaintenanceAsset.objects.all()


class MaintenanceAssetCreateView(LoginRequiredMixin, CreateView):
    """Create a new maintenance asset."""
    model = MaintenanceAsset
    form_class = MaintenanceAssetForm
    template_name = 'maintenance/maintenanceasset_form.html'
    success_url = reverse_lazy('maintenance:asset-list')

    def form_valid(self, form):
        messages.success(self.request, 'Asset created successfully!')
        return super().form_valid(form)


class MaintenanceAssetUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing maintenance asset."""
    model = MaintenanceAsset
    form_class = MaintenanceAssetForm
    template_name = 'maintenance/maintenanceasset_form.html'
    success_url = reverse_lazy('maintenance:asset-list')

    def get_queryset(self):
        return MaintenanceAsset.objects.all()

    def form_valid(self, form):
        messages.success(self.request, 'Asset updated successfully!')
        return super().form_valid(form)


class MaintenanceAssetDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a maintenance asset."""
    model = MaintenanceAsset
    template_name = 'maintenance/maintenanceasset_confirm_delete.html'
    success_url = reverse_lazy('maintenance:asset-list')

    def get_queryset(self):
        return MaintenanceAsset.objects.all()

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Asset deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# MAINTENANCE TASK VIEWS
# ============================================================================

class MaintenanceTaskListView(LoginRequiredMixin, ListView):
    """Display list of maintenance tasks."""
    model = MaintenanceTask
    template_name = 'maintenance/maintenancetask_list.html'
    context_object_name = 'tasks'
    paginate_by = 20

    def get_queryset(self):
        queryset = MaintenanceTask.objects.all().order_by('-created_at')
        
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(task_code__icontains=search_query) |
                Q(task_name__icontains=search_query)
            )
        
        return queryset


class MaintenanceTaskDetailView(LoginRequiredMixin, DetailView):
    """Display maintenance task details."""
    model = MaintenanceTask
    template_name = 'maintenance/maintenancetask_detail.html'
    context_object_name = 'task'

    def get_queryset(self):
        return MaintenanceTask.objects.all()


class MaintenanceTaskCreateView(LoginRequiredMixin, CreateView):
    """Create a new maintenance task."""
    model = MaintenanceTask
    form_class = MaintenanceTaskForm
    template_name = 'maintenance/maintenancetask_form.html'
    success_url = reverse_lazy('maintenance:task-list')

    def form_valid(self, form):
        messages.success(self.request, 'Task created successfully!')
        return super().form_valid(form)


class MaintenanceTaskUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing maintenance task."""
    model = MaintenanceTask
    form_class = MaintenanceTaskForm
    template_name = 'maintenance/maintenancetask_form.html'
    success_url = reverse_lazy('maintenance:task-list')

    def get_queryset(self):
        return MaintenanceTask.objects.all()

    def form_valid(self, form):
        messages.success(self.request, 'Task updated successfully!')
        return super().form_valid(form)


class MaintenanceTaskDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a maintenance task."""
    model = MaintenanceTask
    template_name = 'maintenance/maintenancetask_confirm_delete.html'
    success_url = reverse_lazy('maintenance:task-list')

    def get_queryset(self):
        return MaintenanceTask.objects.all()

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Task deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# WORK ORDER VIEWS
# ============================================================================

class WorkOrderListView(LoginRequiredMixin, ListView):
    """Display list of work orders."""
    model = WorkOrder
    template_name = 'maintenance/workorder_list.html'
    context_object_name = 'work_orders'
    paginate_by = 20

    def get_queryset(self):
        queryset = WorkOrder.objects.all().order_by('-created_at')
        
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(work_order_number__icontains=search_query) |
                Q(asset__asset_name__icontains=search_query)
            )
        
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['status_choices'] = WorkOrder._meta.get_field('status').choices
        return context


class WorkOrderDetailView(LoginRequiredMixin, DetailView):
    """Display work order details."""
    model = WorkOrder
    template_name = 'maintenance/workorder_detail.html'
    context_object_name = 'work_order'

    def get_queryset(self):
        return WorkOrder.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['spare_parts'] = self.object.spare_parts.all()
        context['costs'] = MaintenanceCost.objects.filter(work_order=self.object)
        return context


class WorkOrderCreateView(LoginRequiredMixin, CreateView):
    """Create a new work order."""
    model = WorkOrder
    form_class = WorkOrderForm
    template_name = 'maintenance/workorder_form.html'
    success_url = reverse_lazy('maintenance:workorder-list')

    def form_valid(self, form):
        messages.success(self.request, 'Work order created successfully!')
        return super().form_valid(form)


class WorkOrderUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing work order."""
    model = WorkOrder
    form_class = WorkOrderForm
    template_name = 'maintenance/workorder_form.html'
    success_url = reverse_lazy('maintenance:workorder-list')

    def get_queryset(self):
        return WorkOrder.objects.all()

    def form_valid(self, form):
        messages.success(self.request, 'Work order updated successfully!')
        return super().form_valid(form)


class WorkOrderDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a work order."""
    model = WorkOrder
    template_name = 'maintenance/workorder_confirm_delete.html'
    success_url = reverse_lazy('maintenance:workorder-list')

    def get_queryset(self):
        return WorkOrder.objects.all()

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Work order deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# SPARE PART VIEWS
# ============================================================================

class SparePartListView(LoginRequiredMixin, ListView):
    """Display list of spare parts."""
    model = SparePart
    template_name = 'maintenance/sparepart_list.html'
    context_object_name = 'spare_parts'
    paginate_by = 20

    def get_queryset(self):
        queryset = SparePart.objects.all().order_by('-created_at')
        
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(part_code__icontains=search_query) |
                Q(part_name__icontains=search_query)
            )
        
        return queryset


class SparePartDetailView(LoginRequiredMixin, DetailView):
    """Display spare part details."""
    model = SparePart
    template_name = 'maintenance/sparepart_detail.html'
    context_object_name = 'spare_part'

    def get_queryset(self):
        return SparePart.objects.all()


class SparePartCreateView(LoginRequiredMixin, CreateView):
    """Create a new spare part."""
    model = SparePart
    form_class = SparePartForm
    template_name = 'maintenance/sparepart_form.html'
    success_url = reverse_lazy('maintenance:sparepart-list')

    def form_valid(self, form):
        messages.success(self.request, 'Spare part created successfully!')
        return super().form_valid(form)


class SparePartUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing spare part."""
    model = SparePart
    form_class = SparePartForm
    template_name = 'maintenance/sparepart_form.html'
    success_url = reverse_lazy('maintenance:sparepart-list')

    def get_queryset(self):
        return SparePart.objects.all()

    def form_valid(self, form):
        messages.success(self.request, 'Spare part updated successfully!')
        return super().form_valid(form)


class SparePartDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a spare part."""
    model = SparePart
    template_name = 'maintenance/sparepart_confirm_delete.html'
    success_url = reverse_lazy('maintenance:sparepart-list')

    def get_queryset(self):
        return SparePart.objects.all()

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Spare part deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# MAINTENANCE VENDOR VIEWS
# ============================================================================

class MaintenanceVendorListView(LoginRequiredMixin, ListView):
    """Display list of maintenance vendors."""
    model = MaintenanceVendor
    template_name = 'maintenance/maintenancevendor_list.html'
    context_object_name = 'vendors'
    paginate_by = 20

    def get_queryset(self):
        queryset = MaintenanceVendor.objects.all().order_by('-created_at')
        
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(vendor_code__icontains=search_query) |
                Q(vendor_name__icontains=search_query)
            )
        
        return queryset


class MaintenanceVendorDetailView(LoginRequiredMixin, DetailView):
    """Display maintenance vendor details."""
    model = MaintenanceVendor
    template_name = 'maintenance/maintenancevendor_detail.html'
    context_object_name = 'vendor'

    def get_queryset(self):
        return MaintenanceVendor.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contracts'] = VendorContract.objects.filter(vendor=self.object)
        return context


class MaintenanceVendorCreateView(LoginRequiredMixin, CreateView):
    """Create a new maintenance vendor."""
    model = MaintenanceVendor
    form_class = MaintenanceVendorForm
    template_name = 'maintenance/maintenancevendor_form.html'
    success_url = reverse_lazy('maintenance:vendor-list')

    def form_valid(self, form):
        messages.success(self.request, 'Vendor created successfully!')
        return super().form_valid(form)


class MaintenanceVendorUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing maintenance vendor."""
    model = MaintenanceVendor
    form_class = MaintenanceVendorForm
    template_name = 'maintenance/maintenancevendor_form.html'
    success_url = reverse_lazy('maintenance:vendor-list')

    def get_queryset(self):
        return MaintenanceVendor.objects.all()

    def form_valid(self, form):
        messages.success(self.request, 'Vendor updated successfully!')
        return super().form_valid(form)


class MaintenanceVendorDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a maintenance vendor."""
    model = MaintenanceVendor
    template_name = 'maintenance/maintenancevendor_confirm_delete.html'
    success_url = reverse_lazy('maintenance:vendor-list')

    def get_queryset(self):
        return MaintenanceVendor.objects.all()

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Vendor deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# VENDOR CONTRACT VIEWS
# ============================================================================

class VendorContractListView(LoginRequiredMixin, ListView):
    """Display list of vendor contracts."""
    model = VendorContract
    template_name = 'maintenance/vendorcontract_list.html'
    context_object_name = 'contracts'
    paginate_by = 20

    def get_queryset(self):
        queryset = VendorContract.objects.all().order_by('-created_at')
        
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(contract_number__icontains=search_query) |
                Q(vendor__vendor_name__icontains=search_query)
            )
        
        return queryset


class VendorContractDetailView(LoginRequiredMixin, DetailView):
    """Display vendor contract details."""
    model = VendorContract
    template_name = 'maintenance/vendorcontract_detail.html'
    context_object_name = 'contract'

    def get_queryset(self):
        return VendorContract.objects.all()


class VendorContractCreateView(LoginRequiredMixin, CreateView):
    """Create a new vendor contract."""
    model = VendorContract
    form_class = VendorContractForm
    template_name = 'maintenance/vendorcontract_form.html'
    success_url = reverse_lazy('maintenance:contract-list')

    def form_valid(self, form):
        messages.success(self.request, 'Contract created successfully!')
        return super().form_valid(form)


class VendorContractUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing vendor contract."""
    model = VendorContract
    form_class = VendorContractForm
    template_name = 'maintenance/vendorcontract_form.html'
    success_url = reverse_lazy('maintenance:contract-list')

    def get_queryset(self):
        return VendorContract.objects.all()

    def form_valid(self, form):
        messages.success(self.request, 'Contract updated successfully!')
        return super().form_valid(form)


class VendorContractDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a vendor contract."""
    model = VendorContract
    template_name = 'maintenance/vendorcontract_confirm_delete.html'
    success_url = reverse_lazy('maintenance:contract-list')

    def get_queryset(self):
        return VendorContract.objects.all()

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Contract deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# COMPLIANCE STANDARD VIEWS
# ============================================================================

class ComplianceStandardListView(LoginRequiredMixin, ListView):
    """Display list of compliance standards."""
    model = ComplianceStandard
    template_name = 'maintenance/compliancestandard_list.html'
    context_object_name = 'standards'
    paginate_by = 20

    def get_queryset(self):
        queryset = ComplianceStandard.objects.all().order_by('-created_at')
        
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(standard_code__icontains=search_query) |
                Q(standard_name__icontains=search_query)
            )
        
        return queryset


class ComplianceStandardDetailView(LoginRequiredMixin, DetailView):
    """Display compliance standard details."""
    model = ComplianceStandard
    template_name = 'maintenance/compliancestandard_detail.html'
    context_object_name = 'standard'

    def get_queryset(self):
        return ComplianceStandard.objects.all()


class ComplianceStandardCreateView(LoginRequiredMixin, CreateView):
    """Create a new compliance standard."""
    model = ComplianceStandard
    form_class = ComplianceStandardForm
    template_name = 'maintenance/compliancestandard_form.html'
    success_url = reverse_lazy('maintenance:standard-list')

    def form_valid(self, form):
        messages.success(self.request, 'Standard created successfully!')
        return super().form_valid(form)


class ComplianceStandardUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing compliance standard."""
    model = ComplianceStandard
    form_class = ComplianceStandardForm
    template_name = 'maintenance/compliancestandard_form.html'
    success_url = reverse_lazy('maintenance:standard-list')

    def get_queryset(self):
        return ComplianceStandard.objects.all()

    def form_valid(self, form):
        messages.success(self.request, 'Standard updated successfully!')
        return super().form_valid(form)


class ComplianceStandardDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a compliance standard."""
    model = ComplianceStandard
    template_name = 'maintenance/compliancestandard_confirm_delete.html'
    success_url = reverse_lazy('maintenance:standard-list')

    def get_queryset(self):
        return ComplianceStandard.objects.all()

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Standard deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# COMPLIANCE AUDIT VIEWS
# ============================================================================

class ComplianceAuditListView(LoginRequiredMixin, ListView):
    """Display list of compliance audits."""
    model = ComplianceAudit
    template_name = 'maintenance/complianceaudit_list.html'
    context_object_name = 'audits'
    paginate_by = 20

    def get_queryset(self):
        queryset = ComplianceAudit.objects.all().order_by('-created_at')
        
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(audit_result__icontains=search_query) |
                Q(findings__icontains=search_query)
            )
        
        return queryset


class ComplianceAuditDetailView(LoginRequiredMixin, DetailView):
    """Display compliance audit details."""
    model = ComplianceAudit
    template_name = 'maintenance/complianceaudit_detail.html'
    context_object_name = 'audit'

    def get_queryset(self):
        return ComplianceAudit.objects.all()


class ComplianceAuditCreateView(LoginRequiredMixin, CreateView):
    """Create a new compliance audit."""
    model = ComplianceAudit
    form_class = MaintenanceCostForm  # Using cost form as placeholder
    template_name = 'maintenance/complianceaudit_form.html'
    success_url = reverse_lazy('maintenance:audit-list')

    def form_valid(self, form):
        messages.success(self.request, 'Audit created successfully!')
        return super().form_valid(form)


class ComplianceAuditUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing compliance audit."""
    model = ComplianceAudit
    form_class = MaintenanceCostForm  # Using cost form as placeholder
    template_name = 'maintenance/complianceaudit_form.html'
    success_url = reverse_lazy('maintenance:audit-list')

    def get_queryset(self):
        return ComplianceAudit.objects.all()

    def form_valid(self, form):
        messages.success(self.request, 'Audit updated successfully!')
        return super().form_valid(form)


class ComplianceAuditDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a compliance audit."""
    model = ComplianceAudit
    template_name = 'maintenance/complianceaudit_confirm_delete.html'
    success_url = reverse_lazy('maintenance:audit-list')

    def get_queryset(self):
        return ComplianceAudit.objects.all()

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Audit deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# MAINTENANCE COST VIEWS
# ============================================================================

class MaintenanceCostListView(LoginRequiredMixin, ListView):
    """Display list of maintenance costs."""
    model = MaintenanceCost
    template_name = 'maintenance/maintenancecost_list.html'
    context_object_name = 'costs'
    paginate_by = 20

    def get_queryset(self):
        queryset = MaintenanceCost.objects.all().order_by('-created_at')
        
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(work_order__work_order_number__icontains=search_query)
            )
        
        return queryset


class MaintenanceCostDetailView(LoginRequiredMixin, DetailView):
    """Display maintenance cost details."""
    model = MaintenanceCost
    template_name = 'maintenance/maintenancecost_detail.html'
    context_object_name = 'cost'

    def get_queryset(self):
        return MaintenanceCost.objects.all()


class MaintenanceCostCreateView(LoginRequiredMixin, CreateView):
    """Create a new maintenance cost."""
    model = MaintenanceCost
    form_class = MaintenanceCostForm
    template_name = 'maintenance/maintenancecost_form.html'
    success_url = reverse_lazy('maintenance:cost-list')

    def form_valid(self, form):
        messages.success(self.request, 'Cost recorded successfully!')
        return super().form_valid(form)


class MaintenanceCostUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing maintenance cost."""
    model = MaintenanceCost
    form_class = MaintenanceCostForm
    template_name = 'maintenance/maintenancecost_form.html'
    success_url = reverse_lazy('maintenance:cost-list')

    def get_queryset(self):
        return MaintenanceCost.objects.all()

    def form_valid(self, form):
        messages.success(self.request, 'Cost updated successfully!')
        return super().form_valid(form)


class MaintenanceCostDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a maintenance cost."""
    model = MaintenanceCost
    template_name = 'maintenance/maintenancecost_confirm_delete.html'
    success_url = reverse_lazy('maintenance:cost-list')

    def get_queryset(self):
        return MaintenanceCost.objects.all()

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Cost deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# DOWNTIME RECORD VIEWS
# ============================================================================

class DowntimeRecordListView(LoginRequiredMixin, ListView):
    """Display list of downtime records."""
    model = DowntimeRecord
    template_name = 'maintenance/downtimerecord_list.html'
    context_object_name = 'downtime_records'
    paginate_by = 20

    def get_queryset(self):
        queryset = DowntimeRecord.objects.all().order_by('-created_at')
        
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(asset__asset_name__icontains=search_query) |
                Q(reason__icontains=search_query)
            )
        
        return queryset


class DowntimeRecordDetailView(LoginRequiredMixin, DetailView):
    """Display downtime record details."""
    model = DowntimeRecord
    template_name = 'maintenance/downtimerecord_detail.html'
    context_object_name = 'downtime_record'

    def get_queryset(self):
        return DowntimeRecord.objects.all()


class DowntimeRecordCreateView(LoginRequiredMixin, CreateView):
    """Create a new downtime record."""
    model = DowntimeRecord
    form_class = DowntimeRecordForm
    template_name = 'maintenance/downtimerecord_form.html'
    success_url = reverse_lazy('maintenance:downtime-list')

    def form_valid(self, form):
        messages.success(self.request, 'Downtime record created successfully!')
        return super().form_valid(form)


class DowntimeRecordUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing downtime record."""
    model = DowntimeRecord
    form_class = DowntimeRecordForm
    template_name = 'maintenance/downtimerecord_form.html'
    success_url = reverse_lazy('maintenance:downtime-list')

    def get_queryset(self):
        return DowntimeRecord.objects.all()

    def form_valid(self, form):
        messages.success(self.request, 'Downtime record updated successfully!')
        return super().form_valid(form)


class DowntimeRecordDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a downtime record."""
    model = DowntimeRecord
    template_name = 'maintenance/downtimerecord_confirm_delete.html'
    success_url = reverse_lazy('maintenance:downtime-list')

    def get_queryset(self):
        return DowntimeRecord.objects.all()

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Downtime record deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# DASHBOARD VIEW
# ============================================================================

class MaintenanceDashboardView(LoginRequiredMixin, TemplateView):
    """Display maintenance module dashboard with key metrics."""
    template_name = 'maintenance/dashboard.html'

    def get_context_data(self, **kwargs):
        from django.db import models
        context = super().get_context_data(**kwargs)
        
        # Key metrics - show all records (not filtered by entity for now)
        context['total_assets'] = MaintenanceAsset.objects.count()
        context['active_work_orders'] = WorkOrder.objects.filter(
            status__in=['Open', 'In Progress']
        ).count()
        context['total_vendors'] = MaintenanceVendor.objects.count()
        context['total_spare_parts'] = SparePart.objects.count()
        
        # Low stock spare parts
        context['low_stock_parts'] = SparePart.objects.filter(
            current_stock__lte=models.F('reorder_level')
        )[:5]
        
        # Recent work orders
        context['recent_work_orders'] = WorkOrder.objects.order_by('-created_at')[:5]
        
        # Pending audits
        context['pending_audits'] = ComplianceAudit.objects.filter(
            audit_result__in=['Pending', 'In Progress']
        ).count()
        
        return context
