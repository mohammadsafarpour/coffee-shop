# from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('phone', 'email')

class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ('phone', 'email')


# class SignUpForm(UserCreationForm):
#     class Meta:
#         model = CustomUser
#         fields = ['email', 'phone', 'password1', 'password2']



# class LoginForm(forms.Form): 
#     email = forms.EmailField()
#     password = forms.CharField(widget=forms.PasswordInput)