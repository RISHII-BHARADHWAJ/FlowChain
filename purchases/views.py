"""Purchases ViewSets"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from accounts.permissions import IsProcurementManager


class PurchaseRequisitionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'warehouse', 'priority']
    search_fields = ['pr_number', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        from purchases.models import PurchaseRequisition
        return PurchaseRequisition.objects.select_related(
            'warehouse', 'requested_by'
        ).filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        from purchases.serializers import PurchaseRequisitionSerializer
        return PurchaseRequisitionSerializer

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        pr = self.get_object()
        pr.status = 'approved'
        pr.approved_by = request.user
        pr.save()
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        pr = self.get_object()
        pr.status = 'rejected'
        pr.rejection_reason = request.data.get('reason', '')
        pr.save()
        return Response({'status': 'rejected'})


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'supplier', 'warehouse', 'priority']
    search_fields = ['po_number', 'supplier__name']
    ordering = ['-created_at']

    def get_queryset(self):
        from purchases.models import PurchaseOrder
        return PurchaseOrder.objects.select_related(
            'supplier', 'warehouse', 'created_by'
        ).filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        from purchases.serializers import PurchaseOrderSerializer
        return PurchaseOrderSerializer

    def perform_create(self, serializer):
        import datetime
        from core.utils import generate_unique_id
        serializer.save(
            created_by=self.request.user,
            po_number=generate_unique_id('PO', 8),
            order_date=datetime.date.today(),
        )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        from django.utils import timezone
        po = self.get_object()
        po.status = 'approved'
        po.approved_by = request.user
        po.approved_at = timezone.now()
        po.save()
        return Response({'status': 'approved'})


class GoodsReceiptNoteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'warehouse', 'supplier']
    ordering = ['-created_at']

    def get_queryset(self):
        from purchases.models import GoodsReceiptNote
        return GoodsReceiptNote.objects.select_related(
            'purchase_order', 'supplier', 'warehouse'
        ).filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        from purchases.serializers import GoodsReceiptNoteSerializer
        return GoodsReceiptNoteSerializer


class VendorInvoiceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'supplier']
    ordering = ['-created_at']

    def get_queryset(self):
        from purchases.models import VendorInvoice
        return VendorInvoice.objects.select_related('supplier').filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        from purchases.serializers import VendorInvoiceSerializer
        return VendorInvoiceSerializer
