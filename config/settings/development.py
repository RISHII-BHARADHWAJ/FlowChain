"""Development settings"""
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# Use SQLite in development for easy local setup (no PostgreSQL required)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email - console backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Allow all CORS in development
CORS_ALLOW_ALL_ORIGINS = True
