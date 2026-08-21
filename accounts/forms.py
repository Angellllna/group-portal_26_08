from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms

from .models import User


class RegisterForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = get_user_model().Role.USER
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        # role, is_staff і is_superuser сюди не входять навмисно:
        # підвищити собі права через цю форму неможливо
        fields = ("username", "first_name", "last_name", "email")
        labels = {
            "username": "Username",
            "first_name": "Ім'я",
            "last_name": "Прізвище",
            "email": "Email",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
