from django.urls import path
from inventory import template_views as views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_list, name='inventory_list'),
]
