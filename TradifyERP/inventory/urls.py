from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Products
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/create/', views.product_create, name='product_create'),
    path('product/<int:pk>/edit/', views.product_edit, name='product_edit'),
    
    # Stock
    path('stock/', views.stock_list, name='stock_list'),
    
    # Warehouses
    path('warehouses/', views.warehouse_list, name='warehouse_list'),
    
    # Purchase Orders
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),
    path('purchase-order/<int:pk>/', views.purchase_order_detail, name='purchase_order_detail'),
    
    # Stock Movements
    path('stock-movements/', views.stock_movement_list, name='stock_movement_list'),
    
    # Reports
    path('reports/low-stock/', views.low_stock_report, name='low_stock_report'),
]
