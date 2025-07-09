# =============================================================================
# config/settings/development.py - Development settings
# =============================================================================

from .base import *

DEBUG = True

# Add debug toolbar for development
INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = [
    '127.0.0.1',
]

# Development database - can override if needed
# DATABASES['default']['NAME'] = 'odinsight_dev'