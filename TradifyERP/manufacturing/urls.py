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
    
    # Distributor URLs
    path('distributors/', views.DistributorListView.as_view(), name='distributor_list'),
    path('distributors/new/', views.DistributorCreateView.as_view(), name='distributor_create'),
    path('distributors/<int:pk>/edit/', views.DistributorUpdateView.as_view(), name='distributor_update'),
    path('distributors/<int:pk>/delete/', views.DistributorDeleteView.as_view(), name='distributor_delete'),
    
    # Distributor Order URLs
    path('orders/', views.DistributorOrderListView.as_view(), name='distributororder_list'),
    path('orders/new/', views.DistributorOrderCreateView.as_view(), name='distributororder_create'),
    path('orders/<int:pk>/edit/', views.DistributorOrderUpdateView.as_view(), name='distributororder_update'),
    path('orders/<int:pk>/delete/', views.DistributorOrderDeleteView.as_view(), name='distributororder_delete'),
    
    # Order Shipment URLs
    path('shipments/', views.OrderShipmentListView.as_view(), name='ordershipment_list'),
    path('shipments/new/', views.OrderShipmentCreateView.as_view(), name='ordershipment_create'),
    path('shipments/<int:pk>/edit/', views.OrderShipmentUpdateView.as_view(), name='ordershipment_update'),
    path('shipments/<int:pk>/delete/', views.OrderShipmentDeleteView.as_view(), name='ordershipment_delete'),
    
    # After-Sales Service URLs
    path('services/', views.AfterSalesServiceListView.as_view(), name='aftersalesservice_list'),
    path('services/new/', views.AfterSalesServiceCreateView.as_view(), name='aftersalesservice_create'),
    path('services/<int:pk>/edit/', views.AfterSalesServiceUpdateView.as_view(), name='aftersalesservice_update'),
    path('services/<int:pk>/delete/', views.AfterSalesServiceDeleteView.as_view(), name='aftersalesservice_delete'),
    
    # Warranty Registration URLs
    path('warranties/', views.WarrantyRegistrationListView.as_view(), name='warrantyregistration_list'),
    path('warranties/new/', views.WarrantyRegistrationCreateView.as_view(), name='warrantyregistration_create'),
    path('warranties/<int:pk>/edit/', views.WarrantyRegistrationUpdateView.as_view(), name='warrantyregistration_update'),
    path('warranties/<int:pk>/delete/', views.WarrantyRegistrationDeleteView.as_view(), name='warrantyregistration_delete'),
    
    # Distributor Performance URLs
    path('performance/', views.DistributorPerformanceListView.as_view(), name='distributorperformance_list'),
    path('performance/new/', views.DistributorPerformanceCreateView.as_view(), name='distributorperformance_create'),
    path('performance/<int:pk>/edit/', views.DistributorPerformanceUpdateView.as_view(), name='distributorperformance_update'),
    path('performance/<int:pk>/delete/', views.DistributorPerformanceDeleteView.as_view(), name='distributorperformance_delete'),
]
