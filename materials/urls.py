from django.urls import path

from .views import (
    MaterialCreateView,
    MaterialDeleteView,
    MaterialDetailView,
    MaterialListView,
    MaterialUpdateView,
)

app_name = "materials"

urlpatterns = [
    path("", MaterialListView.as_view(), name="list"),
    # "add/" оголошений раніше за <str:slug>/, інакше його з'їв би конвертер slug-а
    path("add/", MaterialCreateView.as_view(), name="add"),
    # str, а не slug: вбудований конвертер <slug:> не приймає кирилицю,
    # а slug-и генеруються з українських назв (allow_unicode=True)
    path("<str:slug>/", MaterialDetailView.as_view(), name="detail"),
    path("<str:slug>/edit/", MaterialUpdateView.as_view(), name="edit"),
    path("<str:slug>/delete/", MaterialDeleteView.as_view(), name="delete"),
]
