from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView

from .models import Material


class MaterialListView(ListView):
    model = Material
    template_name = "materials/material_list.html"
    context_object_name = "materials"
    paginate_by = 9

    def get_queryset(self):
        return Material.objects.filter(is_published=True).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["title"] = "Навчальні матеріали"
        context["description"] = "Матеріали Академії"
        context["categories"] = (
            Material.objects.filter(is_published=True)
            .values_list("category", flat=True)
            .distinct()
        )

        return context


class MaterialDetailView(DetailView):
    model = Material
    template_name = "materials/material_detail.html"
    context_object_name = "material"

    def get_object(self, queryset=None):
        return get_object_or_404(
            Material,
            pk=self.kwargs["pk"],
            is_published=True,
        )