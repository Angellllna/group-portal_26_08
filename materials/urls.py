from django.urls import path

from .views import (
    MaterialListView,
    MaterialDetailView,
    MaterialCreateView,
    MaterialUpdateView,
    MaterialDeleteView,
)

app_name = "materials"

urlpatterns = [
    path(
        "",
        MaterialListView.as_view(),
        name="material_list",
    ),

    path(
        "add/",
        MaterialCreateView.as_view(),
        name="material_add",
    ),

    path(
        "<slug:slug>/",
        MaterialDetailView.as_view(),
        name="material_detail",
    ),

    path(
        "<slug:slug>/edit/",
        MaterialUpdateView.as_view(),
        name="material_edit",
    ),

    path(
        "<slug:slug>/delete/",
        MaterialDeleteView.as_view(),
        name="material_delete",
    ),
]