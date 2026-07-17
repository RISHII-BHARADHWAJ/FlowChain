from django.urls import path
from sales import template_views as views

app_name = 'sales'

urlpatterns = [
    path('', views.sales_order_list, name='sales_order_list'),
    path('invoices/', views.invoice_list, name='invoice_list'),
]
