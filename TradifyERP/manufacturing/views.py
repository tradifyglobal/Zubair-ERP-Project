"""
Manufacturing Module Views
Complete CRUD operations with RBAC and multi-entity support.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from accounting.permission_utils import module_permission_required
from accounting.mixins import SessionEntityMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.db.models import Q, Sum, Count, F
from django.utils import timezone
from django.middleware.csrf import get_token
from decimal import Decimal

from accounting.models import Entity
from .models import (
    ProductCategory, Product, RawMaterial,
    BillOfMaterials, BOMLine,
    WorkCenter, Routing, RoutingLine,
    ProductionOrder, QualityInspection, Equipment,
    Distributor, DistributorContact, DistributorOrder,
    OrderShipment, AfterSalesService, WarrantyRegistration,
    DistributorPerformance
)
from .forms import (
    ProductCategoryForm, ProductForm, RawMaterialForm,
    BillOfMaterialsForm, BOMLineForm,
    WorkCenterForm, RoutingForm, RoutingLineForm,
    ProductionOrderForm, QualityInspectionForm, EquipmentForm,
    DistributorForm, DistributorContactForm, DistributorOrderForm,
    OrderShipmentForm, AfterSalesServiceForm, WarrantyRegistrationForm,
    DistributorPerformanceForm
)


# ==================== Product Category Views ====================

@method_decorator(csrf_protect, name='dispatch')
class ProductCategoryListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = ProductCategory
    template_name = 'manufacturing/productcategory_list.html'
    context_object_name = 'categories'
    paginate_by = 25
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        # Search filter
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(code__icontains=search))
        
        return qs.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(module_permission_required("manufacturing", "delete"), name='dispatch')
class ProductCategoryDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    model = ProductCategory
    template_name = 'manufacturing/productcategory_confirm_delete.html'
    success_url = reverse_lazy('manufacturing:productcategory_list')
    
    def get_queryset(self):
        return super().get_queryset()


@method_decorator(csrf_protect, name='dispatch')
class ProductCategoryCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    model = ProductCategory
    form_class = ProductCategoryForm
    template_name = 'manufacturing/productcategory_form.html'
    success_url = reverse_lazy('manufacturing:productcategory_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        entity_id = self.request.session.get('selected_entity_id')
        
        # Auto-set entity from session
        if entity_id:
            kwargs['initial'] = {'entity_id': entity_id}
        
        return kwargs
    
    def form_valid(self, form):
        entity_id = self.request.session.get("selected_entity_id")
        
        instance = form.save(commit=False)
        instance.entity_id = entity_id
        instance.save()
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


# ==================== Product Views ====================

@method_decorator(csrf_protect, name='dispatch')
class ProductListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = Product
    template_name = 'manufacturing/product_list.html'
    context_object_name = 'products'
    paginate_by = 25
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        # Search and filter
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(product_code__icontains=search) |
                Q(name__icontains=search)
            )
        
        category = self.request.GET.get('category')
        if category:
            qs = qs.filter(category_id=category)
        
        return qs.order_by('product_code')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class ProductCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'manufacturing/product_form.html'
    success_url = reverse_lazy('manufacturing:product_list')
    
    def form_valid(self, form):
        entity_id = self.request.session.get("selected_entity_id")
        # Entity set by SessionEntityMixin
        
        instance = form.save(commit=False)
        instance.entity_id = entity_id
        instance.created_by = self.request.user
        instance.save()
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class ProductUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'manufacturing/product_form.html'
    success_url = reverse_lazy('manufacturing:product_list')
    
    def get_queryset(self):
        return super().get_queryset()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(module_permission_required("manufacturing", "delete"), name='dispatch')
class ProductDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'manufacturing/product_confirm_delete.html'
    success_url = reverse_lazy('manufacturing:product_list')
    
    def get_queryset(self):
        return super().get_queryset()


# ==================== Raw Material Views ====================

@method_decorator(csrf_protect, name='dispatch')
class RawMaterialListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = RawMaterial
    template_name = 'manufacturing/rawmaterial_list.html'
    context_object_name = 'materials'
    paginate_by = 25
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(material_code__icontains=search) |
                Q(name__icontains=search)
            )
        
        # Stock status filter
        low_stock = self.request.GET.get('low_stock')
        if low_stock:
            qs = qs.filter(current_stock__lte=F('reorder_point'))
        
        return qs.order_by('material_code')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class RawMaterialCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    model = RawMaterial
    form_class = RawMaterialForm
    template_name = 'manufacturing/rawmaterial_form.html'
    success_url = reverse_lazy('manufacturing:rawmaterial_list')
    
    def form_valid(self, form):
        entity_id = self.request.session.get("selected_entity_id")
        # Entity set by SessionEntityMixin
        
        instance = form.save(commit=False)
        instance.entity_id = entity_id
        instance.save()
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(module_permission_required("manufacturing", "delete"), name='dispatch')
class RawMaterialDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    model = RawMaterial
    template_name = 'manufacturing/rawmaterial_confirm_delete.html'
    success_url = reverse_lazy('manufacturing:rawmaterial_list')
    
    def get_queryset(self):
        return super().get_queryset()


# ==================== Bill of Materials Views ====================

@method_decorator(csrf_protect, name='dispatch')
class BOMListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = BillOfMaterials
    template_name = 'manufacturing/bom_list.html'
    context_object_name = 'boms'
    paginate_by = 25
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(product__name__icontains=search) |
                Q(product__product_code__icontains=search)
            )
        
        return qs.order_by('-effective_date', '-version')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class BOMCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    model = BillOfMaterials
    form_class = BillOfMaterialsForm
    template_name = 'manufacturing/bom_form.html'
    success_url = reverse_lazy('manufacturing:bom_list')
    
    def form_valid(self, form):
        entity_id = self.request.session.get("selected_entity_id")
        # Entity set by SessionEntityMixin
        
        instance = form.save(commit=False)
        instance.entity_id = entity_id
        instance.created_by = self.request.user
        instance.save()
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class BOMUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    model = BillOfMaterials
    form_class = BillOfMaterialsForm
    template_name = 'manufacturing/bom_form.html'
    success_url = reverse_lazy('manufacturing:bom_list')
    
    def get_queryset(self):
        return super().get_queryset()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(module_permission_required("manufacturing", "delete"), name='dispatch')
class BOMDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    model = BillOfMaterials
    template_name = 'manufacturing/bom_confirm_delete.html'
    success_url = reverse_lazy('manufacturing:bom_list')
    
    def get_queryset(self):
        return super().get_queryset()


# ==================== Routing Views ====================

@method_decorator(csrf_protect, name='dispatch')
class RoutingListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = Routing
    template_name = 'manufacturing/routing_list.html'
    context_object_name = 'routings'
    paginate_by = 25
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(Q(product__product_name__icontains=search))
        
        return qs.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class RoutingCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    model = Routing
    form_class = RoutingForm
    template_name = 'manufacturing/routing_form.html'
    success_url = reverse_lazy('manufacturing:routing_list')
    
    def form_valid(self, form):
        entity_id = self.request.session.get("selected_entity_id")
        # Entity set by SessionEntityMixin
        
        instance = form.save(commit=False)
        instance.entity_id = entity_id
        instance.created_by = self.request.user
        instance.save()
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class RoutingUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    model = Routing
    form_class = RoutingForm
    template_name = 'manufacturing/routing_form.html'
    success_url = reverse_lazy('manufacturing:routing_list')
    
    def get_queryset(self):
        return super().get_queryset()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(module_permission_required("manufacturing", "delete"), name='dispatch')
class RoutingDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    model = Routing
    template_name = 'manufacturing/routing_confirm_delete.html'
    success_url = reverse_lazy('manufacturing:routing_list')
    
    def get_queryset(self):
        return super().get_queryset()


# ==================== Work Center Views ====================

@method_decorator(csrf_protect, name='dispatch')
class WorkCenterListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = WorkCenter
    template_name = 'manufacturing/workcenter_list.html'
    context_object_name = 'work_centers'
    paginate_by = 25
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(code__icontains=search) |
                Q(name__icontains=search)
            )
        
        return qs.order_by('code')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class WorkCenterCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    model = WorkCenter
    form_class = WorkCenterForm
    template_name = 'manufacturing/workcenter_form.html'
    success_url = reverse_lazy('manufacturing:workcenter_list')
    
    def form_valid(self, form):
        entity_id = self.request.session.get("selected_entity_id")
        # Entity set by SessionEntityMixin
        
        instance = form.save(commit=False)
        instance.entity_id = entity_id
        instance.save()
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class WorkCenterUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    model = WorkCenter
    form_class = WorkCenterForm
    template_name = 'manufacturing/workcenter_form.html'
    success_url = reverse_lazy('manufacturing:workcenter_list')
    
    def get_queryset(self):
        return super().get_queryset()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(module_permission_required("manufacturing", "delete"), name='dispatch')
class WorkCenterDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    model = WorkCenter
    template_name = 'manufacturing/workcenter_confirm_delete.html'
    success_url = reverse_lazy('manufacturing:workcenter_list')
    
    def get_queryset(self):
        return super().get_queryset()


# ==================== Production Order Views ====================

@method_decorator(csrf_protect, name='dispatch')
class ProductionOrderListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = ProductionOrder
    template_name = 'manufacturing/productionorder_list.html'
    context_object_name = 'production_orders'
    paginate_by = 25
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(po_number__icontains=search) |
                Q(product__name__icontains=search)
            )
        
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        
        return qs.order_by('-due_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['statuses'] = ProductionOrder.STATUS_CHOICES
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class ProductionOrderCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    model = ProductionOrder
    form_class = ProductionOrderForm
    template_name = 'manufacturing/productionorder_form.html'
    success_url = reverse_lazy('manufacturing:productionorder_list')
    
    def form_valid(self, form):
        entity_id = self.request.session.get("selected_entity_id")
        # Entity set by SessionEntityMixin
        
        instance = form.save(commit=False)
        instance.entity_id = entity_id
        instance.created_by = self.request.user
        
        # Auto-calculate costs from BOM and Routing
        if instance.bom:
            instance.estimated_material_cost = (
                instance.bom.get_total_material_cost() * instance.quantity_ordered
            )
        
        if instance.routing:
            total_hours = instance.routing.get_total_labor_hours()
            work_centers = WorkCenter.objects.filter(routing_lines__routing=instance.routing).distinct()
            labor_cost = sum(
                wc.labor_cost_per_hour * total_hours
                for wc in work_centers
            ) / max(work_centers.count(), 1)
            instance.estimated_labor_cost = labor_cost * instance.quantity_ordered
        
        instance.save()
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class ProductionOrderUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    model = ProductionOrder
    form_class = ProductionOrderForm
    template_name = 'manufacturing/productionorder_form.html'
    success_url = reverse_lazy('manufacturing:productionorder_list')
    
    def get_queryset(self):
        return super().get_queryset()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(module_permission_required("manufacturing", "delete"), name='dispatch')
class ProductionOrderDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    model = ProductionOrder
    template_name = 'manufacturing/productionorder_confirm_delete.html'
    success_url = reverse_lazy('manufacturing:productionorder_list')
    
    def get_queryset(self):
        return super().get_queryset()


# ==================== Quality Inspection Views ====================

@method_decorator(csrf_protect, name='dispatch')
class QualityInspectionListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = QualityInspection
    template_name = 'manufacturing/qualityinspection_list.html'
    context_object_name = 'inspections'
    paginate_by = 25
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        
        return qs.order_by('-inspection_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = QualityInspection.INSPECTION_STATUS
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class QualityInspectionCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    model = QualityInspection
    form_class = QualityInspectionForm
    template_name = 'manufacturing/qualityinspection_form.html'
    success_url = reverse_lazy('manufacturing:qualityinspection_list')
    
    def form_valid(self, form):
        entity_id = self.request.session.get("selected_entity_id")
        # Entity set by SessionEntityMixin
        
        instance = form.save(commit=False)
        instance.entity_id = entity_id
        instance.inspected_by = self.request.user
        instance.save()
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class QualityInspectionUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    model = QualityInspection
    form_class = QualityInspectionForm
    template_name = 'manufacturing/qualityinspection_form.html'
    success_url = reverse_lazy('manufacturing:qualityinspection_list')
    
    def get_queryset(self):
        return super().get_queryset()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(module_permission_required("manufacturing", "delete"), name='dispatch')
class QualityInspectionDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    model = QualityInspection
    template_name = 'manufacturing/qualityinspection_confirm_delete.html'
    success_url = reverse_lazy('manufacturing:qualityinspection_list')
    
    def get_queryset(self):
        return super().get_queryset()


# ==================== Equipment Views ====================

@method_decorator(csrf_protect, name='dispatch')
class EquipmentListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = Equipment
    template_name = 'manufacturing/equipment_list.html'
    context_object_name = 'equipment'
    paginate_by = 25
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(equipment_code__icontains=search) |
                Q(name__icontains=search)
            )
        
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        
        return qs.order_by('equipment_code')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['statuses'] = Equipment.STATUS_CHOICES
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class EquipmentCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = 'manufacturing/equipment_form.html'
    success_url = reverse_lazy('manufacturing:equipment_list')
    
    def form_valid(self, form):
        entity_id = self.request.session.get("selected_entity_id")
        # Entity set by SessionEntityMixin
        
        instance = form.save(commit=False)
        instance.entity_id = entity_id
        instance.save()
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class EquipmentUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = 'manufacturing/equipment_form.html'
    success_url = reverse_lazy('manufacturing:equipment_list')
    
    def get_queryset(self):
        return super().get_queryset()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(module_permission_required("manufacturing", "delete"), name='dispatch')
class EquipmentDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    model = Equipment
    template_name = 'manufacturing/equipment_confirm_delete.html'
    success_url = reverse_lazy('manufacturing:equipment_list')
    
    def get_queryset(self):
        return super().get_queryset()


# ==================== Dashboard View ====================

@method_decorator(csrf_protect, name='dispatch')
class ManufacturingDashboardView(SessionEntityMixin, LoginRequiredMixin, TemplateView):
    """Manufacturing dashboard with KPIs and metrics."""
    template_name = 'manufacturing/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the current entity from session (set by SessionEntityMixin)
        entity_id = self.request.session.get('selected_entity_id')
        
        # Production metrics - filtered by entity only
        total_orders = ProductionOrder.objects.filter(entity_id=entity_id).count()
        open_orders = ProductionOrder.objects.filter(
            entity_id=entity_id,
            status__in=['RELEASED', 'IN_PROGRESS']
        ).count()
        completed_orders = ProductionOrder.objects.filter(
            entity_id=entity_id,
            status='COMPLETE'
        ).count()
        
        # Quality metrics
        failed_inspections = QualityInspection.objects.filter(
            entity_id=entity_id,
            status='FAIL'
        ).count()
        
        # Inventory metrics
        low_stock_materials = RawMaterial.objects.filter(
            entity_id=entity_id,
            current_stock__lte=F('reorder_point')
        ).count()
        
        # Cost metrics - For pending orders use estimated, for completed use actual OR estimated if actual is 0
        pending_po_cost = ProductionOrder.objects.filter(
            entity_id=entity_id,
            status__in=['DRAFT', 'PLANNED', 'RELEASED', 'IN_PROGRESS']
        ).aggregate(total=Sum('estimated_material_cost') + Sum('estimated_labor_cost'))['total'] or Decimal('0.00')
        
        # For completed orders: use actual costs if > 0, otherwise use estimated
        completed_orders_qs = ProductionOrder.objects.filter(
            entity_id=entity_id,
            status='COMPLETE'
        )
        
        completed_po_cost = Decimal('0.00')
        for po in completed_orders_qs:
            actual_total = (po.actual_material_cost or Decimal('0.00')) + (po.actual_labor_cost or Decimal('0.00'))
            if actual_total > 0:
                completed_po_cost += actual_total
            else:
                # If no actual costs, use estimated
                completed_po_cost += (po.estimated_material_cost or Decimal('0.00')) + (po.estimated_labor_cost or Decimal('0.00'))
        
        total_po_cost = pending_po_cost + completed_po_cost
        
        context.update({
            'total_orders': total_orders,
            'open_orders': open_orders,
            'completed_orders': completed_orders,
            'failed_inspections': failed_inspections,
            'low_stock_materials': low_stock_materials,
            'total_po_cost': total_po_cost,
            'pending_po_cost': pending_po_cost,
            'completed_po_cost': completed_po_cost,
            'csrf_token': get_token(self.request),
        })
        
        return context


# ==================== Distributor Management Views ====================

@method_decorator(csrf_protect, name='dispatch')
class DistributorListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = Distributor
    template_name = 'manufacturing/distributor_list.html'
    context_object_name = 'distributors'
    paginate_by = 25
    
    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(code__icontains=search))
        return qs.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


@method_decorator(csrf_protect, name='dispatch')
class DistributorCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    model = Distributor
    form_class = DistributorForm
    template_name = 'manufacturing/distributor_form.html'
    success_url = reverse_lazy('manufacturing:distributor_list')
    
    def form_valid(self, form):
        entity_id = self.request.session.get("selected_entity_id")
        instance = form.save(commit=False)
        instance.entity_id = entity_id
        instance.save()
        return redirect(self.success_url)


@method_decorator(csrf_protect, name='dispatch')
class DistributorUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    model = Distributor
    form_class = DistributorForm
    template_name = 'manufacturing/distributor_form.html'
    success_url = reverse_lazy('manufacturing:distributor_list')


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(module_permission_required("manufacturing", "delete"), name='dispatch')
class DistributorDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    model = Distributor
    template_name = 'manufacturing/distributor_confirm_delete.html'
    success_url = reverse_lazy('manufacturing:distributor_list')


# ==================== Distributor Order Views ====================

@method_decorator(csrf_protect, name='dispatch')
class DistributorOrderListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = DistributorOrder
    template_name = 'manufacturing/distributororder_list.html'
    context_object_name = 'orders'
    paginate_by = 25
    
    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(Q(distributor__name__icontains=search) | Q(order_number__icontains=search))
        return qs.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


@method_decorator(csrf_protect, name='dispatch')
class DistributorOrderCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    model = DistributorOrder
    form_class = DistributorOrderForm
    template_name = 'manufacturing/distributororder_form.html'
    success_url = reverse_lazy('manufacturing:distributororder_list')
    
    def form_valid(self, form):
        import uuid
        from datetime import datetime
        
        entity_id = self.request.session.get("selected_entity_id")
        instance = form.save(commit=False)
        
        # Generate order_number if not already set
        if not instance.order_number:
            timestamp = datetime.now().strftime('%Y%m%d')
            unique_id = str(uuid.uuid4())[:6].upper()
            instance.order_number = f"ORD-{timestamp}-{unique_id}"
        
        instance.entity_id = entity_id
        instance.save()
        return redirect(self.success_url)


@method_decorator(csrf_protect, name='dispatch')
class DistributorOrderUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    model = DistributorOrder
    form_class = DistributorOrderForm
    template_name = 'manufacturing/distributororder_form.html'
    success_url = reverse_lazy('manufacturing:distributororder_list')


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(module_permission_required("manufacturing", "delete"), name='dispatch')
class DistributorOrderDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    model = DistributorOrder
    template_name = 'manufacturing/distributororder_confirm_delete.html'
    success_url = reverse_lazy('manufacturing:distributororder_list')


# ==================== Order Shipment Views ====================

@method_decorator(csrf_protect, name='dispatch')
class OrderShipmentListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = OrderShipment
    template_name = 'manufacturing/ordershipment_list.html'
    context_object_name = 'shipments'
    paginate_by = 25
    
    def get_queryset(self):
        # Filter through order relationship to entity
        entity_id = self.request.session.get("selected_entity_id")
        qs = OrderShipment.objects.filter(order__entity_id=entity_id)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(Q(tracking_number__icontains=search))
        return qs.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


@method_decorator(csrf_protect, name='dispatch')
class OrderShipmentCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    model = OrderShipment
    form_class = OrderShipmentForm
    template_name = 'manufacturing/ordershipment_form.html'
    success_url = reverse_lazy('manufacturing:ordershipment_list')
    
    def form_valid(self, form):
        import uuid
        from datetime import datetime
        
        entity_id = self.request.session.get("selected_entity_id")
        instance = form.save(commit=False)
        
        # Generate shipment_number if not already set
        if not instance.shipment_number:
            timestamp = datetime.now().strftime('%Y%m%d')
            unique_id = str(uuid.uuid4())[:6].upper()
            instance.shipment_number = f"SHIP-{timestamp}-{unique_id}"
        
        instance.entity_id = entity_id
        instance.save()
        return redirect(self.success_url)


@method_decorator(csrf_protect, name='dispatch')
class OrderShipmentUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    model = OrderShipment
    form_class = OrderShipmentForm
    template_name = 'manufacturing/ordershipment_form.html'
    success_url = reverse_lazy('manufacturing:ordershipment_list')


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(module_permission_required("manufacturing", "delete"), name='dispatch')
class OrderShipmentDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    model = OrderShipment
    template_name = 'manufacturing/ordershipment_confirm_delete.html'
    success_url = reverse_lazy('manufacturing:ordershipment_list')


# ==================== After-Sales Service Views ====================

@method_decorator(csrf_protect, name='dispatch')
class AfterSalesServiceListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = AfterSalesService
    template_name = 'manufacturing/aftersalesservice_list.html'
    context_object_name = 'services'
    paginate_by = 25
    
    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(Q(service_ticket_number__icontains=search) | Q(subject__icontains=search))
        return qs.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


@method_decorator(csrf_protect, name='dispatch')
class AfterSalesServiceCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    model = AfterSalesService
    form_class = AfterSalesServiceForm
    template_name = 'manufacturing/aftersalesservice_form.html'
    success_url = reverse_lazy('manufacturing:aftersalesservice_list')
    
    def form_valid(self, form):
        import uuid
        from datetime import datetime
        
        entity_id = self.request.session.get("selected_entity_id")
        instance = form.save(commit=False)
        
        # Generate service_ticket_number if not already set
        if not instance.service_ticket_number:
            timestamp = datetime.now().strftime('%Y%m%d')
            unique_id = str(uuid.uuid4())[:6].upper()
            instance.service_ticket_number = f"TICKET-{timestamp}-{unique_id}"
        
        instance.entity_id = entity_id
        instance.save()
        return redirect(self.success_url)


@method_decorator(csrf_protect, name='dispatch')
class AfterSalesServiceUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    model = AfterSalesService
    form_class = AfterSalesServiceForm
    template_name = 'manufacturing/aftersalesservice_form.html'
    success_url = reverse_lazy('manufacturing:aftersalesservice_list')


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(module_permission_required("manufacturing", "delete"), name='dispatch')
class AfterSalesServiceDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    model = AfterSalesService
    template_name = 'manufacturing/aftersalesservice_confirm_delete.html'
    success_url = reverse_lazy('manufacturing:aftersalesservice_list')


# ==================== Warranty Registration Views ====================

@method_decorator(csrf_protect, name='dispatch')
class WarrantyRegistrationListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = WarrantyRegistration
    template_name = 'manufacturing/warrantyregistration_list.html'
    context_object_name = 'warranties'
    paginate_by = 25
    
    def get_queryset(self):
        entity_id = self.request.session.get("selected_entity_id")
        qs = WarrantyRegistration.objects.filter(entity_id=entity_id)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(Q(warranty_number__icontains=search) | Q(product_code__icontains=search))
        return qs.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


@method_decorator(csrf_protect, name='dispatch')
class WarrantyRegistrationCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    model = WarrantyRegistration
    form_class = WarrantyRegistrationForm
    template_name = 'manufacturing/warrantyregistration_form.html'
    success_url = reverse_lazy('manufacturing:warrantyregistration_list')
    
    def form_valid(self, form):
        import uuid
        from datetime import datetime
        
        entity_id = self.request.session.get("selected_entity_id")
        instance = form.save(commit=False)
        
        # Generate warranty_number if not already set
        if not instance.warranty_number:
            timestamp = datetime.now().strftime('%Y%m%d')
            unique_id = str(uuid.uuid4())[:6].upper()
            instance.warranty_number = f"WAR-{timestamp}-{unique_id}"
        
        instance.entity_id = entity_id
        instance.save()
        return redirect(self.success_url)


@method_decorator(csrf_protect, name='dispatch')
class WarrantyRegistrationUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    model = WarrantyRegistration
    form_class = WarrantyRegistrationForm
    template_name = 'manufacturing/warrantyregistration_form.html'
    success_url = reverse_lazy('manufacturing:warrantyregistration_list')


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(module_permission_required("manufacturing", "delete"), name='dispatch')
class WarrantyRegistrationDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    model = WarrantyRegistration
    template_name = 'manufacturing/warrantyregistration_confirm_delete.html'
    success_url = reverse_lazy('manufacturing:warrantyregistration_list')


# ==================== Distributor Performance Views ====================

@method_decorator(csrf_protect, name='dispatch')
class DistributorPerformanceListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = DistributorPerformance
    template_name = 'manufacturing/distributorperformance_list.html'
    context_object_name = 'performances'
    paginate_by = 25
    
    def get_queryset(self):
        entity_id = self.request.session.get("selected_entity_id")
        qs = DistributorPerformance.objects.filter(entity_id=entity_id)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(Q(distributor__distributor_name__icontains=search))
        return qs.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


@method_decorator(csrf_protect, name='dispatch')
class DistributorPerformanceCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    model = DistributorPerformance
    form_class = DistributorPerformanceForm
    template_name = 'manufacturing/distributorperformance_form.html'
    success_url = reverse_lazy('manufacturing:distributorperformance_list')
    
    def form_valid(self, form):
        # Get instance and set entity from session
        instance = form.save(commit=False)
        entity_id = self.request.session.get("selected_entity_id")
        instance.entity_id = entity_id
        
        # Handle update_or_create for unique constraint (distributor, month, year)
        if instance.performance_date:
            obj, created = DistributorPerformance.objects.update_or_create(
                distributor=instance.distributor,
                performance_month=instance.performance_month,
                performance_year=instance.performance_year,
                defaults={
                    'entity_id': instance.entity_id,
                    'performance_date': instance.performance_date,
                    'orders_count': instance.orders_count,
                    'total_sales': instance.total_sales,
                    'average_order_value': instance.average_order_value,
                    'on_time_delivery_percentage': instance.on_time_delivery_percentage,
                    'order_accuracy_percentage': instance.order_accuracy_percentage,
                    'return_rate_percentage': instance.return_rate_percentage,
                    'complaint_count': instance.complaint_count,
                    'payment_on_time_percentage': instance.payment_on_time_percentage,
                    'overall_rating': instance.overall_rating,
                }
            )
        
        return redirect(self.success_url)


@method_decorator(csrf_protect, name='dispatch')
class DistributorPerformanceUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    model = DistributorPerformance
    form_class = DistributorPerformanceForm
    template_name = 'manufacturing/distributorperformance_form.html'
    success_url = reverse_lazy('manufacturing:distributorperformance_list')


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(module_permission_required("manufacturing", "delete"), name='dispatch')
class DistributorPerformanceDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    model = DistributorPerformance
    template_name = 'manufacturing/distributorperformance_confirm_delete.html'
    success_url = reverse_lazy('manufacturing:distributorperformance_list')

