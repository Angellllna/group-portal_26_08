from django.urls import path

from .views import (
    PollListView,
    PollDetailView,
    PollPageView,
)
app_name = "polls"

urlpatterns = [
    path(
        "",
        PollListView.as_view(),
        name="poll_list"),
    path(
        "<slug:slug>/",
        PollDetailView.as_view(),
        name="poll_detail"),
    path(
        "<slug:slug>/page/<int:page_number>/",
        PollPageView.as_view(),
        name="poll_page"),
]