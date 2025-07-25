# =============================================================================
# apps/users/views.py - Users app views
# =============================================================================

from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import viewsets
from django.contrib.auth.models import User
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ProfileView(TemplateView):
    template_name = 'users/profile.html'