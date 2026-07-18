from django.urls import path
from reports import template_views as views

app_name = 'reports'

urlpatterns = [
    path('', views.report_list, name='report_list'),
]
