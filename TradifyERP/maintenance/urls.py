from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    # Dashboard
    path('', views.MaintenanceDashboardView.as_view(), name='dashboard'),
    
    # Maintenance Asset URLs
    path('assets/', views.MaintenanceAssetListView.as_view(), name='asset-list'),
    path('assets/<int:pk>/', views.MaintenanceAssetDetailView.as_view(), name='asset-detail'),
    path('assets/new/', views.MaintenanceAssetCreateView.as_view(), name='asset-create'),
    path('assets/<int:pk>/edit/', views.MaintenanceAssetUpdateView.as_view(), name='asset-update'),
    path('assets/<int:pk>/delete/', views.MaintenanceAssetDeleteView.as_view(), name='asset-delete'),
    
    # Maintenance Task URLs
    path('tasks/', views.MaintenanceTaskListView.as_view(), name='task-list'),
    path('tasks/<int:pk>/', views.MaintenanceTaskDetailView.as_view(), name='task-detail'),
    path('tasks/new/', views.MaintenanceTaskCreateView.as_view(), name='task-create'),
    path('tasks/<int:pk>/edit/', views.MaintenanceTaskUpdateView.as_view(), name='task-update'),
    path('tasks/<int:pk>/delete/', views.MaintenanceTaskDeleteView.as_view(), name='task-delete'),
    
    # Work Order URLs
    path('work-orders/', views.WorkOrderListView.as_view(), name='workorder-list'),
    path('work-orders/<int:pk>/', views.WorkOrderDetailView.as_view(), name='workorder-detail'),
    path('work-orders/new/', views.WorkOrderCreateView.as_view(), name='workorder-create'),
    path('work-orders/<int:pk>/edit/', views.WorkOrderUpdateView.as_view(), name='workorder-update'),
    path('work-orders/<int:pk>/delete/', views.WorkOrderDeleteView.as_view(), name='workorder-delete'),
    
    # Spare Part URLs
    path('spare-parts/', views.SparePartListView.as_view(), name='sparepart-list'),
    path('spare-parts/<int:pk>/', views.SparePartDetailView.as_view(), name='sparepart-detail'),
    path('spare-parts/new/', views.SparePartCreateView.as_view(), name='sparepart-create'),
    path('spare-parts/<int:pk>/edit/', views.SparePartUpdateView.as_view(), name='sparepart-update'),
    path('spare-parts/<int:pk>/delete/', views.SparePartDeleteView.as_view(), name='sparepart-delete'),
    
    # Maintenance Vendor URLs
    path('vendors/', views.MaintenanceVendorListView.as_view(), name='vendor-list'),
    path('vendors/<int:pk>/', views.MaintenanceVendorDetailView.as_view(), name='vendor-detail'),
    path('vendors/new/', views.MaintenanceVendorCreateView.as_view(), name='vendor-create'),
    path('vendors/<int:pk>/edit/', views.MaintenanceVendorUpdateView.as_view(), name='vendor-update'),
    path('vendors/<int:pk>/delete/', views.MaintenanceVendorDeleteView.as_view(), name='vendor-delete'),
    
    # Vendor Contract URLs
    path('contracts/', views.VendorContractListView.as_view(), name='contract-list'),
    path('contracts/<int:pk>/', views.VendorContractDetailView.as_view(), name='contract-detail'),
    path('contracts/new/', views.VendorContractCreateView.as_view(), name='contract-create'),
    path('contracts/<int:pk>/edit/', views.VendorContractUpdateView.as_view(), name='contract-update'),
    path('contracts/<int:pk>/delete/', views.VendorContractDeleteView.as_view(), name='contract-delete'),
    
    # Compliance Standard URLs
    path('standards/', views.ComplianceStandardListView.as_view(), name='standard-list'),
    path('standards/<int:pk>/', views.ComplianceStandardDetailView.as_view(), name='standard-detail'),
    path('standards/new/', views.ComplianceStandardCreateView.as_view(), name='standard-create'),
    path('standards/<int:pk>/edit/', views.ComplianceStandardUpdateView.as_view(), name='standard-update'),
    path('standards/<int:pk>/delete/', views.ComplianceStandardDeleteView.as_view(), name='standard-delete'),
    
    # Compliance Audit URLs
    path('audits/', views.ComplianceAuditListView.as_view(), name='audit-list'),
    path('audits/<int:pk>/', views.ComplianceAuditDetailView.as_view(), name='audit-detail'),
    path('audits/new/', views.ComplianceAuditCreateView.as_view(), name='audit-create'),
    path('audits/<int:pk>/edit/', views.ComplianceAuditUpdateView.as_view(), name='audit-update'),
    path('audits/<int:pk>/delete/', views.ComplianceAuditDeleteView.as_view(), name='audit-delete'),
    
    # Maintenance Cost URLs
    path('costs/', views.MaintenanceCostListView.as_view(), name='cost-list'),
    path('costs/<int:pk>/', views.MaintenanceCostDetailView.as_view(), name='cost-detail'),
    path('costs/new/', views.MaintenanceCostCreateView.as_view(), name='cost-create'),
    path('costs/<int:pk>/edit/', views.MaintenanceCostUpdateView.as_view(), name='cost-update'),
    path('costs/<int:pk>/delete/', views.MaintenanceCostDeleteView.as_view(), name='cost-delete'),
    
    # Downtime Record URLs
    path('downtime/', views.DowntimeRecordListView.as_view(), name='downtime-list'),
    path('downtime/<int:pk>/', views.DowntimeRecordDetailView.as_view(), name='downtime-detail'),
    path('downtime/new/', views.DowntimeRecordCreateView.as_view(), name='downtime-create'),
    path('downtime/<int:pk>/edit/', views.DowntimeRecordUpdateView.as_view(), name='downtime-update'),
    path('downtime/<int:pk>/delete/', views.DowntimeRecordDeleteView.as_view(), name='downtime-delete'),
]
