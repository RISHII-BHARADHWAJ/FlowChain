"""
Global context processors for templates
"""
from django.conf import settings
from inventory.models import StockLevel
from notifications.models import Notification


def global_settings(request):
    """Inject global settings into all templates"""
    context = {
        'COMPANY_NAME': getattr(settings, 'COMPANY_NAME', 'FlowChain'),
        'COMPANY_LOGO': getattr(settings, 'COMPANY_LOGO', ''),
        'CURRENCY': getattr(settings, 'CURRENCY', 'INR'),
        'CURRENCY_SYMBOL': getattr(settings, 'CURRENCY_SYMBOL', '₹'),
        'DEBUG': settings.DEBUG,
    }
    return context
