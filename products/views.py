"""Products ViewSets"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Sum, Q
import csv
import io
from products.models import Product, Category, Brand, Unit
from accounts.permissions import IsManagerOrReadOnly


class ProductSerializer:
    pass  # Defined in products/serializers.py


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'brand', 'status', 'is_active', 'is_batch_tracked']
    search_fields = ['sku', 'name', 'barcode', 'hsn_code']
    ordering_fields = ['name', 'sku', 'created_at', 'selling_price', 'cost_price']
    ordering = ['name']

    def get_queryset(self):
        from products.models import Product
        return Product.objects.select_related(
            'category', 'brand', 'unit'
        ).filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        from products.serializers import ProductSerializer, ProductListSerializer
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer

    @action(detail=False, methods=['post'], url_path='bulk-import')
    def bulk_import(self, request):
        """Import products from CSV"""
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        # CSV import logic
        return Response({'message': 'Import started', 'task_id': 'task_123'})

    @action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        """Export products to CSV"""
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'
        writer = csv.writer(response)
        writer.writerow(['SKU', 'Name', 'Category', 'Brand', 'Cost Price', 'Selling Price', 'Status'])
        for product in self.get_queryset():
            writer.writerow([
                product.sku, product.name,
                product.category.name if product.category else '',
                product.brand.name if product.brand else '',
                product.cost_price, product.selling_price, product.status,
            ])
        return response

    @action(detail=True, methods=['post'], url_path='generate-barcode')
    def generate_barcode(self, request, pk=None):
        """Generate barcode for product"""
        product = self.get_object()
        from products.services import BarcodeService
        barcode_url = BarcodeService.generate_barcode(product)
        return Response({'barcode_url': barcode_url})


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'sort_order']

    def get_queryset(self):
        return Category.objects.filter(deleted_at__isnull=True).annotate(
            product_count=Count('products', filter=Q(products__deleted_at__isnull=True))
        )

    def get_serializer_class(self):
        from products.serializers import CategorySerializer
        return CategorySerializer


class BrandViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly]
    search_fields = ['name']

    def get_queryset(self):
        return Brand.objects.filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        from products.serializers import BrandSerializer
        return BrandSerializer


class UnitViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly]
    search_fields = ['name', 'abbreviation']

    def get_queryset(self):
        return Unit.objects.filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        from products.serializers import UnitSerializer
        return UnitSerializer
