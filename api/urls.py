"""API v1 URL configuration"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

# Import API views
from api.auth_views import (
    LoginView, LogoutView, ChangePasswordView,
    ForgotPasswordAPIView, ResetPasswordAPIView,
    VerifyEmailAPIView, UserProfileAPIView,
)
from api.user_views import UserViewSet
from products.views import ProductViewSet, CategoryViewSet, BrandViewSet, UnitViewSet
from warehouses.views import WarehouseViewSet, StockTransferViewSet, WarehouseZoneViewSet
from inventory.views import (
    StockLevelViewSet, StockMovementViewSet, BatchViewSet,
    InventoryAdjustmentViewSet, CycleCountingViewSet,
)
from suppliers.views import SupplierViewSet, SupplierContactViewSet
from purchases.views import (
    PurchaseRequisitionViewSet, PurchaseOrderViewSet,
    GoodsReceiptNoteViewSet, VendorInvoiceViewSet,
)
from sales.views import (
    CustomerViewSet, SalesOrderViewSet, InvoiceViewSet,
    PaymentViewSet, DeliveryNoteViewSet,
)
from forecasting.views import DemandForecastViewSet, StockForecastSnapshotViewSet
from analytics.views import AnalyticsDashboardView, ABCAnalysisView, InventoryTurnoverView
from reports.views import ReportViewSet
from notifications.views import NotificationViewSet
from audit.views import AuditLogViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'units', UnitViewSet, basename='unit')
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'warehouse-zones', WarehouseZoneViewSet, basename='warehouse-zone')
router.register(r'stock-transfers', StockTransferViewSet, basename='stock-transfer')
router.register(r'stock-levels', StockLevelViewSet, basename='stock-level')
router.register(r'stock-movements', StockMovementViewSet, basename='stock-movement')
router.register(r'batches', BatchViewSet, basename='batch')
router.register(r'inventory-adjustments', InventoryAdjustmentViewSet, basename='inventory-adjustment')
router.register(r'cycle-counts', CycleCountingViewSet, basename='cycle-count')
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'supplier-contacts', SupplierContactViewSet, basename='supplier-contact')
router.register(r'purchase-requisitions', PurchaseRequisitionViewSet, basename='purchase-requisition')
router.register(r'purchase-orders', PurchaseOrderViewSet, basename='purchase-order')
router.register(r'grns', GoodsReceiptNoteViewSet, basename='grn')
router.register(r'vendor-invoices', VendorInvoiceViewSet, basename='vendor-invoice')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'sales-orders', SalesOrderViewSet, basename='sales-order')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'delivery-notes', DeliveryNoteViewSet, basename='delivery-note')
router.register(r'demand-forecasts', DemandForecastViewSet, basename='demand-forecast')
router.register(r'stock-snapshots', StockForecastSnapshotViewSet, basename='stock-snapshot')
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='api_login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/logout/', LogoutView.as_view(), name='api_logout'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='api_change_password'),
    path('auth/forgot-password/', ForgotPasswordAPIView.as_view(), name='api_forgot_password'),
    path('auth/reset-password/', ResetPasswordAPIView.as_view(), name='api_reset_password'),
    path('auth/verify-email/<uuid:token>/', VerifyEmailAPIView.as_view(), name='api_verify_email'),
    path('auth/profile/', UserProfileAPIView.as_view(), name='api_user_profile'),
    path('analytics/dashboard/', AnalyticsDashboardView.as_view(), name='analytics_dashboard'),
    path('analytics/abc/', ABCAnalysisView.as_view(), name='abc_analysis'),
    path('analytics/turnover/', InventoryTurnoverView.as_view(), name='inventory_turnover'),
    path('', include(router.urls)),
]
