from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView

from .forms import ProfileUpdateForm, RegisterForm
from .models import User


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Реєстрацію успішно завершено. Тепер ви можете увійти.",
        )
        return response


class AccountLoginView(LoginView):
    template_name = "accounts/login.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Ви успішно увійшли в акаунт.")
        return response


class AccountLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, "Ви вийшли з акаунта.")
        return super().dispatch(request, *args, **kwargs)


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "accounts/profile_detail.html"

    def get_object(self, queryset=None):
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = "accounts/profile_form.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Профіль успішно оновлено.")
        return response


class PublicProfileDetailView(DetailView):
    model = User
    template_name = "accounts/public_profile_detail.html"

    def get_queryset(self):
        # деактивований акаунт не показуємо навіть за прямим посиланням
        return User.objects.filter(is_active=True)
