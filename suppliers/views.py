"""Suppliers ViewSets & serializers"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend


class SupplierViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'type', 'is_preferred', 'blacklisted']
    search_fields = ['name', 'code', 'gst_number', 'email']
    ordering_fields = ['name', 'rating', 'total_orders']

    def get_queryset(self):
        from suppliers.models import Supplier
        return Supplier.objects.filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        from suppliers.serializers import SupplierSerializer
        return SupplierSerializer


class SupplierContactViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        from suppliers.models import SupplierContact
        return SupplierContact.objects.select_related('supplier')

    def get_serializer_class(self):
        from suppliers.serializers import SupplierContactSerializer
        return SupplierContactSerializer
