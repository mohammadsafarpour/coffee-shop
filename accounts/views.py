from django.urls import reverse_lazy, reverse
from django.views import generic
# from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.conf import settings

from .forms import CustomUserCreationForm
# from products.models import Product


# تابع شبیه‌سازی شده برای ارسال پیامک
def send_welcome_sms(phone_number):

    print(f" شبیه‌سازی ارسال پیامک به شماره {phone_number} ")
    print(" پیام: به کافه ما خوش آمدید ")


class SignUpView(generic.CreateView):

    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'

    def form_valid(self, form):

        response = super().form_valid(form)
        user = self.object

        send_mail(
            subject='به کافه ما خوش آمدید',
            message=f'سلام، از ثبت‌نام شما در وب‌سایت ما سپاسگزاریم.',
            from_email=getattr(settings, 'EMAIL_HOST_USER', 'noreply@example.com'),
            recipient_list=[user.email],
            fail_silently=False,
        )

        send_welcome_sms(user.phone)

        return response


class DashboardView(LoginRequiredMixin, generic.TemplateView):

    template_name = 'accounts/dashboard.html'


# class AddToFavoritesView(LoginRequiredMixin, generic.View):

#     def get(self, request, *args, **kwargs):
#         product = get_object_or_404(Product, pk=self.kwargs['product_id'])
    
#         request.user.profile.favorites.add(product)
#         کاربر را به صفحه‌ای که از آن آمده بازمی‌گردانیم
#         return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('dashboard')))


# class RemoveFromFavoritesView(LoginRequiredMixin, generic.View):
   

#     def get(self, request, *args, **kwargs):
#         product = get_object_or_404(Product, pk=self.kwargs['product_id'])
#         request.user.profile.favorites.remove(product)
#         return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('dashboard')))


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
