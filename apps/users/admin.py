# =============================================================================
# apps/users/admin.py - Users app admin
# =============================================================================

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Extend the default User admin if needed
# For now, we'll use the default Django User admin