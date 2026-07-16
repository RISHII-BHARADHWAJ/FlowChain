"""Products template views"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from core.utils import paginate_queryset
import csv


@login_required
def product_list(request):
    from products.models import Product, Category
    qs = Product.objects.select_related('category', 'brand', 'unit').filter(deleted_at__isnull=True)

    # Filters
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    status = request.GET.get('status', '')
    ordering = request.GET.get('ordering', 'name')

    if search:
        qs = qs.filter(name__icontains=search) | qs.filter(sku__icontains=search) | qs.filter(barcode__icontains=search)
    if category:
        qs = qs.filter(category__id=category)
    if status:
        qs = qs.filter(status=status)
    if ordering:
        qs = qs.order_by(ordering)

    products, paginator = paginate_queryset(qs, request.GET.get('page', 1), 25)
    categories = Category.objects.filter(is_active=True).order_by('name')

    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        'total_count': paginator.count,
        'category_count': categories.count(),
    })


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, deleted_at__isnull=True)
    from inventory.models import StockLevel, StockMovement
    stock_levels = StockLevel.objects.filter(product=product).select_related('warehouse')
    recent_movements = StockMovement.objects.filter(product=product).order_by('-created_at')[:10]
    return render(request, 'products/product_detail.html', {
        'product': product,
        'stock_levels': stock_levels,
        'recent_movements': recent_movements,
    })


@login_required
def product_create(request):
    from products.models import Category, Brand, Unit
    from products.forms import ProductForm
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" created successfully.')
            return redirect('products:product_detail', pk=product.pk)
    else:
        form = ProductForm()
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    units = Unit.objects.filter(is_active=True)
    return render(request, 'products/product_form.html', {
        'form': form, 'categories': categories, 'brands': brands, 'units': units,
        'title': 'Add New Product',
    })


@login_required
def product_edit(request, pk):
    from products.models import Product, Category, Brand, Unit
    from products.forms import ProductForm
    product = get_object_or_404(Product, pk=pk, deleted_at__isnull=True)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" updated successfully.')
            return redirect('products:product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    units = Unit.objects.filter(is_active=True)
    return render(request, 'products/product_form.html', {
        'form': form, 'product': product, 'categories': categories, 'brands': brands, 'units': units,
        'title': f'Edit: {product.name}',
    })


@login_required
def download_template(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="product_import_template.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'SKU', 'Name', 'Description', 'Category Code', 'Brand', 'Unit',
        'HSN Code', 'Tax Rate', 'Cost Price', 'Selling Price', 'MRP',
        'Minimum Stock', 'Maximum Stock', 'Reorder Point', 'Weight', 'Status'
    ])
    writer.writerow([
        'SKU001', 'Sample Product', 'A sample product', 'ELEC', 'Sony', 'PCS',
        '8471', '18', '1000', '1500', '1800', '10', '500', '20', '0.5', 'active'
    ])
    return response
