from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EmailVerificationForm, RegistrationForm
from .models import EmailVerification, User

# Session key holding the id of a user who has signed up but not yet verified.
PENDING_USER_SESSION_KEY = "pending_verification_user_id"


def _send_verification_code(user, verification):
    """Email the six-digit code to the user (console backend in development)."""
    send_mail(
        subject="Your University of Tech Portal verification code",
        message=(
            f"Hi {user.get_short_name() or user.username},\n\n"
            f"Your verification code is {verification.code}.\n"
            f"It expires in {settings.EMAIL_OTP_TTL_MINUTES} minutes.\n\n"
            "If you did not create an account, you can ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def register(request):
    """Create a new student account (inactive) and email a verification code."""
    if request.user.is_authenticated:
        return redirect("course_list")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Hold the account until the email address is verified.
            user.is_active = False
            user.save()

            verification = EmailVerification.issue(user)
            _send_verification_code(user, verification)

            request.session[PENDING_USER_SESSION_KEY] = user.id
            messages.info(
                request,
                f"We've emailed a verification code to {user.email}. "
                "Enter it below to finish creating your account.",
            )
            return redirect("verify_email")
    else:
        form = RegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


def verify_email(request):
    """Confirm the emailed code, then activate the account and sign the user in."""
    user_id = request.session.get(PENDING_USER_SESSION_KEY)
    if not user_id:
        messages.error(request, "Please sign up to verify your email.")
        return redirect("register")

    user = get_object_or_404(User, pk=user_id, is_active=False)

    if request.method == "POST":
        form = EmailVerificationForm(request.POST)
        if form.is_valid():
            verification = EmailVerification.objects.filter(user=user).first()
            if verification is None or verification.is_expired:
                messages.error(
                    request, "That code has expired. We can send you a new one."
                )
            elif verification.attempts_exhausted:
                messages.error(
                    request, "Too many incorrect attempts. Request a new code."
                )
            elif verification.check_code(form.cleaned_data["code"]):
                user.is_active = True
                user.save(update_fields=["is_active"])
                verification.delete()
                del request.session[PENDING_USER_SESSION_KEY]
                login(request, user)
                messages.success(request, "Your email is verified. Welcome!")
                return redirect("course_list")
            else:
                messages.error(request, "That code is not correct. Please try again.")
    else:
        form = EmailVerificationForm()

    return render(
        request, "accounts/verify_email.html", {"form": form, "email": user.email}
    )


def resend_code(request):
    """Issue and email a fresh verification code for the pending sign-up."""
    user_id = request.session.get(PENDING_USER_SESSION_KEY)
    if not user_id:
        return redirect("register")

    user = get_object_or_404(User, pk=user_id, is_active=False)
    if request.method == "POST":
        verification = EmailVerification.issue(user)
        _send_verification_code(user, verification)
        messages.info(request, f"A new code is on its way to {user.email}.")

    return redirect("verify_email")


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
