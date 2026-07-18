"""API user viewset"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active', 'department']
    search_fields = ['first_name', 'last_name', 'email', 'employee_id']
    ordering_fields = ['date_joined', 'first_name', 'role']
    ordering = ['-date_joined']

    def get_queryset(self):
        return User.objects.filter(is_active=True)

    def get_serializer_class(self):
        from accounts.serializers import UserSerializer
        return UserSerializer

    def get_permissions(self):
        from accounts.permissions import IsSuperAdmin
        if self.action in ['list', 'create', 'destroy']:
            return [IsAuthenticated(), IsSuperAdmin()]
        return [IsAuthenticated()]
