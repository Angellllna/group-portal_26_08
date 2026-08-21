from django.urls import path

from .views import (
    GradeCreateView,
    GradeUpdateView,
    GradeDeleteView,
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
    path("grades/<int:pk>/update", GradeUpdateView.as_view(), name="grade_update"),
    path("grades/<int:pk>/delete", GradeDeleteView.as_view(), name="grade_delete"),
    path("subjects/", SubjectListView.as_view(), name="subject-list"),
    path("subject/<int:pk>/", SubjectDetailView.as_view(), name="subject-detail"),
]
