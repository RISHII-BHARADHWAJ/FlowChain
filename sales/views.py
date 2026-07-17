"""Sales ViewSets"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend


class CustomerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'code', 'email', 'phone', 'gst_number']
    filterset_fields = ['is_active', 'type']
    ordering_fields = ['name', 'total_revenue', 'total_orders']

    def get_queryset(self):
        from sales.models import Customer
        return Customer.objects.filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        from sales.serializers import CustomerSerializer
        return CustomerSerializer


class SalesOrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'customer', 'warehouse', 'priority']
    search_fields = ['order_number', 'customer__name']
    ordering = ['-created_at']

    def get_queryset(self):
        from sales.models import SalesOrder
        return SalesOrder.objects.select_related('customer', 'warehouse', 'salesperson').filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        from sales.serializers import SalesOrderSerializer
        return SalesOrderSerializer

    def perform_create(self, serializer):
        from core.utils import generate_unique_id
        import datetime
        serializer.save(
            salesperson=self.request.user,
            order_number=generate_unique_id('SO', 8),
            order_date=datetime.date.today(),
        )

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        order = self.get_object()
        order.status = 'confirmed'
        order.save()
        return Response({'status': 'confirmed'})

    @action(detail=True, methods=['get'])
    def generate_invoice(self, request, pk=None):
        order = self.get_object()
        # Invoice generation logic
        return Response({'message': 'Invoice generation triggered'})


class InvoiceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'customer']
    search_fields = ['invoice_number', 'customer__name']
    ordering = ['-created_at']

    def get_queryset(self):
        from sales.models import Invoice
        return Invoice.objects.select_related('customer', 'created_by').filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        from sales.serializers import InvoiceSerializer
        return InvoiceSerializer

    def perform_create(self, serializer):
        from core.utils import generate_unique_id
        serializer.save(
            created_by=self.request.user,
            invoice_number=generate_unique_id('INV', 8),
        )

    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        invoice = self.get_object()
        from sales.services import InvoiceService
        pdf_path = InvoiceService.generate_pdf(invoice)
        from django.http import FileResponse
        return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf',
                            as_attachment=True, filename=f"invoice-{invoice.invoice_number}.pdf")

    @action(detail=True, methods=['post'])
    def send_email(self, request, pk=None):
        invoice = self.get_object()
        from sales.tasks import send_invoice_email
        send_invoice_email.delay(str(invoice.id))
        return Response({'message': 'Invoice email queued'})


class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['customer', 'payment_method']
    ordering = ['-created_at']

    def get_queryset(self):
        from sales.models import Payment
        return Payment.objects.select_related('customer', 'invoice').filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        from sales.serializers import PaymentSerializer
        return PaymentSerializer

    def perform_create(self, serializer):
        from core.utils import generate_unique_id
        payment = serializer.save(
            received_by=self.request.user,
            payment_number=generate_unique_id('PMT', 8),
        )
        # Update invoice paid amount
        invoice = payment.invoice
        invoice.paid_amount += payment.amount
        if invoice.paid_amount >= invoice.total_amount:
            invoice.status = 'paid'
        elif invoice.paid_amount > 0:
            invoice.status = 'partial'
        invoice.save()


class DeliveryNoteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'customer']
    ordering = ['-created_at']

    def get_queryset(self):
        from sales.models import DeliveryNote
        return DeliveryNote.objects.select_related('customer', 'sales_order').filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        from sales.serializers import DeliveryNoteSerializer
        return DeliveryNoteSerializer
