from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .validators import validate_password_strength


class SignUpForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter password',
                'pattern': '(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[^A-Za-z0-9]).{8,}',
                'title': 'Password must contain lowercase, uppercase, number, special character and be at least 8 characters',
                'required': 'required',
                'class': 'css-password-field',
            }
        ),
        label='Password',
    )
    confirm_password = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Confirm password',
                'required': 'required',
                'class': 'css-password-field',
            }
        ),
        label='Confirm Password',
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Choose username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter email'}),
        }
# getting password and confirm password from form
# checking if both are same
# if not, showing error message
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
            validate_password_strength(password)
        return password


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'autocomplete': 'off'}))
    password = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Password', 'autocomplete': 'new-password', 'class': 'css-password-field'}))

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your registered email', 'required': 'required'})
    )

class VerifyOTPForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={'placeholder': 'Enter 6-digit OTP', 'required': 'required', 'pattern': r'\d{6}'})
    )

class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': 'Enter new password', 'required': 'required', 'class': 'css-password-field'}
        ),
        label='New Password'
    )
    confirm_password = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': 'Confirm new password', 'required': 'required', 'class': 'css-password-field'}
        ),
        label='Confirm Password'
    )

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
            validate_password_strength(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data
