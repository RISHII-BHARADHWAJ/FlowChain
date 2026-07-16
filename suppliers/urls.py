from django.urls import path
from suppliers import template_views as views

app_name = 'suppliers'

urlpatterns = [
    path('', views.supplier_list, name='supplier_list'),
]
