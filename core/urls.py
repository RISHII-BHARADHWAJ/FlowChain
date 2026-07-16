"""Core URL patterns"""
from django.urls import path
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    path('', views.dashboard, name='home'),
]
