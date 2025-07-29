from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from .forms import LoginForm, SignUpForm
from django.contrib.auth.decorators import login_required


from django.core.mail import send_mail
import requests

def user_signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Send welcome email
            send_mail(
                subject='خوش آمدید!',
                message='ثبت‌نام شما با موفقیت انجام شد.',
                from_email='your@example.com',
                recipient_list=[user.email],
                fail_silently=False,
            )
            # Send welcome SMS
            if user.phone:
                send_sms(user.phone, 'ثبت‌نام شما با موفقیت انجام شد.')
            return HttpResponse("Registration successful. You can now log in.")
        else:
            return render(request, "accounts/signup.html", {"form": form})
    else:
        form = SignUpForm()
        return render(request, "accounts/signup.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, email=cd["email"], password=cd["password"])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse("Authenticated successfully")
                else:
                    return HttpResponse("Disabled account")
            else:
                return render(request, "accounts/login.html", {"form": form, "error": "Invalid login"})
    else:
        form = LoginForm()
        return render(request, "accounts/login.html", {"form": form})


@login_required
def dashboard(request):
    return render(request, "accounts/dashboard.html", {"section": "dashboard"})

