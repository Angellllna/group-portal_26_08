from django.urls import path
from .views import ForumHomeView, CategoryDetailView, ThreadDetailView

app_name = 'forum'

urlpatterns = [
    path('', ForumHomeView.as_view(), name='home'),
    path('category/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('thread/<int:pk>/', ThreadDetailView.as_view(), name='thread_detail'),
]