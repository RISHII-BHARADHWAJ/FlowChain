"""Products serializers"""
from rest_framework import serializers
from products.models import Product, Category, Brand, Unit, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'code', 'description', 'parent', 'image',
                  'is_active', 'sort_order', 'product_count', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'description', 'logo', 'is_active', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name', 'abbreviation', 'type', 'is_active']
        read_only_fields = ['id']


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True, allow_null=True)
    unit_name = serializers.CharField(source='unit.abbreviation', read_only=True)
    profit_margin = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'barcode', 'name', 'category_name', 'brand_name',
            'unit_name', 'cost_price', 'selling_price', 'profit_margin',
            'minimum_stock', 'reorder_point', 'status', 'image', 'created_at',
        ]


class ProductSerializer(serializers.ModelSerializer):
    """Full product serializer"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True, allow_null=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    profit_margin = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'barcode', 'qr_code', 'name', 'slug', 'description',
            'short_description', 'category', 'category_name', 'brand', 'brand_name',
            'unit', 'unit_name', 'hsn_code', 'tax_rate', 'cost_price',
            'selling_price', 'mrp', 'discount_percentage', 'minimum_stock',
            'maximum_stock', 'reorder_point', 'reorder_quantity', 'safety_stock',
            'weight', 'weight_unit', 'length', 'width', 'height', 'dimension_unit',
            'is_batch_tracked', 'is_lot_tracked', 'is_expiry_tracked',
            'shelf_life_days', 'image', 'status', 'is_active',
            'is_purchasable', 'is_sellable', 'tags', 'notes',
            'profit_margin', 'images', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def get_profit_margin(self, obj):
        return round(obj.profit_margin, 2)

    def get_images(self, obj):
        return [{'id': str(img.id), 'url': img.image.url, 'alt_text': img.alt_text}
                for img in obj.images.all()[:5]]
