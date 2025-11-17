"""
Manufacturing Module Views
Complete CRUD operations with RBAC and multi-entity support.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
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

from accounting.role_models import UserRole
from accounting.models import Entity
from .models import (
    ProductCategory, Product, RawMaterial,
    BillOfMaterials, BOMLine,
    WorkCenter, Routing, RoutingLine,
    ProductionOrder, QualityInspection, Equipment
)
from .forms import (
    ProductCategoryForm, ProductForm, RawMaterialForm,
    BillOfMaterialsForm, BOMLineForm,
    WorkCenterForm, RoutingForm, RoutingLineForm,
    ProductionOrderForm, QualityInspectionForm, EquipmentForm
)


# ==================== Utility Functions ====================

def get_user_entities(user):
    """Get entities accessible to user based on UserRole."""
    return UserRole.objects.filter(
        user=user,
        is_active=True
    ).values_list('entity_id', flat=True)


def get_filtered_queryset(model, user, base_queryset=None):
    """Filter queryset by user's accessible entities."""
    if base_queryset is None:
        base_queryset = model.objects.all()
    
    user_entities = get_user_entities(user)
    return base_queryset.filter(entity_id__in=user_entities)


# ==================== Product Category Views ====================

@method_decorator(csrf_protect, name='dispatch')
class ProductCategoryListView(LoginRequiredMixin, ListView):
    model = ProductCategory
    template_name = 'manufacturing/productcategory_list.html'
    context_object_name = 'categories'
    paginate_by = 25
    
    def get_queryset(self):
        qs = get_filtered_queryset(ProductCategory, self.request.user)
        
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
class ProductCategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = ProductCategory
    template_name = 'manufacturing/productcategory_confirm_delete.html'
    success_url = reverse_lazy('manufacturing:productcategory_list')
    
    def get_queryset(self):
        return get_filtered_queryset(ProductCategory, self.request.user)


@method_decorator(csrf_protect, name='dispatch')
class ProductCategoryCreateView(LoginRequiredMixin, CreateView):
    model = ProductCategory
    form_class = ProductCategoryForm
    template_name = 'manufacturing/productcategory_form.html'
    success_url = reverse_lazy('manufacturing:productcategory_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user_entities = get_user_entities(self.request.user)
        
        # Auto-set entity for single-entity users
        if user_entities.count() == 1:
            kwargs['initial'] = {'entity': user_entities.first()}
        
        return kwargs
    
    def form_valid(self, form):
        # Set entity based on user's accessible entities
        user_entities = list(get_user_entities(self.request.user))
        if not user_entities:
            return redirect('manufacturing:productcategory_list')
        
        instance = form.save(commit=False)
        instance.entity_id = user_entities[0]
        instance.save()
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


# ==================== Product Views ====================

@method_decorator(csrf_protect, name='dispatch')
class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'manufacturing/product_list.html'
    context_object_name = 'products'
    paginate_by = 25
    
    def get_queryset(self):
        qs = get_filtered_queryset(Product, self.request.user)
        
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
class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'manufacturing/product_form.html'
    success_url = reverse_lazy('manufacturing:product_list')
    
    def form_valid(self, form):
        user_entities = list(get_user_entities(self.request.user))
        if not user_entities:
            return redirect('manufacturing:product_list')
        
        instance = form.save(commit=False)
        instance.entity_id = user_entities[0]
        instance.created_by = self.request.user
        instance.save()
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'manufacturing/product_form.html'
    success_url = reverse_lazy('manufacturing:product_list')
    
    def get_queryset(self):
        return get_filtered_queryset(Product, self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'manufacturing/product_confirm_delete.html'
    success_url = reverse_lazy('manufacturing:product_list')
    
    def get_queryset(self):
        return get_filtered_queryset(Product, self.request.user)


# ==================== Raw Material Views ====================

@method_decorator(csrf_protect, name='dispatch')
class RawMaterialListView(LoginRequiredMixin, ListView):
    model = RawMaterial
    template_name = 'manufacturing/rawmaterial_list.html'
    context_object_name = 'materials'
    paginate_by = 25
    
    def get_queryset(self):
        qs = get_filtered_queryset(RawMaterial, self.request.user)
        
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
class RawMaterialCreateView(LoginRequiredMixin, CreateView):
    model = RawMaterial
    form_class = RawMaterialForm
    template_name = 'manufacturing/rawmaterial_form.html'
    success_url = reverse_lazy('manufacturing:rawmaterial_list')
    
    def form_valid(self, form):
        user_entities = list(get_user_entities(self.request.user))
        if not user_entities:
            return redirect('manufacturing:rawmaterial_list')
        
        instance = form.save(commit=False)
        instance.entity_id = user_entities[0]
        instance.save()
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class RawMaterialDeleteView(LoginRequiredMixin, DeleteView):
    model = RawMaterial
    template_name = 'manufacturing/rawmaterial_confirm_delete.html'
    success_url = reverse_lazy('manufacturing:rawmaterial_list')
    
    def get_queryset(self):
        return get_filtered_queryset(RawMaterial, self.request.user)


# ==================== Bill of Materials Views ====================

@method_decorator(csrf_protect, name='dispatch')
class BOMListView(LoginRequiredMixin, ListView):
    model = BillOfMaterials
    template_name = 'manufacturing/bom_list.html'
    context_object_name = 'boms'
    paginate_by = 25
    
    def get_queryset(self):
        qs = get_filtered_queryset(BillOfMaterials, self.request.user)
        
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
class BOMCreateView(LoginRequiredMixin, CreateView):
    model = BillOfMaterials
    form_class = BillOfMaterialsForm
    template_name = 'manufacturing/bom_form.html'
    success_url = reverse_lazy('manufacturing:bom_list')
    
    def form_valid(self, form):
        user_entities = list(get_user_entities(self.request.user))
        if not user_entities:
            return redirect('manufacturing:bom_list')
        
        instance = form.save(commit=False)
        instance.entity_id = user_entities[0]
        instance.created_by = self.request.user
        instance.save()
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class BOMUpdateView(LoginRequiredMixin, UpdateView):
    model = BillOfMaterials
    form_class = BillOfMaterialsForm
    template_name = 'manufacturing/bom_form.html'
    success_url = reverse_lazy('manufacturing:bom_list')
    
    def get_queryset(self):
        return get_filtered_queryset(BillOfMaterials, self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class BOMDeleteView(LoginRequiredMixin, DeleteView):
    model = BillOfMaterials
    template_name = 'manufacturing/bom_confirm_delete.html'
    success_url = reverse_lazy('manufacturing:bom_list')
    
    def get_queryset(self):
        return get_filtered_queryset(BillOfMaterials, self.request.user)


# ==================== Routing Views ====================

@method_decorator(csrf_protect, name='dispatch')
class RoutingListView(LoginRequiredMixin, ListView):
    model = Routing
    template_name = 'manufacturing/routing_list.html'
    context_object_name = 'routings'
    paginate_by = 25
    
    def get_queryset(self):
        qs = get_filtered_queryset(Routing, self.request.user)
        
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
class RoutingCreateView(LoginRequiredMixin, CreateView):
    model = Routing
    form_class = RoutingForm
    template_name = 'manufacturing/routing_form.html'
    success_url = reverse_lazy('manufacturing:routing_list')
    
    def form_valid(self, form):
        user_entities = list(get_user_entities(self.request.user))
        if not user_entities:
            return redirect('manufacturing:routing_list')
        
        instance = form.save(commit=False)
        instance.entity_id = user_entities[0]
        instance.created_by = self.request.user
        instance.save()
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class RoutingUpdateView(LoginRequiredMixin, UpdateView):
    model = Routing
    form_class = RoutingForm
    template_name = 'manufacturing/routing_form.html'
    success_url = reverse_lazy('manufacturing:routing_list')
    
    def get_queryset(self):
        return get_filtered_queryset(Routing, self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class RoutingDeleteView(LoginRequiredMixin, DeleteView):
    model = Routing
    template_name = 'manufacturing/routing_confirm_delete.html'
    success_url = reverse_lazy('manufacturing:routing_list')
    
    def get_queryset(self):
        return get_filtered_queryset(Routing, self.request.user)


# ==================== Work Center Views ====================

@method_decorator(csrf_protect, name='dispatch')
class WorkCenterListView(LoginRequiredMixin, ListView):
    model = WorkCenter
    template_name = 'manufacturing/workcenter_list.html'
    context_object_name = 'work_centers'
    paginate_by = 25
    
    def get_queryset(self):
        qs = get_filtered_queryset(WorkCenter, self.request.user)
        
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
class WorkCenterCreateView(LoginRequiredMixin, CreateView):
    model = WorkCenter
    form_class = WorkCenterForm
    template_name = 'manufacturing/workcenter_form.html'
    success_url = reverse_lazy('manufacturing:workcenter_list')
    
    def form_valid(self, form):
        user_entities = list(get_user_entities(self.request.user))
        if not user_entities:
            return redirect('manufacturing:workcenter_list')
        
        instance = form.save(commit=False)
        instance.entity_id = user_entities[0]
        instance.save()
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class WorkCenterDeleteView(LoginRequiredMixin, DeleteView):
    model = WorkCenter
    template_name = 'manufacturing/workcenter_confirm_delete.html'
    success_url = reverse_lazy('manufacturing:workcenter_list')
    
    def get_queryset(self):
        return get_filtered_queryset(WorkCenter, self.request.user)


# ==================== Production Order Views ====================

@method_decorator(csrf_protect, name='dispatch')
class ProductionOrderListView(LoginRequiredMixin, ListView):
    model = ProductionOrder
    template_name = 'manufacturing/productionorder_list.html'
    context_object_name = 'production_orders'
    paginate_by = 25
    
    def get_queryset(self):
        qs = get_filtered_queryset(ProductionOrder, self.request.user)
        
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
class ProductionOrderCreateView(LoginRequiredMixin, CreateView):
    model = ProductionOrder
    form_class = ProductionOrderForm
    template_name = 'manufacturing/productionorder_form.html'
    success_url = reverse_lazy('manufacturing:productionorder_list')
    
    def form_valid(self, form):
        user_entities = list(get_user_entities(self.request.user))
        if not user_entities:
            return redirect('manufacturing:productionorder_list')
        
        instance = form.save(commit=False)
        instance.entity_id = user_entities[0]
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
class ProductionOrderUpdateView(LoginRequiredMixin, UpdateView):
    model = ProductionOrder
    form_class = ProductionOrderForm
    template_name = 'manufacturing/productionorder_form.html'
    success_url = reverse_lazy('manufacturing:productionorder_list')
    
    def get_queryset(self):
        return get_filtered_queryset(ProductionOrder, self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class ProductionOrderDeleteView(LoginRequiredMixin, DeleteView):
    model = ProductionOrder
    template_name = 'manufacturing/productionorder_confirm_delete.html'
    success_url = reverse_lazy('manufacturing:productionorder_list')
    
    def get_queryset(self):
        return get_filtered_queryset(ProductionOrder, self.request.user)


# ==================== Quality Inspection Views ====================

@method_decorator(csrf_protect, name='dispatch')
class QualityInspectionListView(LoginRequiredMixin, ListView):
    model = QualityInspection
    template_name = 'manufacturing/qualityinspection_list.html'
    context_object_name = 'inspections'
    paginate_by = 25
    
    def get_queryset(self):
        qs = get_filtered_queryset(QualityInspection, self.request.user)
        
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
class QualityInspectionCreateView(LoginRequiredMixin, CreateView):
    model = QualityInspection
    form_class = QualityInspectionForm
    template_name = 'manufacturing/qualityinspection_form.html'
    success_url = reverse_lazy('manufacturing:qualityinspection_list')
    
    def form_valid(self, form):
        user_entities = list(get_user_entities(self.request.user))
        if not user_entities:
            return redirect('manufacturing:qualityinspection_list')
        
        instance = form.save(commit=False)
        instance.entity_id = user_entities[0]
        instance.inspected_by = self.request.user
        instance.save()
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class QualityInspectionUpdateView(LoginRequiredMixin, UpdateView):
    model = QualityInspection
    form_class = QualityInspectionForm
    template_name = 'manufacturing/qualityinspection_form.html'
    success_url = reverse_lazy('manufacturing:qualityinspection_list')
    
    def get_queryset(self):
        return get_filtered_queryset(QualityInspection, self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class QualityInspectionDeleteView(LoginRequiredMixin, DeleteView):
    model = QualityInspection
    template_name = 'manufacturing/qualityinspection_confirm_delete.html'
    success_url = reverse_lazy('manufacturing:qualityinspection_list')
    
    def get_queryset(self):
        return get_filtered_queryset(QualityInspection, self.request.user)


# ==================== Equipment Views ====================

@method_decorator(csrf_protect, name='dispatch')
class EquipmentListView(LoginRequiredMixin, ListView):
    model = Equipment
    template_name = 'manufacturing/equipment_list.html'
    context_object_name = 'equipment'
    paginate_by = 25
    
    def get_queryset(self):
        qs = get_filtered_queryset(Equipment, self.request.user)
        
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
class EquipmentCreateView(LoginRequiredMixin, CreateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = 'manufacturing/equipment_form.html'
    success_url = reverse_lazy('manufacturing:equipment_list')
    
    def form_valid(self, form):
        user_entities = list(get_user_entities(self.request.user))
        if not user_entities:
            return redirect('manufacturing:equipment_list')
        
        instance = form.save(commit=False)
        instance.entity_id = user_entities[0]
        instance.save()
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class EquipmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Equipment
    template_name = 'manufacturing/equipment_confirm_delete.html'
    success_url = reverse_lazy('manufacturing:equipment_list')
    
    def get_queryset(self):
        return get_filtered_queryset(Equipment, self.request.user)


# ==================== Dashboard View ====================

@method_decorator(csrf_protect, name='dispatch')
class ManufacturingDashboardView(LoginRequiredMixin, TemplateView):
    """Manufacturing dashboard with KPIs and metrics."""
    template_name = 'manufacturing/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_entities = get_user_entities(self.request.user)
        
        # Production metrics
        total_orders = ProductionOrder.objects.filter(entity_id__in=user_entities).count()
        open_orders = ProductionOrder.objects.filter(
            entity_id__in=user_entities,
            status__in=['RELEASED', 'IN_PROGRESS']
        ).count()
        completed_orders = ProductionOrder.objects.filter(
            entity_id__in=user_entities,
            status='COMPLETE'
        ).count()
        
        # Quality metrics
        failed_inspections = QualityInspection.objects.filter(
            entity_id__in=user_entities,
            status='FAIL'
        ).count()
        
        # Inventory metrics
        low_stock_materials = RawMaterial.objects.filter(
            entity_id__in=user_entities,
            current_stock__lte=F('reorder_point')
        ).count()
        
        # Cost metrics - For pending orders use estimated, for completed use actual OR estimated if actual is 0
        pending_po_cost = ProductionOrder.objects.filter(
            entity_id__in=user_entities,
            status__in=['DRAFT', 'PLANNED', 'RELEASED', 'IN_PROGRESS']
        ).aggregate(total=Sum('estimated_material_cost') + Sum('estimated_labor_cost'))['total'] or Decimal('0.00')
        
        # For completed orders: use actual costs if > 0, otherwise use estimated
        completed_orders_qs = ProductionOrder.objects.filter(
            entity_id__in=user_entities,
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
        
        context = {
            'total_orders': total_orders,
            'open_orders': open_orders,
            'completed_orders': completed_orders,
            'failed_inspections': failed_inspections,
            'low_stock_materials': low_stock_materials,
            'total_po_cost': total_po_cost,
            'pending_po_cost': pending_po_cost,
            'completed_po_cost': completed_po_cost,
            'csrf_token': get_token(self.request),
        }
        
        return context
