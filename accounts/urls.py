"""Accounts URL configuration"""
from django.urls import path
from django.contrib.auth import views as auth_views
from accounts import views as account_views

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', account_views.profile_view, name='profile'),
    path('change-password/', account_views.change_password_view, name='change_password'),
    path('forgot-password/', account_views.forgot_password_view, name='forgot_password'),
    path('reset-password/<uuid:token>/', account_views.reset_password_view, name='reset_password'),
    path('verify-email/<uuid:token>/', account_views.verify_email_view, name='verify_email'),
]
