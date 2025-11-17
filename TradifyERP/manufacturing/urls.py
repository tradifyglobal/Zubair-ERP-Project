"""
Manufacturing Module URL Configuration
Complete URL routing for manufacturing module views.
"""

from django.urls import path
from . import views

app_name = 'manufacturing'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.ManufacturingDashboardView.as_view(), name='dashboard'),
    
    # Product Category URLs
    path('categories/', views.ProductCategoryListView.as_view(), name='productcategory_list'),
    path('categories/new/', views.ProductCategoryCreateView.as_view(), name='productcategory_create'),
    path('categories/<int:pk>/delete/', views.ProductCategoryDeleteView.as_view(), name='productcategory_delete'),
    
    # Product URLs
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/new/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    
    # Raw Material URLs
    path('materials/', views.RawMaterialListView.as_view(), name='rawmaterial_list'),
    path('materials/new/', views.RawMaterialCreateView.as_view(), name='rawmaterial_create'),
    path('materials/<int:pk>/delete/', views.RawMaterialDeleteView.as_view(), name='rawmaterial_delete'),
    
    # Bill of Materials URLs
    path('bom/', views.BOMListView.as_view(), name='bom_list'),
    path('bom/new/', views.BOMCreateView.as_view(), name='bom_create'),
    path('bom/<int:pk>/edit/', views.BOMUpdateView.as_view(), name='bom_update'),
    path('bom/<int:pk>/delete/', views.BOMDeleteView.as_view(), name='bom_delete'),
    
    # Work Center URLs
    path('work-centers/', views.WorkCenterListView.as_view(), name='workcenter_list'),
    path('work-centers/new/', views.WorkCenterCreateView.as_view(), name='workcenter_create'),
    path('work-centers/<int:pk>/delete/', views.WorkCenterDeleteView.as_view(), name='workcenter_delete'),
    
    # Routing URLs
    path('routings/', views.RoutingListView.as_view(), name='routing_list'),
    path('routings/new/', views.RoutingCreateView.as_view(), name='routing_create'),
    path('routings/<int:pk>/edit/', views.RoutingUpdateView.as_view(), name='routing_update'),
    path('routings/<int:pk>/delete/', views.RoutingDeleteView.as_view(), name='routing_delete'),
    
    # Production Order URLs
    path('production-orders/', views.ProductionOrderListView.as_view(), name='productionorder_list'),
    path('production-orders/new/', views.ProductionOrderCreateView.as_view(), name='productionorder_create'),
    path('production-orders/<int:pk>/edit/', views.ProductionOrderUpdateView.as_view(), name='productionorder_update'),
    path('production-orders/<int:pk>/delete/', views.ProductionOrderDeleteView.as_view(), name='productionorder_delete'),
    
    # Quality Inspection URLs
    path('inspections/', views.QualityInspectionListView.as_view(), name='qualityinspection_list'),
    path('inspections/new/', views.QualityInspectionCreateView.as_view(), name='qualityinspection_create'),
    path('inspections/<int:pk>/edit/', views.QualityInspectionUpdateView.as_view(), name='qualityinspection_update'),
    path('inspections/<int:pk>/delete/', views.QualityInspectionDeleteView.as_view(), name='qualityinspection_delete'),
    
    # Equipment URLs
    path('equipment/', views.EquipmentListView.as_view(), name='equipment_list'),
    path('equipment/new/', views.EquipmentCreateView.as_view(), name='equipment_create'),
    path('equipment/<int:pk>/delete/', views.EquipmentDeleteView.as_view(), name='equipment_delete'),
]
