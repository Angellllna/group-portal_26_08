from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path  # noqa: F401  (include знадобиться для модулів нижче)
from django.views.generic import TemplateView
from .views import DiaryHomeView
app_name = "diary"
urlpatterns = [
    path("",DiaryHomeView.as_view(),name="home"),
]

