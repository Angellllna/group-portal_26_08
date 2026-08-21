from django.urls import path

from .views import (
    AccountLoginView,
    AccountLogoutView,
    ProfileDetailView,
    ProfileUpdateView,
    PublicProfileDetailView,
    RegisterView,
)

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", AccountLoginView.as_view(), name="login"),
    path("logout/", AccountLogoutView.as_view(), name="logout"),
    path("profile/", ProfileDetailView.as_view(), name="profile"),
    path("profile/edit/", ProfileUpdateView.as_view(), name="profile-edit"),
    path("users/<int:pk>/", PublicProfileDetailView.as_view(), name="public-profile"),
]
