from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# from django.contrib.auth import get_user_model
from .models import CustomUser, Profile
from django.conf import settings

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ['email', 'phone']
        help_texts = {
            'email': 'لطفا یک آدرس ایمیل معتبر وارد کنید.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'] = forms.CharField(label='نام', max_length=100)
        self.fields['last_name'] = forms.CharField(label='نام خانوادگی', max_length=100)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.save()
        profile = user.profile
        profile.first_name = self.cleaned_data['first_name']
        profile.last_name = self.cleaned_data['last_name']
        if commit:
            profile.save()
        return user
    

class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ['email', 'phone']
        help_texts = {
            'email': 'لطفا یک آدرس ایمیل معتبر وارد کنید.',
        }
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'آدرس ایمیل'}),
            'phone': forms.TextInput(attrs={'placeholder': 'شماره تلفن'}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        self.fields['avatar'].required = False

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
        return profile
    
class ProfileImageForm(forms.ModelForm):
    """
    Form for updating profile image.
    """

    class Meta:
        model = Profile
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={'accept': 'image/*'})
        }

    def clean_avatar(self):
        """
        Validate the uploaded image.

        :return: The validated image.
        :rtype: File
        """
        avatar = self.cleaned_data.get('avatar')
        if not avatar:
            raise forms.ValidationError('لطفا یک تصویر انتخاب کنید.')
        if avatar.size > settings.MAX_AVATAR_SIZE:
            raise forms.ValidationError('حجم تصویر بیش از حد مجاز است.')
        if not getattr(avatar, 'content_type', '').startswith('image/'):
            raise forms.ValidationError('فقط فایل تصویری مجاز است.')
        return avatar

    def save(self, commit=True):
        """
        Save the form data to the model instance.

        :param commit: Whether to save the model instance to the database.
        :type commit: bool
        :return: The saved model instance.
        :rtype: Profile
        """
        profile = super().save(commit=False)
        if commit:
            profile.avatar.save(
                name=self.cleaned_data['avatar'].name,
                content=self.cleaned_data['avatar'].file,
                save=False,
            )
            profile.save()
        return profile
    
# class EmailAuthenticationForm(AuthenticationForm):

#     username = forms.EmailField(label="Email Address", max_length=255)

#     def __init__(self, *args, **kwargs):
#         super(EmailAuthenticationForm, self).__init__(*args, **kwargs)
#         self.fields['username'].widget.attrs['autofocus'] = True
#         self.fields['username'].widget.attrs['placeholder'] = 'Email Address'
#         self.fields['password'].widget.attrs['placeholder'] = 'Password'

#     def clean(self):
#         username = self.cleaned_data.get("username")
#         password = self.cleaned_data.get("password")
#         if username is not None and password:
#             self.user_cache = CustomUser.objects.filter(email=username).first()
#             if self.user_cache is None:
#                 raise self.get_invalid_login_error()
#             self.confirm_login_allowed(self.user_cache)
#         return self.cleaned_data
    

# class ProfileCoverForm(forms.ModelForm):
#     class Meta:
#         model = Profile
#         fields = ['cover_photo']
#         widgets = {
#             'cover_photo': forms.FileInput(attrs={'accept': 'image/*'})
#         }

#     def save(self, commit=True):
#         profile = super().save(commit=False)
#         if commit:
#             profile.save()
#         return profile


# class SignUpForm(UserCreationForm):
#     class Meta:
#         model = CustomUser
#         fields = ['email', 'phone', 'password1', 'password2']



# class LoginForm(forms.Form): 
#     email = forms.EmailField()
#     password = forms.CharField(widget=forms.PasswordInput)


