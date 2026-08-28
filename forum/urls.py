from django.urls import path
from .views import ForumHomeView, CategoryDetailView, ThreadDetailView
from .views import ForumPostCreateView
from .views import ForumThreadCreateView
from .views import ForumThreadCreateView, ForumThreadUpdateView
from .views import ForumPostDeleteView

from .views import (
    ForumThreadCreateView,
    ForumThreadUpdateView,
    ForumThreadDeleteView,
    ForumPostUpdateView,
    ForumPostDeleteView,

    

)





app_name = "forum"

urlpatterns = [
    path("", ForumHomeView.as_view(), name="forum_home"),
    path("category/<slug:slug>/", CategoryDetailView.as_view(), name="category_detail"),
    path("thread/<int:pk>/", ThreadDetailView.as_view(), name="thread_detail"),
    path("thread/<int:pk>/reply/", ForumPostCreateView.as_view(), name="post_create"),
    path("thread/create/", ForumThreadCreateView.as_view(), name="thread_create"),
    path("thread/<int:pk>/edit/", ForumThreadUpdateView.as_view(), name="thread_edit"),
    path("thread/<int:pk>/delete/", ForumThreadDeleteView.as_view(), name="thread_delete"),
    path("post/<int:pk>/edit/", ForumPostUpdateView.as_view(), name="post_edit"),
    path("post/<int:pk>/delete/", ForumPostDeleteView.as_view(), name="post_delete"),






]

