from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Q, F, Prefetch
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django import forms
from .models import RawMaterial, Supplier, RawMaterialCategory, Stock


class RawMaterialForm(forms.ModelForm):
    # Explicitly define category and supplier fields to ensure they show all options
    category = forms.ModelChoiceField(
        queryset=RawMaterialCategory.objects.all().order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control', 'required': 'required', 'id': 'id_category'}),
        label='Category'
    )
    
    # Field to select existing material names by category
    existing_material = forms.ModelChoiceField(
        queryset=RawMaterial.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_existing_material'}),
        label='Select Existing Material Name (Optional)',
        required=False,
        help_text='Choose from existing materials in the selected category'
    )
    
    default_supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.filter(is_active=True).order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Default Supplier',
        required=False
    )
    
    class Meta:
        model = RawMaterial
        fields = ['product_code', 'name', 'description', 'category', 'unit_of_measure', 
                  'hsn_code', 'default_supplier', 'current_unit_price', 'is_active']
        widgets = {
            'product_code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'unit_of_measure': forms.Select(attrs={'class': 'form-control'}),
            'hsn_code': forms.TextInput(attrs={'class': 'form-control'}),
            'current_unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Refresh the querysets to ensure they are current
        self.fields['category'].queryset = RawMaterialCategory.objects.all().order_by('name')
        self.fields['default_supplier'].queryset = Supplier.objects.filter(is_active=True).order_by('name')
        # Initialize existing_material with empty queryset - will be populated by JavaScript
        self.fields['existing_material'].queryset = RawMaterial.objects.none()


class RawMaterialsDashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard for raw materials management"""
    template_name = 'raw_materials/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all data
        context['total_materials'] = RawMaterial.objects.count()
        context['total_suppliers'] = Supplier.objects.count()
        context['total_categories'] = RawMaterialCategory.objects.count()
        
        # Get low stock items (quantity < minimum level)
        context['low_stock_items'] = Stock.objects.filter(
            quantity_on_hand__lt=F('minimum_stock_level')
        ).select_related('raw_material').count()
        
        # Get total inventory value
        context['total_inventory_qty'] = Stock.objects.aggregate(
            total=Sum('quantity_on_hand')
        )['total'] or 0
        
        # Get materials grouped by category
        context['materials_by_category'] = RawMaterialCategory.objects.annotate(
            material_count=Count('rawmaterial')
        ).order_by('-material_count')
        
        # Get suppliers with their material counts
        context['suppliers_with_counts'] = Supplier.objects.annotate(
            material_count=Count('rawmaterial')
        ).order_by('-material_count')
        
        # Get recent raw materials
        context['recent_materials'] = RawMaterial.objects.all().order_by('-created_at')[:10]
        
        # Get active suppliers
        context['active_suppliers'] = Supplier.objects.filter(is_active=True)
        
        # Stock status summary
        context['in_stock'] = Stock.objects.filter(
            quantity_on_hand__gt=F('minimum_stock_level')
        ).count()
        context['low_stock'] = Stock.objects.filter(
            quantity_on_hand__lte=F('minimum_stock_level'),
            quantity_on_hand__gt=0
        ).count()
        context['out_of_stock'] = Stock.objects.filter(quantity_on_hand=0).count()
        
        return context


class RawMaterialListView(LoginRequiredMixin, ListView):
    """List all raw materials"""
    model = RawMaterial
    template_name = 'raw_materials/raw_material_list.html'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = RawMaterial.objects.all().order_by('product_code')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(product_code__icontains=search) |
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.select_related('category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class SupplierListView(LoginRequiredMixin, ListView):
    """List all suppliers"""
    model = Supplier
    template_name = 'raw_materials/supplier_list.html'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Supplier.objects.all().order_by('name')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(contact_person__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset.annotate(material_count=Count('rawmaterial'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class SupplierForm(forms.ModelForm):
    """Form for creating and editing suppliers"""
    class Meta:
        model = Supplier
        fields = ['name', 'supplier_code', 'contact_person', 'email', 'phone', 'address', 'city', 
                  'state', 'country', 'payment_terms', 'credit_limit', 'currency', 
                  'quality_rating', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter supplier name'}),
            'supplier_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., SUPP-001'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact person name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Street address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State/Province'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'payment_terms': forms.Select(attrs={'class': 'form-select'}),
            'credit_limit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'INR'}),
            'quality_rating': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.0', 'step': '0.1', 'min': '0', 'max': '10'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SupplierCreateView(LoginRequiredMixin, CreateView):
    """Create a new supplier"""
    model = Supplier
    form_class = SupplierForm
    template_name = 'raw_materials/supplier_form.html'
    success_url = reverse_lazy('raw_materials:supplier_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Supplier'
        context['button_text'] = 'Create Supplier'
        return context


class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    """Edit a supplier"""
    model = Supplier
    form_class = SupplierForm
    template_name = 'raw_materials/supplier_form.html'
    success_url = reverse_lazy('raw_materials:supplier_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Supplier - {self.object.name}'
        context['button_text'] = 'Update Supplier'
        context['supplier_code'] = self.object.supplier_code
        
        # Get materials supplied by this supplier
        context['supplied_materials'] = RawMaterial.objects.filter(
            default_supplier=self.object,
            is_active=True
        ).select_related('category').order_by('name')
        
        # Get available materials to add
        context['available_materials'] = RawMaterial.objects.filter(
            is_active=True
        ).exclude(
            default_supplier=self.object
        ).select_related('category').order_by('name')
        
        return context


class StockLevelView(LoginRequiredMixin, ListView):
    """List all stock levels with status indicators"""
    model = Stock
    template_name = 'raw_materials/stock_levels.html'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Stock.objects.all().select_related('raw_material')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'low':
            queryset = queryset.filter(
                quantity_on_hand__lte=F('minimum_stock_level'),
                quantity_on_hand__gt=0
            )
        elif status == 'out':
            queryset = queryset.filter(quantity_on_hand=0)
        elif status == 'good':
            queryset = queryset.filter(quantity_on_hand__gt=F('minimum_stock_level'))
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(raw_material__product_code__icontains=search) |
                Q(raw_material__name__icontains=search)
            )
        
        return queryset.order_by('-quantity_on_hand')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status'] = self.request.GET.get('status', '')
        context['search'] = self.request.GET.get('search', '')
        
        # Stock statistics
        all_stock = Stock.objects.all()
        context['total_items'] = all_stock.count()
        context['in_stock_count'] = all_stock.filter(
            quantity_on_hand__gt=F('minimum_stock_level')
        ).count()
        context['low_stock_count'] = all_stock.filter(
            quantity_on_hand__lte=F('minimum_stock_level'),
            quantity_on_hand__gt=0
        ).count()
        context['out_of_stock_count'] = all_stock.filter(quantity_on_hand=0).count()
        
        return context


class CategoryListView(LoginRequiredMixin, ListView):
    """List all raw material categories with materials"""
    model = RawMaterialCategory
    template_name = 'raw_materials/category_list.html'
    paginate_by = 25
    
    def get_queryset(self):
        return RawMaterialCategory.objects.annotate(
            material_count=Count('rawmaterial')
        ).order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Prefetch materials with their stock data
        materials_prefetch = Prefetch(
            'rawmaterial_set',
            queryset=RawMaterial.objects.select_related('stock').order_by('name')
        )
        
        # Get all categories with their materials (prefetched with stock data)
        context['categories_with_materials'] = RawMaterialCategory.objects.annotate(
            material_count=Count('rawmaterial')
        ).order_by('name').prefetch_related(materials_prefetch)
        
        context['total_materials'] = RawMaterial.objects.count()
        return context


class GetMaterialsByCategory(LoginRequiredMixin, View):
    """API endpoint to get materials by category"""
    def get(self, request):
        category_id = request.GET.get('category_id')
        
        if not category_id:
            return JsonResponse({'materials': []})
        
        try:
            materials = RawMaterial.objects.filter(
                category_id=category_id
            ).values('id', 'name', 'product_code').order_by('name')
            
            materials_list = [
                {
                    'id': m['id'],
                    'name': f"{m['product_code']} - {m['name']}"
                }
                for m in materials
            ]
            
            return JsonResponse({'materials': materials_list})
        except Exception as e:
            return JsonResponse({'materials': [], 'error': str(e)})


class GetMaterialsBySupplier(LoginRequiredMixin, View):
    """API endpoint to get materials supplied by a supplier"""
    def get(self, request):
        supplier_id = request.GET.get('supplier_id')
        
        if not supplier_id:
            return JsonResponse({'materials': []})
        
        try:
            materials = RawMaterial.objects.filter(
                default_supplier_id=supplier_id,
                is_active=True
            ).values('id', 'name', 'product_code', 'unit_of_measure').order_by('name')
            
            materials_list = [
                {
                    'id': m['id'],
                    'name': f"{m['product_code']} - {m['name']}",
                    'unit': m['unit_of_measure']
                }
                for m in materials
            ]
            
            return JsonResponse({'materials': materials_list, 'count': len(materials_list)})
        except Exception as e:
            return JsonResponse({'materials': [], 'error': str(e), 'count': 0})


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class UpdateSupplierProduct(LoginRequiredMixin, View):
    """API endpoint to add/remove a product from a supplier"""
    def post(self, request):
        try:
            supplier_id = request.POST.get('supplier_id')
            material_id = request.POST.get('material_id')
            action = request.POST.get('action')  # 'add' or 'remove'
            
            if not supplier_id or not material_id or not action:
                return JsonResponse({
                    'success': False, 
                    'error': 'Missing required parameters'
                }, status=400)
            
            supplier = Supplier.objects.get(id=supplier_id)
            material = RawMaterial.objects.get(id=material_id)
            
            if action == 'add':
                # Set this supplier as the default for this material
                material.default_supplier = supplier
                material.save()
                return JsonResponse({
                    'success': True,
                    'message': f'Added {material.name} to {supplier.name}'
                })
            elif action == 'remove':
                # Remove this supplier
                material.default_supplier = None
                material.save()
                return JsonResponse({
                    'success': True,
                    'message': f'Removed {material.name} from {supplier.name}'
                })
            else:
                return JsonResponse({
                    'success': False, 
                    'error': 'Invalid action'
                }, status=400)
        except Supplier.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'Supplier not found'
            }, status=404)
        except RawMaterial.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'Material not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': str(e)
            }, status=500)


class GetProductsBySupplier(LoginRequiredMixin, View):
    """Get all products supplied by a specific supplier (dynamic dropdown filter)"""
    def get(self, request):
        supplier_id = request.GET.get('supplier_id')
        
        if not supplier_id:
            return JsonResponse({'products': [], 'error': 'No supplier specified'}, status=400)
        
        try:
            supplier = Supplier.objects.get(id=supplier_id, is_active=True)
            
            # Get all raw materials where this supplier is the default supplier
            materials = RawMaterial.objects.filter(
                default_supplier=supplier,
                is_active=True
            ).select_related('category').order_by('name')
            
            products_list = [
                {
                    'id': m.id,
                    'name': f"{m.name} ({m.unit_of_measure})",
                    'product_code': m.product_code,
                    'category': m.category.name,
                    'unit_of_measure': m.unit_of_measure,
                    'current_unit_price': str(m.current_unit_price),
                }
                for m in materials
            ]
            
            return JsonResponse({'products': products_list, 'count': len(products_list)})
        except Supplier.DoesNotExist:
            return JsonResponse({'products': [], 'error': 'Supplier not found'}, status=404)
        except Exception as e:
            return JsonResponse({'products': [], 'error': str(e)}, status=500)


class RawMaterialCreateView(LoginRequiredMixin, CreateView):
    """Create a new raw material"""
    model = RawMaterial
    form_class = RawMaterialForm
    template_name = 'raw_materials/rawmaterial_form.html'
    success_url = reverse_lazy('raw_materials:material_list')
    
    def form_valid(self, form):
        # Save the raw material
        response = super().form_valid(form)
        
        # Create associated stock record
        Stock.objects.get_or_create(
            raw_material=self.object,
            defaults={
                'quantity_on_hand': 0,
                'quantity_reserved': 0,
                'quantity_damaged': 0,
                'minimum_stock_level': 0,
                'maximum_stock_level': 0,
                'reorder_quantity': 0,
                'lead_time_days': 7,
                'valuation_method': 'FIFO',
                'standard_cost': 0,
                'warehouse_location': '',
            }
        )
        
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Raw Material'
        context['button_text'] = 'Create Material'
        return context


class RawMaterialEditForm(forms.ModelForm):
    """Form for editing raw materials"""
    category = forms.ModelChoiceField(
        queryset=RawMaterialCategory.objects.all().order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
        label='Category'
    )
    
    default_supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.filter(is_active=True).order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Default Supplier',
        required=False
    )
    
    class Meta:
        model = RawMaterial
        fields = ['product_code', 'name', 'description', 'category', 'unit_of_measure', 
                  'hsn_code', 'default_supplier', 'current_unit_price', 'is_active']
        widgets = {
            'product_code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'unit_of_measure': forms.Select(attrs={'class': 'form-control'}),
            'hsn_code': forms.TextInput(attrs={'class': 'form-control'}),
            'current_unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = RawMaterialCategory.objects.all().order_by('name')
        self.fields['default_supplier'].queryset = Supplier.objects.filter(is_active=True).order_by('name')


class RawMaterialUpdateView(LoginRequiredMixin, UpdateView):
    """Edit raw materials from dashboard"""
    model = RawMaterial
    form_class = RawMaterialEditForm
    template_name = 'raw_materials/rawmaterial_edit.html'
    success_url = reverse_lazy('raw_materials:category_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Material - {self.object.name}'
        context['product_code'] = self.object.product_code
        return context


class StockForm(forms.ModelForm):
    """Form for editing stock records"""
    class Meta:
        model = Stock
        fields = ['quantity_on_hand', 'quantity_reserved', 'quantity_damaged', 
                  'minimum_stock_level', 'maximum_stock_level', 'reorder_quantity',
                  'lead_time_days', 'valuation_method', 'standard_cost', 'warehouse_location']
        widgets = {
            'quantity_on_hand': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity_reserved': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity_damaged': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'minimum_stock_level': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'maximum_stock_level': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'reorder_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'lead_time_days': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
            'valuation_method': forms.Select(attrs={'class': 'form-control'}),
            'standard_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'warehouse_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Shelf A1, Bin 42'}),
        }


class StockUpdateView(LoginRequiredMixin, UpdateView):
    """Edit stock records from dashboard"""
    model = Stock
    form_class = StockForm
    template_name = 'raw_materials/stock_form.html'
    success_url = reverse_lazy('raw_materials:stock_levels')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['raw_material'] = self.object.raw_material
        context['title'] = f'Edit Stock - {self.object.raw_material.name}'
        
        # Calculate net available quantity
        net_available = (
            self.object.quantity_on_hand - 
            self.object.quantity_reserved - 
            self.object.quantity_damaged
        )
        context['net_available_qty'] = max(0, net_available)  # Don't show negative values
        
        return context
