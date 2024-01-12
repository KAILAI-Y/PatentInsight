from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms


class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label="Username",
        max_length=150,
        widget=forms.TextInput(attrs={"id": "register_username"}),
    )
    password1 = forms.CharField(
        label="Password", widget=forms.PasswordInput(attrs={"id": "register_password1"})
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={"id": "register_password2"}),
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        max_length=150,
        widget=forms.TextInput(attrs={"id": "login_username"}),
    )
    password = forms.CharField(
        label="Password", widget=forms.PasswordInput(attrs={"id": "login_password"})
    )

    class Meta:
        model = User
        fields = ("username", "password")
