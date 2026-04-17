import logging
import random
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password

logger = logging.getLogger(__name__)

def generate_otp():
    """Generates a secure random 6-digit OTP."""
    return str(random.randint(100000, 999999))

def send_welcome_email(user):
    """
    Sends a beautifully formatted welcome email to the user upon signup.
    Includes both plain text and HTML versions.
    """
    subject = "Welcome to Project Master! 🎉"
    
    # Plain text version as fallback
    text_content = f"""
    Hello {user.username},
    
    Welcome to Project Master! We are absolutely thrilled to have you on board.
    Project Master is your professional, unified workspace designed to help you manage, track, and propel your ideas forward with ease.
    
    Go to Dashboard: http://127.0.0.1:8000/dashboard/
    
    If you have any questions, simply reply to this email to reach our support team.
    
    © 2026 Project Master. Need help? support@projectmaster.com
    """
    
    # Clean, plain-text style HTML layout with standard button
    html_content = f"""
    <div style="font-family: Arial, sans-serif; color: #1e293b; max-width: 600px;">
        <h2>Welcome, {user.username}! 🎉</h2>
        
        <p style="line-height: 1.6; font-size: 16px;">
            We are absolutely thrilled to have you on board. <strong>Project Master</strong> is your professional, unified workspace designed to help you manage, track, and propel your ideas forward with ease.
        </p>
        
        <p style="margin: 30px 0;">
            <a href="http://127.0.0.1:8000/dashboard/" style="background-color: #4ade80; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 16px;">Go to Dashboard</a>
        </p>
        
        <p style="font-size: 14px; margin-bottom: 0;">
            If you have any questions, simply reply to this email to reach our support team. We're here to help!
        </p>
        
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
        
        <div style="color: #64748b; font-size: 12px;">
            &copy; 2026 Project Master.<br>
            Need help? <a href="mailto:support@projectmaster.com" style="color: #64748b;">support@projectmaster.com</a>
        </div>
    </div>
    """
    
    msg = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )
    msg.attach_alternative(html_content, "text/html")
    
    try:
        msg.send(fail_silently=True) # Fail silently so user can still login if SMTP is off
        logger.info(f"Welcome email successfully sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")

def send_otp_email(user):
    """
    Generates an OTP and sends an inline HTML email for password reset.
    Rate limited to 3 per 10min.
    """
    email = user.email
    req_key = f"otp_req_count_{email}"
    count = cache.get(req_key, 0)
    
    if count >= 3:
        logger.warning(f"Rate limit exceeded for OTP generation: {email}")
        return False, "You have requested too many OTPs. Please wait 10 minutes."
    
    otp = generate_otp()
    otp_hash = make_password(otp)
    
    # Cache OTP Hash & Reset Attempts for 5 minutes
    cache.set(f"otp_hash_{email}", otp_hash, timeout=300)
    cache.set(f"otp_attempts_{email}", 0, timeout=300)
    
    # Extend Request TTL (10 mins = 600s)
    cache.set(req_key, count + 1, timeout=600)
    
    subject = "Project Master - Password Reset OTP 🔒"
    
    # Plain text version as fallback
    text_content = f"""
    Hello,
    
    We received a request to reset your Project Master password.
    
    Your OTP is: {otp}
    
    This code is valid for exactly 5 minutes. Please do not share this code with anyone.
    If you did not request this reset, you can safely ignore this email.
    
    © 2026 Project Master. Support: support@projectmaster.com
    """
    
    # Clean, plain-text style HTML layout with raw OTP
    html_content = f"""
    <div style="font-family: Arial, sans-serif; color: #1e293b; max-width: 600px;">
        <h2>Password Reset Request</h2>
        
        <p style="line-height: 1.6; font-size: 16px;">
            We received a request to reset your password for your Project Master account.
        </p>
        
        <div style="margin: 25px 0;">
            <strong style="display: block; font-size: 14px; margin-bottom: 5px;">Your Authorization Code</strong>
            <span style="display: block; font-size: 32px; font-weight: bold; letter-spacing: 5px;">{otp}</span>
        </div>
        
        <p style="color: #ef4444; font-size: 14px; margin-top: 20px; font-weight: bold;">
            ⚠️ This code is valid for exactly 5 minutes. Do not share this code with anyone.
        </p>
        
        <p style="font-size: 14px; margin-bottom: 0; line-height: 1.5;">
            If you did not request a password reset, you can safely ignore this email. Your account remains secure.
        </p>
        
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
        
        <div style="color: #64748b; font-size: 12px;">
            &copy; 2026 Project Master.<br>
            Need help? <a href="mailto:support@projectmaster.com" style="color: #64748b;">support@projectmaster.com</a>
        </div>
    </div>
    """
    
    msg = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [email]
    )
    msg.attach_alternative(html_content, "text/html")
    
    logger.info(f"OTP generated and attempted to send to {email}")
    try:
        msg.send(fail_silently=False)
        return True, "OTP sent successfully."
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False, "Failed to send email. Please add your real Gmail and App Password in settings.py."

def verify_otp_submission(email, otp_input):
    """
    Verifies an OTP input natively using hash matching & controls attempt counts.
    """
    attempts_key = f"otp_attempts_{email}"
    attempts = cache.get(attempts_key, 0)
    
    if attempts >= 5:
        logger.warning(f"OTP max attempts reached for {email}")
        return False, "Maximum verification attempts exceeded. Please request a new OTP."
        
    otp_hash = cache.get(f"otp_hash_{email}")
    if not otp_hash:
        logger.info(f"Expired/Nonexistent OTP requested for {email}")
        return False, "OTP has expired or was not requested."
        
    if check_password(otp_input, otp_hash):
        cache.delete(f"otp_hash_{email}")
        cache.delete(attempts_key)
        logger.info(f"OTP successfully verified for {email}")
        return True, "OTP verified successfully."
    else:
        cache.set(attempts_key, attempts + 1, timeout=300)
        logger.info(f"Invalid OTP attempt {attempts+1} for {email}")
        return False, "Invalid OTP."
