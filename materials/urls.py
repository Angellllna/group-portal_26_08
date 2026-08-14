from django.urls import path

from .views import MaterialDetailView, MaterialListView

app_name = "materials"

urlpatterns = [
    path("", MaterialListView.as_view(), name="list"),
    # str, а не slug: вбудований конвертер <slug:> не приймає кирилицю,
    # а slug-и генеруються з українських назв (allow_unicode=True)
    path("<str:slug>/", MaterialDetailView.as_view(), name="detail"),
]
