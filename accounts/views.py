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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = Product.objects.all()
        return context


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

class ProfileNotificationsView(LoginRequiredMixin, generic.TemplateView):
    template_name = "accounts/profile_notifications.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        notifications = self.request.user.notifications.all()
        context["unread_notifications_count"] = notifications.filter(is_read=False).count()
        context["notifications"] = notifications.order_by("-created_at")
        return context


