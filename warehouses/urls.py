from django.urls import path
from warehouses import template_views as views

app_name = 'warehouses'

urlpatterns = [
    path('', views.warehouse_list, name='warehouse_list'),
]
