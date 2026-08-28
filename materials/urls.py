from django.urls import path

from .views import (
    MaterialListView,
    MaterialDetailView,
    MaterialCreateView,
    MaterialUpdateView,
    MaterialDeleteView,
    MaterialCategoryListView,
    MaterialCategoryCreateView,
    MaterialCategoryUpdateView,
    MaterialCategoryDeleteView,
    MaterialCategoryToggleView,
    MaterialCategoryMoveUpView,
    MaterialCategoryMoveDownView,
)


app_name = "materials"


urlpatterns = [
    # Матеріали
    path(
        "",
        MaterialListView.as_view(),
        name="material_list",
    ),

    path(
        "add/",
        MaterialCreateView.as_view(),
        name="material_create",
    ),

    # Категорії
    path(
        "categories/",
        MaterialCategoryListView.as_view(),
        name="category_list",
    ),

    path(
        "categories/create/",
        MaterialCategoryCreateView.as_view(),
        name="category_create",
    ),

    path(
        "categories/<int:pk>/update/",
        MaterialCategoryUpdateView.as_view(),
        name="category_update",
    ),

    path(
        "categories/<int:pk>/delete/",
        MaterialCategoryDeleteView.as_view(),
        name="category_delete",
    ),

    path(
        "categories/<int:pk>/toggle/",
        MaterialCategoryToggleView.as_view(),
        name="category_toggle",
    ),

    path(
        "categories/<int:pk>/move-up/",
        MaterialCategoryMoveUpView.as_view(),
        name="category_move_up",
    ),

    path(
        "categories/<int:pk>/move-down/",
        MaterialCategoryMoveDownView.as_view(),
        name="category_move_down",
    ),

    # Важливо: ці маршрути повинні бути після categories/
    path(
        "<slug:slug>/edit/",
        MaterialUpdateView.as_view(),
        name="material_update",
    ),

    path(
        "<slug:slug>/delete/",
        MaterialDeleteView.as_view(),
        name="material_delete",
    ),

    path(
        "<slug:slug>/",
        MaterialDetailView.as_view(),
        name="material_detail",
    ),
]