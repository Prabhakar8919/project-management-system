from django.urls import path
from .views import (
    explorer_view,
    project_detail,
    studio_view,
    project_create,
    project_edit,
    project_delete,
)

urlpatterns = [
    path('', explorer_view, name='explorer'),
    path('studio/', studio_view, name='studio'),
    path('create/', project_create, name='project_create'),
    path('edit/<int:pk>/', project_edit, name='project_edit'),
    path('delete/<int:pk>/', project_delete, name='project_delete'),
    path('detail/<int:pk>/', project_detail, name='project_detail'),
]
