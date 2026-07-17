from django.urls import path
from audit import template_views as views

app_name = 'audit'

urlpatterns = [
    path('', views.audit_list, name='audit_list'),
]
