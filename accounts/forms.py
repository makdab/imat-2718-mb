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
