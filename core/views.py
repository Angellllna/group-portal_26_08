from django.views.generic import TemplateView


class HomePageView(TemplateView):
    """Головна сторінка порталу."""

    template_name = "core/home.html"
