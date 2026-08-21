from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView,UpdateView,DeleteView

from accounts.mixins import AdminRequiredMixin

from .forms import GradeForm
from .models import Grade, Subject

User = get_user_model()


def students_queryset():
    """Учні — це активні користувачі з роллю user.

    Роль береться з поля role модуля AUTH, а не з is_staff:
    модератор теж не is_staff, але учнем не є.
    """
    return User.objects.filter(role=User.Role.USER, is_active=True)


class StudentListView(LoginRequiredMixin, ListView):
    template_name = "diary/student_list.html"
    context_object_name = "students"

    def get_queryset(self):
        return (
            students_queryset()
            .annotate(
                grades_count=Count("grades"),
                grades_average=Avg("grades__value"),
            )
            .order_by("last_name", "first_name", "username")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_add_grade"] = (
            self.request.user.is_authenticated and self.request.user.is_admin_role()
        )
        return context


class StudentGradesView(LoginRequiredMixin, DetailView):
    template_name = "diary/student_grades.html"
    context_object_name = "student"

    def get_queryset(self):
        # модератор або адміністратор, переданий у URL напряму, сюди не потрапить
        return students_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object

        grades = (
            Grade.objects
            .filter(student=student)
            .select_related("subject")
            .order_by("subject__title", "created_at")
        )

        # середні бали рахує ORM, окремого поля в базі немає
        averages = {
            row["subject"]: row["average"]
            for row in (
                Grade.objects
                .filter(student=student)
                .values("subject")
                .annotate(average=Avg("value"))
            )
        }

        by_subject = []
        for grade in grades:
            if not by_subject or by_subject[-1]["subject"] != grade.subject:
                by_subject.append({
                    "subject": grade.subject,
                    "grades": [],
                    "average": averages.get(grade.subject_id),
                })
            by_subject[-1]["grades"].append(grade)

        context["subjects_with_grades"] = by_subject
        context["grades_count"] = grades.count()
        context["total_average"] = (
            Grade.objects.filter(student=student).aggregate(average=Avg("value"))["average"]
        )
        # предмети, з яких оцінок ще немає — щоб не показувати порожні таблиці
        context["subjects_without_grades"] = (
            Subject.objects
            .filter(is_active=True)
            .exclude(pk__in=[item["subject"].pk for item in by_subject])
            .order_by("title")
        )
        context["can_add_grade"] = (
            self.request.user.is_authenticated and self.request.user.is_admin_role()
        )

        return context


class GradeCreateView(AdminRequiredMixin, CreateView):
    """Виставляти оцінки може лише адміністратор."""

    model = Grade
    form_class = GradeForm
    template_name = "diary/grade_form.html"
    success_url = reverse_lazy("diary:student_list")

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Виставляти оцінки може лише адміністратор.")

        return super().handle_no_permission()

    def get_initial(self):
        initial = super().get_initial()

        # /diary/grades/add/?student=<pk> — кнопка зі сторінки учня
        student_pk = self.request.GET.get("student")
        if student_pk and student_pk.isdigit():
            initial["student"] = student_pk

        return initial

    def form_valid(self, form):
        # автор оцінки береться з запиту, а не з форми
        form.instance.created_by = self.request.user

        response = super().form_valid(form)

        messages.success(self.request, "Оцінку виставлено.")

        return response

    def get_success_url(self):
        return reverse("diary:student_grades", args=[self.object.student_id])
class GradeUpdateView(AdminRequiredMixin,UpdateView):
    model = Grade
    form_class = GradeForm
    template_name = "diary/grade_form.html"
    context_object_name = 'grade'
    def handle_no_permission(self):
            if self.request.user.is_authenticated:
                messages.error(self.request, "Виставляти оцінки може лише адміністратор.")
    
            return super().handle_no_permission()
    def form_valid(self, form):
            # автор оцінки береться з запиту, а не з форми
            form.instance.created_by = self.request.user
    
            response = super().form_valid(form)
    
            messages.success(self.request, "Оцінку виставлено.")
    
            return response
    def get_success_url(self):
            return reverse("diary:student_grades", args=[self.object.student_id])

class GradeDeleteView(AdminRequiredMixin,DeleteView):
    model = Grade
    template_name = 'diary/grade_delete.html'
class SubjectDetailView(LoginRequiredMixin, DetailView):
    model = Subject
    template_name = "diary/subject_detail.html"
    context_object_name = "subject"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["grades"] = (
            Grade.objects
            .filter(subject=self.object, student__role=User.Role.USER, student__is_active=True)
            .select_related("student")
            .order_by("student__username", "created_at")
        )
        context["average"] = (
            Grade.objects.filter(subject=self.object).aggregate(average=Avg("value"))["average"]
        )

        return context


class SubjectListView(LoginRequiredMixin, ListView):
    model = Subject
    template_name = "diary/subject_list.html"
    context_object_name = "subjects"

    def get_queryset(self):
        return (
            Subject.objects
            .filter(is_active=True)
            .annotate(grades_count=Count("grade"), average=Avg("grade__value"))
            .order_by("title")
        )
