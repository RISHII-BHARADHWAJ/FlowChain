"""
Custom User model with RBAC for FlowChain Platform
"""
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel


class UserRole(models.TextChoices):
    SUPER_ADMIN = 'super_admin', 'Super Admin'
    WAREHOUSE_MANAGER = 'warehouse_manager', 'Warehouse Manager'
    PROCUREMENT_MANAGER = 'procurement_manager', 'Procurement Manager'
    INVENTORY_MANAGER = 'inventory_manager', 'Inventory Manager'
    SALES_MANAGER = 'sales_manager', 'Sales Manager'
    FINANCE_MANAGER = 'finance_manager', 'Finance Manager'
    EMPLOYEE = 'employee', 'Employee'


class UserManager(BaseUserManager):
    """Custom user manager supporting email as username"""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Email address is required'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('role', UserRole.SUPER_ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """Extended User model with roles, profile, and verification"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    phone = models.CharField(max_length=20, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/%Y/%m/', null=True, blank=True)
    role = models.CharField(
        max_length=30,
        choices=UserRole.choices,
        default=UserRole.EMPLOYEE,
        db_index=True,
    )
    department = models.CharField(max_length=100, null=True, blank=True)
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)

    # Status flags
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_2fa_enabled = models.BooleanField(default=False)

    # Preferences
    user_timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')
    theme = models.CharField(max_length=20, default='dark', choices=[
        ('dark', 'Dark'), ('light', 'Light'), ('auto', 'Auto')
    ])
    notifications_enabled = models.BooleanField(default=True)

    # Timestamps
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_password_change = models.DateTimeField(null=True, blank=True)

    # Assigned warehouse (for warehouse managers)
    assigned_warehouse = models.ForeignKey(
        'warehouses.Warehouse',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_users',
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email', 'is_active']),
            models.Index(fields=['role', 'is_active']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    @property
    def is_super_admin(self):
        return self.role == UserRole.SUPER_ADMIN or self.is_superuser

    @property
    def is_warehouse_manager(self):
        return self.role == UserRole.WAREHOUSE_MANAGER

    @property
    def is_procurement_manager(self):
        return self.role == UserRole.PROCUREMENT_MANAGER

    @property
    def is_inventory_manager(self):
        return self.role == UserRole.INVENTORY_MANAGER

    @property
    def is_sales_manager(self):
        return self.role == UserRole.SALES_MANAGER

    @property
    def is_finance_manager(self):
        return self.role == UserRole.FINANCE_MANAGER

    def can_access_module(self, module):
        """Check if user can access a specific module based on role"""
        from accounts.permissions import ROLE_MODULE_ACCESS
        allowed_modules = ROLE_MODULE_ACCESS.get(self.role, [])
        if self.is_super_admin:
            return True
        return module in allowed_modules


class EmailVerificationToken(TimeStampedModel):
    """Email verification token for new users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verification_token')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    class Meta:
        verbose_name = 'Email Verification Token'


class PasswordResetToken(TimeStampedModel):
    """Password reset token"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_from_ip = models.GenericIPAddressField(null=True, blank=True)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    class Meta:
        verbose_name = 'Password Reset Token'


class UserActivity(TimeStampedModel):
    """Track user login/logout activity"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=50, choices=[
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('failed_login', 'Failed Login'),
        ('password_change', 'Password Change'),
        ('profile_update', 'Profile Update'),
    ])
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', 'action', 'created_at'])]
