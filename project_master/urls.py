from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from dashboard.views import admin_login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-login/', admin_login_view, name='admin_login'),
    path('', include('accounts.urls')),
    path('projects/', include('projects.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]
