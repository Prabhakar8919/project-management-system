import re
from django.core.exceptions import ValidationError

def validate_password_strength(password):
    """Ensure password follows strong security policies."""
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter.')
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter.')
    if not re.search(r'\d', password):
        raise ValidationError('Password must contain at least one number.')
    if not re.search(r'[^A-Za-z0-9]', password):
        raise ValidationError('Password must contain at least one special character.')
