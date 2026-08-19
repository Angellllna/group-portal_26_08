from django.views.generic import DetailView, ListView

from .models import Material


class MaterialListView(ListView):
    model = Material
    template_name = "materials/material_list.html"
    context_object_name = "materials"
    paginate_by = 9

    def get_queryset(self):
        return (
            Material.objects
            .filter(is_published=True)
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["title"] = "Навчальні матеріали"
        context["description"] = "Матеріали Академії"

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
        # неопублікований матеріал не відкривається через прямий URL
        return Material.objects.filter(is_published=True)
