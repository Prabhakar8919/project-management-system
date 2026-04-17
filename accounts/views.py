from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.contrib.auth.models import User
import logging

from .forms import SignUpForm, LoginForm, ForgotPasswordForm, VerifyOTPForm, ResetPasswordForm
from .utils import send_welcome_email, send_otp_email, verify_otp_submission

logger = logging.getLogger(__name__)
signer = TimestampSigner()

TRANSPARENT_1X1_PNG = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'

def set_theme_light(request):
    request.session['theme'] = 'light'
    request.session.modified = True
    response = HttpResponse(TRANSPARENT_1X1_PNG, content_type="image/png")
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    return response

def set_theme_dark(request):
    request.session['theme'] = 'dark'
    request.session.modified = True
    response = HttpResponse(TRANSPARENT_1X1_PNG, content_type="image/png")
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    return response

def landing_page(request):
    return render(request, 'home.html')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.is_active = True # Bypass Email Verification
        user.save()
        send_welcome_email(user)
        messages.success(request, 'Account created successfully. Please login.')
        return redirect('login')
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data.get('username'),
            password=form.cleaned_data.get('password'),
        )
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have logged out successfully.')
    return redirect('login')

@login_required
def profile_redirect(request):
    return redirect('dashboard')

def verify_email_view(request, token):
    if request.user.is_authenticated:
        return redirect('dashboard')
    try:
        user_id = signer.unsign(token, max_age=86400) # 1 day validity
        user = get_object_or_404(User, pk=user_id)
        if not user.is_active:
            user.is_active = True
            user.save()
            messages.success(request, 'Email verified successfully! You can now login.')
        else:
            messages.info(request, 'Account is already verified.')
        return redirect('login')
    except (BadSignature, SignatureExpired):
        messages.error(request, 'Invalid or expired verification token.')
        return redirect('login')

def forgot_password_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = ForgotPasswordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        user = User.objects.filter(email=email).first()
        if user:
            success, msg = send_otp_email(user)
            if success:
                request.session['reset_email'] = email
                messages.success(request, msg)
                return redirect('verify_otp')
            else:
                messages.error(request, msg)
        else:
            # Prevent email enumeration attacks
            request.session['reset_email'] = email
            messages.success(request, 'If an account with this email exists, an OTP has been sent.')
            return redirect('verify_otp')
    return render(request, 'accounts/forgot_password.html', {'form': form})

def verify_otp_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, 'Session expired. Please request OTP again.')
        return redirect('forgot_password')
        
    form = VerifyOTPForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        otp = form.cleaned_data['otp']
        success, msg = verify_otp_submission(email, otp)
        if success:
            # Generates a signed token to safely allow resetting password bypassing session state limit
            reset_token = signer.sign(f"reset_{email}")
            request.session['reset_token'] = reset_token
            messages.success(request, msg)
            return redirect('reset_password')
        else:
            messages.error(request, msg)
            
    return render(request, 'accounts/verify_otp.html', {'form': form, 'email': email})

def reset_password_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    email = request.session.get('reset_email')
    reset_token = request.session.get('reset_token')
    
    if not email or not reset_token:
        messages.error(request, 'Unauthorized or session expired.')
        return redirect('forgot_password')
        
    try:
        # Validate reset token strictly
        signer.unsign(reset_token, max_age=600) # Valid for 10 min after OTP
    except (BadSignature, SignatureExpired):
        logger.warning(f"Invalid or expired reset token for {email}")
        messages.error(request, 'Reset session expired. Please start again.')
        return redirect('forgot_password')
        
    user = get_object_or_404(User, email=email)
    form = ResetPasswordForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        user.set_password(form.cleaned_data['password'])
        user.save()
        # Clear session
        del request.session['reset_email']
        del request.session['reset_token']
        logger.info(f"Password reset successfully for {email}")
        messages.success(request, 'Password reset successfully. Please login.')
        return redirect('login')
        
    return render(request, 'accounts/reset_password.html', {'form': form})
