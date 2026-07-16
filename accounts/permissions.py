"""
RBAC permissions for the SCM platform
"""
from rest_framework.permissions import BasePermission
from accounts.models import UserRole

# ===================== MODULE ACCESS MATRIX =====================
ROLE_MODULE_ACCESS = {
    UserRole.SUPER_ADMIN: [
        'dashboard', 'products', 'warehouses', 'inventory', 'suppliers',
        'purchases', 'sales', 'forecasting', 'analytics', 'reports',
        'notifications', 'audit', 'users', 'settings',
    ],
    UserRole.WAREHOUSE_MANAGER: [
        'dashboard', 'products', 'warehouses', 'inventory',
        'reports', 'notifications',
    ],
    UserRole.PROCUREMENT_MANAGER: [
        'dashboard', 'products', 'suppliers', 'purchases',
        'inventory', 'reports', 'notifications',
    ],
    UserRole.INVENTORY_MANAGER: [
        'dashboard', 'products', 'inventory', 'warehouses',
        'reports', 'notifications',
    ],
    UserRole.SALES_MANAGER: [
        'dashboard', 'products', 'sales', 'inventory',
        'reports', 'notifications',
    ],
    UserRole.FINANCE_MANAGER: [
        'dashboard', 'purchases', 'sales', 'analytics',
        'reports', 'notifications',
    ],
    UserRole.EMPLOYEE: [
        'dashboard', 'products', 'inventory',
    ],
}


class IsSuperAdmin(BasePermission):
    """Only Super Admins"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_super_admin


class IsWarehouseManager(BasePermission):
    """Warehouse Managers and Super Admins"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_super_admin or request.user.is_warehouse_manager
        )


class IsProcurementManager(BasePermission):
    """Procurement Managers and Super Admins"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_super_admin or request.user.is_procurement_manager
        )


class IsInventoryManager(BasePermission):
    """Inventory Managers and Super Admins"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_super_admin or request.user.is_inventory_manager
        )


class IsSalesManager(BasePermission):
    """Sales Managers and Super Admins"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_super_admin or request.user.is_sales_manager
        )


class IsFinanceManager(BasePermission):
    """Finance Managers and Super Admins"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_super_admin or request.user.is_finance_manager
        )


class IsManagerOrReadOnly(BasePermission):
    """Any manager can write; employees can only read"""
    MANAGER_ROLES = [
        UserRole.SUPER_ADMIN, UserRole.WAREHOUSE_MANAGER,
        UserRole.PROCUREMENT_MANAGER, UserRole.INVENTORY_MANAGER,
        UserRole.SALES_MANAGER, UserRole.FINANCE_MANAGER,
    ]

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user.role in self.MANAGER_ROLES


class HasModuleAccess(BasePermission):
    """Check if user has access to the module defined in the view"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        module = getattr(view, 'required_module', None)
        if module is None:
            return True
        return request.user.can_access_module(module)
