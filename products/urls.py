"""Product URL configuration"""
from django.urls import path
from products import template_views as views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('new/', views.product_create, name='product_create'),
    path('<uuid:pk>/', views.product_detail, name='product_detail'),
    path('<uuid:pk>/edit/', views.product_edit, name='product_edit'),
    path('template/', views.download_template, name='download_template'),
]
