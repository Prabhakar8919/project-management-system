from django.urls import path
from .views import (
    signup_view, login_view, logout_view, profile_redirect, 
    set_theme_light, set_theme_dark, verify_email_view,
    forgot_password_view, verify_otp_view, reset_password_view
)

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_redirect, name='profile'),
    path('verify-email/<str:token>/', verify_email_view, name='verify_email'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('verify-otp/', verify_otp_view, name='verify_otp'),
    path('reset-password/', reset_password_view, name='reset_password'),
    path('set-theme/light/', set_theme_light, name='set_theme_light'),
    path('set-theme/dark/', set_theme_dark, name='set_theme_dark'),
]
