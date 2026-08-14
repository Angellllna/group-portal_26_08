from django.shortcuts import render
from django.views.generic import ListView
from .models import Subject, Grade

# Create your views here.
class DiaryHomeView(ListView):
    model = Subject
    template_name = "diary/home.html"
    context_object_name = "subjects"
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        return context