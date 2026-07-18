from django.urls import path
from forecasting import template_views as views

app_name = 'forecasting'

urlpatterns = [
    path('', views.forecast_dashboard, name='forecast_dashboard'),
]
