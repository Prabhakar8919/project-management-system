from django.urls import path
from .views import signup_view, login_view, logout_view, profile_redirect, set_theme_light, set_theme_dark

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_redirect, name='profile'),
    path('set-theme/light/', set_theme_light, name='set_theme_light'),
    path('set-theme/dark/', set_theme_dark, name='set_theme_dark'),
]
