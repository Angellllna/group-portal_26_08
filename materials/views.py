from urllib.parse import urlencode

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from accounts.mixins import ModeratorOrAdminRequiredMixin

from .forms import MaterialCategoryForm, MaterialForm
from .models import Material, MaterialCategory


class MaterialListView(ListView):
    model = Material
    template_name = "materials/material_list.html"
    context_object_name = "materials"
    paginate_by = 9

    def user_can_manage(self):
        user = self.request.user

        return (
            user.is_authenticated
            and hasattr(user, "can_moderate")
            and user.can_moderate()
        )

    def get_queryset(self):
        queryset = Material.objects.select_related(
            "category",
            "author",
        )

        # Звичайний користувач бачить тільки:
        # - опубліковані матеріали
        # - активні категорії
        if not self.user_can_manage():
            queryset = queryset.filter(
                is_published=True,
                category__is_active=True,
            )

        # Пошук
        search_query = self.request.GET.get(
            "search",
            "",
        ).strip()

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
            )

        # Фільтр категорії
        category_slug = self.request.GET.get(
            "category",
            "",
        ).strip()

        if category_slug:
            queryset = queryset.filter(
                category__slug=category_slug
            )

        # Фільтр типу
        material_type = self.request.GET.get(
            "type",
            "",
        ).strip()

        allowed_types = {
            choice[0]
            for choice in Material.MATERIAL_TYPES
        }

        if material_type in allowed_types:
            queryset = queryset.filter(
                material_type=material_type
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_query = self.request.GET.get(
            "search",
            "",
        ).strip()

        category_slug = self.request.GET.get(
            "category",
            "",
        ).strip()

        material_type = self.request.GET.get(
            "type",
            "",
        ).strip()

        can_manage = self.user_can_manage()

        # Активні категорії доступні звичайним користувачам.
        # Модератори також можуть бачити їх.
        context["categories"] = MaterialCategory.objects.filter(
            is_active=True
        )

        context["material_types"] = Material.MATERIAL_TYPES

        context["current_search"] = search_query
        context["current_category"] = category_slug
        context["current_type"] = material_type

        context["can_manage"] = can_manage

        # Зберігаємо search/category/type при переході між сторінками.
        query_params = {}

        if search_query:
            query_params["search"] = search_query

        if category_slug:
            query_params["category"] = category_slug

        if material_type:
            query_params["type"] = material_type

        context["filter_query"] = urlencode(query_params)

        context["has_filters"] = bool(
            search_query
            or category_slug
            or material_type
        )

        return context


class MaterialDetailView(DetailView):
    model = Material
    template_name = "materials/material_detail.html"
    context_object_name = "material"

    def user_can_manage(self):
        user = self.request.user

        return (
            user.is_authenticated
            and hasattr(user, "can_moderate")
            and user.can_moderate()
        )

    def get_queryset(self):
        queryset = Material.objects.select_related(
            "category",
            "author",
        )

        if not self.user_can_manage():
            queryset = queryset.filter(
                is_published=True,
                category__is_active=True,
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage"] = self.user_can_manage()
        return context


class MaterialCreateView(
    ModeratorOrAdminRequiredMixin,
    CreateView,
):
    model = Material
    form_class = MaterialForm
    template_name = "materials/material_form.html"

    def form_valid(self, form):
        # Автор НІКОЛИ не береться з форми.
        form.instance.author = self.request.user

        response = super().form_valid(form)

        messages.success(
            self.request,
            "Матеріал успішно додано.",
        )

        return response


class MaterialUpdateView(
    ModeratorOrAdminRequiredMixin,
    UpdateView,
):
    model = Material
    form_class = MaterialForm
    template_name = "materials/material_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Матеріал успішно змінено.",
        )

        return response


class MaterialDeleteView(
    ModeratorOrAdminRequiredMixin,
    DeleteView,
):
    model = Material
    template_name = "materials/material_confirm_delete.html"
    success_url = reverse_lazy(
        "materials:material_list"
    )

    def post(self, request, *args, **kwargs):
        messages.success(
            request,
            "Матеріал видалено.",
        )

        return super().post(
            request,
            *args,
            **kwargs,
        )


# =========================================================
# КАТЕГОРІЇ
# =========================================================


class MaterialCategoryListView(
    ModeratorOrAdminRequiredMixin,
    ListView,
):
    model = MaterialCategory
    template_name = "materials/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return MaterialCategory.objects.all().order_by(
            "position",
            "title",
        )


class MaterialCategoryCreateView(
    ModeratorOrAdminRequiredMixin,
    CreateView,
):
    model = MaterialCategory
    form_class = MaterialCategoryForm
    template_name = "materials/category_form.html"
    success_url = reverse_lazy(
        "materials:category_list"
    )

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Категорію успішно створено.",
        )

        return response


class MaterialCategoryUpdateView(
    ModeratorOrAdminRequiredMixin,
    UpdateView,
):
    model = MaterialCategory
    form_class = MaterialCategoryForm
    template_name = "materials/category_form.html"
    success_url = reverse_lazy(
        "materials:category_list"
    )

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Категорію успішно змінено.",
        )

        return response


class MaterialCategoryDeleteView(
    ModeratorOrAdminRequiredMixin,
    DeleteView,
):
    model = MaterialCategory
    template_name = "materials/category_confirm_delete.html"
    success_url = reverse_lazy(
        "materials:category_list"
    )

    def post(self, request, *args, **kwargs):
        category = self.get_object()

        # Категорію з матеріалами видаляти не можна.
        if category.materials.exists():
            messages.error(
                request,
                "Категорію не можна видалити, оскільки вона містить матеріали.",
            )

            return redirect(
                "materials:category_list"
            )

        messages.success(
            request,
            "Категорію успішно видалено.",
        )

        return super().post(
            request,
            *args,
            **kwargs,
        )


class MaterialCategoryToggleView(
    ModeratorOrAdminRequiredMixin,
    View,
):
    def post(self, request, pk):
        category = get_object_or_404(
            MaterialCategory,
            pk=pk,
        )

        category.is_active = not category.is_active
        category.save()

        if category.is_active:
            message = "Категорію успішно активовано."
        else:
            message = "Категорію успішно приховано."

        messages.success(
            request,
            message,
        )

        return redirect(
            "materials:category_list"
        )


class MaterialCategoryMoveUpView(
    ModeratorOrAdminRequiredMixin,
    View,
):
    def post(self, request, pk):
        category = get_object_or_404(
            MaterialCategory,
            pk=pk,
        )

        if category.position > 0:
            category.position -= 1
            category.save()

            messages.success(
                request,
                "Порядок категорії змінено.",
            )

        return redirect(
            "materials:category_list"
        )


class MaterialCategoryMoveDownView(
    ModeratorOrAdminRequiredMixin,
    View,
):
    def post(self, request, pk):
        category = get_object_or_404(
            MaterialCategory,
            pk=pk,
        )

        category.position += 1
        category.save()

        messages.success(
            request,
            "Порядок категорії змінено.",
        )

        return redirect(
            "materials:category_list"
        )