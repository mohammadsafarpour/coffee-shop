from django import forms
from django.contrib.auth.forms import AuthenticationForm

class EmailAuthenticationForm(AuthenticationForm):

    username = forms.EmailField(label="Email Address", max_length=255)