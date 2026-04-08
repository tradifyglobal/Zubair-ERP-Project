from django.urls import path
from . import views
from . import views_p2p_dashboard

app_name = 'procurement'

urlpatterns = [
    # Purchase Orders
    path('po/', views.PurchaseOrderListView.as_view(), name='po_list'),
    path('po/create/', views.PurchaseOrderCreateView.as_view(), name='po_create'),
    path('po/<int:pk>/', views.PurchaseOrderDetailView.as_view(), name='po_detail'),
    path('po/<int:pk>/edit/', views.PurchaseOrderUpdateView.as_view(), name='po_update'),
    path('po/<int:pk>/approve/', views.PurchaseOrderApproveView.as_view(), name='po_approve'),
    
    # Goods Receipts
    path('receipts/', views.GoodsReceiptListView.as_view(), name='receipt_list'),
    path('receipts/create/', views.GoodsReceiptCreateView.as_view(), name='receipt_create'),
    path('receipts/<int:pk>/', views.GoodsReceiptDetailView.as_view(), name='receipt_detail'),
    path('receipts/<int:pk>/edit/', views.GoodsReceiptUpdateView.as_view(), name='receipt_update'),
    
    # Request for Quotation
    path('rfq/', views.RequestForQuotationListView.as_view(), name='rfq_list'),
    path('rfq/create/', views.RequestForQuotationCreateView.as_view(), name='rfq_create'),
    path('rfq/<int:pk>/', views.RequestForQuotationDetailView.as_view(), name='rfq_detail'),
    
    # Vendor Quotations
    path('quotations/', views.VendorQuotationListView.as_view(), name='quotation_list'),
    
    # 3-Way Matching
    path('matching/', views.ThreeWayMatchingListView.as_view(), name='matching_list'),
    path('matching/<int:pk>/', views.ThreeWayMatchingDetailView.as_view(), name='matching_detail'),
    
    # Raw Material Purchase Orders
    path('po/raw-material/create/', views.RawMaterialPurchaseOrderCreateView.as_view(), name='rm_po_create'),
    path('po/<int:po_id>/add-raw-material/', views.RawMaterialPOLineItemAddView.as_view(), name='rm_po_add_item'),
    
    # Procurement Dashboard
    path('dashboard/', views.ProcurementDashboardView.as_view(), name='dashboard'),
    
    # P2P Dashboard (Procure-to-Pay)
    path('p2p/', views_p2p_dashboard.P2PDashboardView.as_view(), name='p2p_dashboard'),
    path('p2p/<int:pk>/', views_p2p_dashboard.P2PDetailsView.as_view(), name='p2p_details'),
    path('p2p-comparison/', views_p2p_dashboard.p2p_comparison_view, name='p2p_comparison'),
]
