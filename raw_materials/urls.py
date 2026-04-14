from django.urls import path
from . import views

app_name = 'raw_materials'

urlpatterns = [
    # Dashboard
    path('', views.RawMaterialsDashboardView.as_view(), name='dashboard'),
    
    # Raw Materials
    path('materials/', views.RawMaterialListView.as_view(), name='material_list'),
    path('materials/add/', views.RawMaterialCreateView.as_view(), name='material_create'),
    path('materials/<int:pk>/edit/', views.RawMaterialUpdateView.as_view(), name='material_edit'),
    
    # API
    path('api/materials-by-category/', views.GetMaterialsByCategory.as_view(), name='materials_by_category'),
    path('api/materials-by-supplier/', views.GetMaterialsBySupplier.as_view(), name='materials_by_supplier'),
    path('api/products-by-supplier/', views.GetProductsBySupplier.as_view(), name='products_by_supplier'),
    path('api/update-supplier-product/', views.UpdateSupplierProduct.as_view(), name='update_supplier_product'),
    
    # Suppliers
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/add/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='supplier_edit'),
    
    # Stock Levels
    path('stock/', views.StockLevelView.as_view(), name='stock_levels'),
    path('stock/<int:pk>/edit/', views.StockUpdateView.as_view(), name='stock_edit'),
    
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
]
