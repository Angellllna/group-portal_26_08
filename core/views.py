from django.shortcuts import render
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
]

def home_page(request):
    return render(request, 'core/index.html')

# Create your views here.
