from django.contrib.auth.forms import UserCreationForm
from django import forms

from .models import User


class RegistrationForm(UserCreationForm):
    """Sign-up form.

    Builds on Django's ``UserCreationForm`` so password strength validation
    and confirmation are handled by the framework. Email is required so we can
    contact registered students.
    """

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class EmailVerificationForm(forms.Form):
    """Collects the six-digit code we email during sign-up."""

    code = forms.CharField(
        label="Verification code",
        min_length=6,
        max_length=6,
        widget=forms.TextInput(
            attrs={
                "inputmode": "numeric",
                "autocomplete": "one-time-code",
                "pattern": "[0-9]*",
                "placeholder": "123456",
            }
        ),
    )

    def clean_code(self):
        code = self.cleaned_data["code"].strip()
        if not code.isdigit():
            raise forms.ValidationError("The code is six digits.")
        return code
