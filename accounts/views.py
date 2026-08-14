from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from .forms import RegistrationForm


def register(request):
    """Create a new student account and log them straight in."""
    if request.user.is_authenticated:
        return redirect("course_list")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome! Your account has been created.")
            return redirect("course_list")
    else:
        form = RegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    """Authenticate an existing user."""
    if request.user.is_authenticated:
        return redirect("course_list")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                messages.success(request, f"Signed in as {user}.")
                return redirect(request.GET.get("next") or "course_list")
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    """Log the current user out."""
    logout(request)
    messages.info(request, "You have been signed out.")
    return redirect("course_list")
