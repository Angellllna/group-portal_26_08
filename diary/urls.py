from django.urls import path

from .views import (
    GradeCreateView,
    StudentGradesView,
    StudentListView,
    SubjectDetailView,
    SubjectListView,
)

app_name = "diary"

urlpatterns = [
    path("", StudentListView.as_view(), name="student_list"),
    path("student/<int:pk>/", StudentGradesView.as_view(), name="student_grades"),
    path("grades/add/", GradeCreateView.as_view(), name="grade_add"),
    path("subjects/", SubjectListView.as_view(), name="subject-list"),
    path("subject/<int:pk>/", SubjectDetailView.as_view(), name="subject-detail"),
]
