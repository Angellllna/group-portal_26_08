"""
Головний маршрутизатор URL проєкту "Портал групи".

Як підключити свій модуль:
    1. Створити додаток:            python manage.py startapp forum
    2. Розкоментувати додаток у     config/settings.py -> INSTALLED_APPS
    3. Створити файл                forum/urls.py:

           from django.urls import path
           from . import views

           app_name = "forum"

           urlpatterns = [
               path("", views.ThreadListView.as_view(), name="thread-list"),
           ]

    4. Розкоментувати рядок свого модуля в urlpatterns нижче.

Документація: https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView


urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),

    path(
        "",
        TemplateView.as_view(
            template_name="home.html"
        ),
        name="home",
    ),

    path(
        "materials/",
        include("materials.urls"),
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )