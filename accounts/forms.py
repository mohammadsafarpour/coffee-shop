from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# from django.contrib.auth import get_user_model
from .models import CustomUser, Profile

class CustomUserCreationForm(UserCreationForm):
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ['first_name', 'last_name','email', 'phone', 'password1', 'password2']

class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ['email', 'phone']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'avatar', 'favorites']


# class SignUpForm(UserCreationForm):
#     class Meta:
#         model = CustomUser
#         fields = ['email', 'phone', 'password1', 'password2']



# class LoginForm(forms.Form): 
#     email = forms.EmailField()
#     password = forms.CharField(widget=forms.PasswordInput)


class EmailAuthenticationForm(AuthenticationForm):

    username = forms.EmailField(label="Email Address", max_length=255)
