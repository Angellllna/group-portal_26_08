from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from accounts.mixins import ModeratorOrAdminRequiredMixin

from .forms import MaterialForm
from .models import Material


def can_manage(user):
    """Керувати матеріалами можуть лише модератори й адміністратори."""
    return user.is_authenticated and user.can_moderate()


class MaterialListView(ListView):
    model = Material
    template_name = "materials/material_list.html"
    context_object_name = "materials"
    paginate_by = 9

    def get_queryset(self):
        queryset = Material.objects.all()

        # звичайний користувач бачить лише опубліковане,
        # модератор — і чернетки, інакше він не зможе їх відредагувати
        if not can_manage(self.request.user):
            queryset = queryset.filter(is_published=True)

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["title"] = "Навчальні матеріали"
        context["description"] = "Матеріали Академії"
        context["can_manage"] = can_manage(self.request.user)

        # активні категорії — тільки ті, у яких є опубліковані матеріали,
        # з людськими назвами замість кодів
        used = set(
            Material.objects
            .filter(is_published=True)
            .values_list("category", flat=True)
        )
        context["categories"] = [
            label for value, label in Material.Category.choices if value in used
        ]

        return context


class MaterialDetailView(DetailView):
    model = Material
    template_name = "materials/material_detail.html"
    context_object_name = "material"

    def get_queryset(self):
        # неопублікований матеріал не відкривається через прямий URL,
        # але модератор мусить його бачити, щоб відредагувати
        if can_manage(self.request.user):
            return Material.objects.all()

        return Material.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage"] = can_manage(self.request.user)
        return context


class MaterialManageMixin(ModeratorOrAdminRequiredMixin):
    """Права модератора/адміністратора + повідомлення про відмову."""

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "У вас немає прав для цієї дії.")

        return super().handle_no_permission()


class MaterialCreateView(MaterialManageMixin, CreateView):
    model = Material
    form_class = MaterialForm
    template_name = "materials/material_form.html"

    def form_valid(self, form):
        # автор береться з запиту, а не з форми — підмінити його неможливо
        form.instance.author = self.request.user

        response = super().form_valid(form)

        messages.success(self.request, "Матеріал успішно додано.")

        return response

    def get_success_url(self):
        return reverse("materials:detail", args=[self.object.slug])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Додати матеріал"
        return context


class MaterialUpdateView(MaterialManageMixin, UpdateView):
    model = Material
    form_class = MaterialForm
    template_name = "materials/material_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(self.request, "Матеріал успішно змінено.")

        return response

    def get_success_url(self):
        return reverse("materials:detail", args=[self.object.slug])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Редагувати матеріал"
        return context


class MaterialDeleteView(MaterialManageMixin, DeleteView):
    model = Material
    template_name = "materials/material_confirm_delete.html"
    context_object_name = "material"
    success_url = reverse_lazy("materials:list")

    def form_valid(self, form):
        messages.success(self.request, "Матеріал видалено.")

        return super().form_valid(form)
