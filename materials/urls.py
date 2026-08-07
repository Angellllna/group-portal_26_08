from django.urls import path
from .views import MaterialListView, MaterialDetailView

app_name = "materials"

urlpatterns = [
    path("", MaterialListView.as_view(), name="list"),
    path("<int:pk>/", MaterialDetailView.as_view(), name="detail"),
]