from django.shortcuts import render
from django.views.generic import ListView,DetailView
from .models import Subject, Grade
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.
class DiaryHomeView(ListView):
    model = User
    template_name = "diary/student_list.html"
    context_object_name = "students"
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context["User"] = User.objects.all()
        return context
class SubjectDetailView(DetailView):
    model = Subject
    template_name = "diary/home3.html"
    context_object_name = "subject"
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        return context