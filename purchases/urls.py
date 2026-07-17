from django.urls import path
from purchases import template_views as views

app_name = 'purchases'

urlpatterns = [
    path('', views.purchase_order_list, name='purchase_order_list'),
]
