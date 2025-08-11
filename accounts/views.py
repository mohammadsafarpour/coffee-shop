from .models import Profile
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.conf import settings
from .forms import CustomUserCreationForm, CustomUserChangeForm, ProfileUpdateForm
from kavenegar import KavenegarAPI, APIException, HTTPException
from products.models import Product

def send_welcome_sms(phone_number):
    api = KavenegarAPI(settings.KAVENEGAR_API_KEY)
    try:
        params = {
        'sender': '2000660110',
        'receptor' : phone_number,
        'message' : "سلام به کافه ما خوش آمدید"
        }
        response = api.sms_send(params)

    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)
    

    # print(f" شبیه‌سازی ارسال پیامک به شماره {phone_number} ")
    # print(" پیام: به کافه ما خوش آمدید ")


class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "accounts/signup.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object

        send_mail(
            subject="به کافه ما خوش آمدید",
            message=f"سلام، از ثبت‌نام شما در وب‌سایت تمیزکافه سپاسگزاریم.",
            from_email=getattr(settings, "EMAIL_HOST_USER", "noreply@example.com"),
            recipient_list=[user.email],
            fail_silently=False,
        )

        send_welcome_sms(user.phone)

        return response


class DashboardView(LoginRequiredMixin, generic.TemplateView):
    template_name = "accounts/dashboard.html"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["profile"] = self.request.user.profile
    #     return context
    


class ProfileEditView(LoginRequiredMixin, generic.UpdateView):

    def get(self, request, *args, **kwargs):
        user_form = CustomUserChangeForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        context = {"user_form": user_form, "profile_form": profile_form}
        return render(request, "accounts/profile_edit.html", context)

    def post(self, request, *args, **kwargs):
        user_form = CustomUserChangeForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "پروفایل شما با موفقیت به‌روزرسانی شد.")
            return redirect("dashboard")

        context = {"user_form": user_form, "profile_form": profile_form}
        return render(request, "accounts/profile_edit.html", context)

    def get_success_url(self):
        return reverse("dashboard")

class ProfileFavoritesView(LoginRequiredMixin, generic.TemplateView):
    template_name = "accounts/profile_favorites.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.request.user.profile
        return context

class ProfileRemoveFavoriteView(LoginRequiredMixin, generic.View):

    def post(self, request, user_id, product_id):
        profile = get_object_or_404(Profile, user_id=user_id)
        product = get_object_or_404(Product, id=product_id)
        profile.favorites.remove(product)
        return HttpResponseRedirect(reverse("profile-favorites", args=[user_id]))


# class SignUpView(generic.CreateView):

#     form_class = CustomUserCreationForm
#     success_url = reverse_lazy('login')
#     template_name = 'signup.html'

# def user_login(request):
#     if request.method == "POST":
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             user = authenticate(request, email=cd["email"], password=cd["password"])
#             if user is not None:
#                 if user.is_active:
#                     login(request, user)
#                     return HttpResponse("Authenticated successfully")
#                 else:
#                     return HttpResponse("Disabled account")
#             else:
#                 return render(request, "accounts/login.html", {"form": form, "error": "Invalid login"})
#     else:
#         form = LoginForm()
#         return render(request, "accounts/login.html", {"form": form})


# @login_required
# def dashboard(request):
#     return render(request, "accounts/dashboard.html", {"section": "dashboard"})

# def SignUpView(request):
#     if request.method == "POST":
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             # Send welcome email
#             send_mail(
#                 subject='خوش آمدید!',
#                 message='ثبت‌نام شما با موفقیت انجام شد.',
#                 from_email='your@example.com',
#                 recipient_list=[user.email],
#                 fail_silently=False,
#             )
#             # Send welcome SMS
#             if user.phone:
#                 send_sms(user.phone, 'ثبت‌نام شما با موفقیت انجام شد.')
#             return HttpResponse("Registration successful. You can now log in.")
#         else:
#             return render(request, "accounts/signup.html", {"form": form})
#     else:
#         form = SignUpForm()
#         return render(request, "accounts/signup.html", {"form": form})
