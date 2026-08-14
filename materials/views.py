from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from accounts.mixins import ModeratorOrAdminRequiredMixin

from .models import Material
from .forms import MaterialForm


class MaterialListView(ListView):
    model = Material
    template_name = "materials/material_list.html"
    context_object_name = "materials"


class MaterialDetailView(DetailView):
    model = Material
    template_name = "materials/material_detail.html"
    context_object_name = "material"
    slug_field = "slug"
    slug_url_kwarg = "slug"


class MaterialCreateView(
    ModeratorOrAdminRequiredMixin,
    CreateView,
):
    model = Material
    form_class = MaterialForm
    template_name = "materials/material_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user

        response = super().form_valid(form)

        messages.success(
            self.request,
            "Матеріал успішно додано."
        )

        return response

    def get_success_url(self):
        return self.object.get_absolute_url()


class MaterialUpdateView(
    ModeratorOrAdminRequiredMixin,
    UpdateView,
):
    model = Material
    form_class = MaterialForm
    template_name = "materials/material_form.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Матеріал успішно змінено."
        )

        return response

    def get_success_url(self):
        return self.object.get_absolute_url()


class MaterialDeleteView(
    ModeratorOrAdminRequiredMixin,
    DeleteView,
):
    model = Material
    template_name = "materials/material_confirm_delete.html"
    context_object_name = "material"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    success_url = reverse_lazy("materials:material_list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Матеріал видалено."
        )

        return super().form_valid(form)