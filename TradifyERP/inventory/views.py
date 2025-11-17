from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, F, Count
from django.core.paginator import Paginator
from .models import (
    Category, Product, Warehouse, Stock, StockMovement,
    PurchaseOrder, PurchaseOrderLine, InventoryAdjustment, InventoryAdjustmentLine
)


@login_required
def dashboard(request):
    """Inventory Dashboard"""
    context = {
        'total_products': Product.objects.filter(status='active').count(),
        'total_warehouses': Warehouse.objects.filter(is_active=True).count(),
        'low_stock_items': Stock.objects.filter(
            quantity_available__lte=F('product__reorder_level')
        ).select_related('product', 'warehouse').count(),
        'pending_orders': PurchaseOrder.objects.filter(status__in=['draft', 'pending', 'confirmed']).count(),
    }
    return render(request, 'inventory/dashboard.html', context)


@login_required
def product_list(request):
    """List all products"""
    products = Product.objects.select_related('category')
    
    # Filters
    category_id = request.GET.get('category')
    status = request.GET.get('status')
    search = request.GET.get('search')
    
    if category_id:
        products = products.filter(category_id=category_id)
    if status:
        products = products.filter(status=status)
    if search:
        products = products.filter(Q(sku__icontains=search) | Q(name__icontains=search))
    
    paginator = Paginator(products, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'search': search,
        'status': status,
    }
    return render(request, 'inventory/product_list.html', context)


@login_required
def product_detail(request, pk):
    """Product detail with stock levels"""
    product = get_object_or_404(Product, pk=pk)
    stocks = Stock.objects.filter(product=product).select_related('warehouse')
    movements = StockMovement.objects.filter(product=product).order_by('-created_at')[:20]
    
    context = {
        'product': product,
        'stocks': stocks,
        'movements': movements,
        'total_on_hand': stocks.aggregate(Sum('quantity_on_hand'))['quantity_on_hand__sum'] or 0,
        'total_available': stocks.aggregate(Sum('quantity_available'))['quantity_available__sum'] or 0,
    }
    return render(request, 'inventory/product_detail.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def product_create(request):
    """Create new product"""
    if request.method == 'POST':
        try:
            product = Product.objects.create(
                sku=request.POST.get('sku'),
                name=request.POST.get('name'),
                description=request.POST.get('description'),
                category_id=request.POST.get('category'),
                cost_price=request.POST.get('cost_price'),
                selling_price=request.POST.get('selling_price'),
                reorder_level=request.POST.get('reorder_level', 10),
                reorder_quantity=request.POST.get('reorder_quantity', 50),
            )
            messages.success(request, f'Product {product.sku} created successfully')
            return redirect('inventory:product_detail', pk=product.pk)
        except Exception as e:
            messages.error(request, f'Error creating product: {str(e)}')
    
    context = {
        'categories': Category.objects.all(),
    }
    return render(request, 'inventory/product_form.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def product_edit(request, pk):
    """Edit existing product"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        try:
            product.sku = request.POST.get('sku', product.sku)
            product.name = request.POST.get('name', product.name)
            product.description = request.POST.get('description', product.description)
            product.category_id = request.POST.get('category', product.category_id)
            product.cost_price = request.POST.get('cost_price', product.cost_price)
            product.selling_price = request.POST.get('selling_price', product.selling_price)
            product.reorder_level = request.POST.get('reorder_level', product.reorder_level)
            product.reorder_quantity = request.POST.get('reorder_quantity', product.reorder_quantity)
            product.status = request.POST.get('status', product.status)
            product.save()
            messages.success(request, f'Product {product.sku} updated successfully')
            return redirect('inventory:product_detail', pk=product.pk)
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
    
    context = {
        'product': product,
        'categories': Category.objects.all(),
        'is_edit': True,
    }
    return render(request, 'inventory/product_form.html', context)


@login_required
def stock_list(request):
    """List stock by warehouse (read-only)"""
    stocks = Stock.objects.select_related('product', 'warehouse')
    
    warehouse_id = request.GET.get('warehouse')
    if warehouse_id:
        stocks = stocks.filter(warehouse_id=warehouse_id)
    
    paginator = Paginator(stocks, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'warehouses': Warehouse.objects.filter(is_active=True),
        'readonly': True,  # Stock levels are read-only
    }
    return render(request, 'inventory/stock_list.html', context)


@login_required
def warehouse_list(request):
    """List all warehouses"""
    warehouses = Warehouse.objects.all().annotate(
        total_products=Count('stocks')
    )
    
    context = {
        'warehouses': warehouses,
    }
    return render(request, 'inventory/warehouse_list.html', context)


@login_required
def purchase_order_list(request):
    """List purchase orders"""
    orders = PurchaseOrder.objects.select_related('warehouse')
    
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status': status,
    }
    return render(request, 'inventory/purchase_order_list.html', context)


@login_required
def purchase_order_detail(request, pk):
    """Purchase order detail"""
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    lines = purchase_order.lines.select_related('product')
    
    context = {
        'purchase_order': purchase_order,
        'lines': lines,
    }
    return render(request, 'inventory/purchase_order_detail.html', context)


@login_required
def stock_movement_list(request):
    """List stock movements"""
    movements = StockMovement.objects.select_related('product', 'warehouse')
    
    movement_type = request.GET.get('type')
    if movement_type:
        movements = movements.filter(movement_type=movement_type)
    
    paginator = Paginator(movements, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'movement_type': movement_type,
    }
    return render(request, 'inventory/stock_movement_list.html', context)


@login_required
def low_stock_report(request):
    """Report of items with low stock"""
    low_stock = Stock.objects.filter(
        quantity_available__lte=F('product__reorder_level')
    ).select_related('product', 'warehouse').order_by('quantity_available')
    
    context = {
        'low_stock': low_stock,
    }
    return render(request, 'inventory/low_stock_report.html', context)
