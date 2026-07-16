"""Core app utilities"""
import uuid
import random
import string
from decimal import Decimal
from django.utils.text import slugify


def generate_unique_id(prefix='', length=8):
    """Generate a unique ID with optional prefix"""
    chars = string.ascii_uppercase + string.digits
    unique = ''.join(random.choices(chars, k=length))
    return f"{prefix}{unique}" if prefix else unique


def generate_sku(product_name, category_code='GEN'):
    """Generate SKU from product name and category"""
    name_part = product_name[:3].upper().replace(' ', '')
    uid = generate_unique_id(length=6)
    return f"{category_code}-{name_part}-{uid}"


def calculate_tax(amount, tax_rate):
    """Calculate tax amount"""
    return Decimal(str(amount)) * Decimal(str(tax_rate)) / Decimal('100')


def calculate_profit_margin(cost_price, selling_price):
    """Calculate profit margin percentage"""
    if cost_price == 0:
        return Decimal('0')
    profit = selling_price - cost_price
    return (profit / cost_price) * 100


def format_currency(amount, currency_symbol='₹'):
    """Format amount as currency string"""
    return f"{currency_symbol}{amount:,.2f}"


def paginate_queryset(queryset, page, page_size=25):
    """Simple queryset pagination"""
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(queryset, page_size)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    return items, paginator


def get_date_range(period='month'):
    """Get date range for a given period"""
    from django.utils import timezone
    from datetime import timedelta
    now = timezone.now()
    if period == 'day':
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'week':
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'month':
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == 'quarter':
        month = ((now.month - 1) // 3) * 3 + 1
        start = now.replace(month=month, day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == 'year':
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start = now - timedelta(days=30)
    return start, now


def safe_divide(numerator, denominator, default=0):
    """Safe division that returns default on division by zero"""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default
