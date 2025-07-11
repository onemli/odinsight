from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
app_name = 'workflows'
# DRF Router
router = DefaultRouter()
router.register(r'categories', views.ModuleCategoryViewSet)
router.register(r'modules', views.ModuleViewSet)
router.register(r'workflows', views.WorkflowViewSet)
router.register(r'executions', views.WorkflowExecutionViewSet)



urlpatterns = [
    # Template Views
    path('', views.workflow_builder, name='builder'),
    path('list/', views.workflow_list, name='workflow_list'),
    
    # API URLs
    # path('api/', include((router.urls, 'api'))),
]