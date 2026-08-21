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

urlpatterns = [
    path("admin/", admin.site.urls),
    # --- Модулі порталу ---
    path("", include("core.urls"))                        # HOME — головна сторінка
    path(% url "home" %)
    # path("accounts/", include("accounts.urls")),               # AUTH — автентифікація, профілі
    # path("forum/", include("forum.urls")),                     # FOR  — форум
    # path("diary/", include("diary.urls")),                     # DIA  — електронний щоденник
    # path("events/", include("events.urls")),                   # EVE  — події та календар
    # path("polls/", include("polls.urls")),                     # POL  — опитування
    # path("voting/", include("voting.urls")),                   # VOT  — голосування
    # path("announcements/", include("announcements.urls")),     # ANN  — оголошення
    # path("materials/", include("materials.urls")),             # MAT  — матеріали
    # path("portfolio/", include("portfolio.urls")),             # POR  — портфоліо
    # path("gallery/", include("gallery.urls")),                 # GAL  — галерея
]

# Роздача завантажених користувачами файлів під час розробки (DEBUG = True).
# На продакшені медіа роздає вебсервер (nginx тощо), а не Django.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
