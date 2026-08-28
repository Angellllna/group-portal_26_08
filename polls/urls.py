from django.urls import path

from .views import (
    PollDetailView,
    PollListView,
    PollPageView,
    PollStartView,
)

app_name = "polls"

urlpatterns = [
    path("", PollListView.as_view(), name="poll_list"),
    # str, а не slug: вбудований конвертер <slug:> не приймає кирилицю,
    # а slug-и генеруються з українських назв (allow_unicode=True)
    path("<str:slug>/", PollDetailView.as_view(), name="poll_detail"),
    path("<str:slug>/start/", PollStartView.as_view(), name="poll_start"),
    path(
        "<str:slug>/page/<int:page_number>/",
        PollPageView.as_view(),
        name="poll_page",
    ),
]
