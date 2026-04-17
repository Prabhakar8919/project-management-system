from django.db import models
from django.contrib.auth.models import User

# Accounts app uses Django's built-in User model.

class OTPVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_requests', db_index=True)
    otp_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    attempts = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"OTP for {self.user.email} at {self.created_at}"
