from django.urls import path
from .views import dashboard_view, admin_panel

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('admin/', admin_panel, name='admin_panel'),
]
