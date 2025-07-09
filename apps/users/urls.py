# =============================================================================
# apps/users/urls.py - Users app URLs
# =============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)

app_name = 'users'

urlpatterns = [
    path('api/', include(router.urls)),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
]