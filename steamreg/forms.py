from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django import forms
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    """Custom UserCreationForm(new email field)"""
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Придумайте логин'
        self.fields['email'].widget.attrs['placeholder'] = 'Введите почту'
        self.fields['password1'].widget.attrs['placeholder'] = 'Придумайте пароль'
        self.fields['password2'].widget.attrs['placeholder'] = 'Повторите пароль'

class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput)
    def __init__(self, *args, **kwargs):
        super(UserPasswordResetForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = 'Введите почту'

class UserSetPassowrdForm(SetPasswordForm):
    new_password1 = forms.CharField(widget=forms.PasswordInput)
    new_password2 = forms.CharField(widget=forms.PasswordInput)
    def __init__(self, *args, **kwargs):
        super(UserSetPassowrdForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs['placeholder'] = 'Введите новый пароль'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Повторите новый пароль'

