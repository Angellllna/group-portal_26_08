from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, FormView
from .models import Poll, PollPage
from .forms import PollPageForm

class PollListView(LoginRequiredMixin, ListView):
    model = Poll
    template_name = "polls/poll_list.html"
    context_object_name = "polls"

    def get_queryset(self):
        return Poll.objects.filter(is_active=True)

class PollDetailView(LoginRequiredMixin, DetailView):
    model = Poll
    template_name = "polls/poll_detail.html"
    context_object_name = "poll"

    def get_queryset(self):
        return Poll.objects.filter(is_active=True)

class PollPageView(LoginRequiredMixin, FormView):
    template_name = "polls/poll_page.html"
    form_class = PollPageForm

    def dispatch(self, request, *args, **kwargs):
        self.poll = get_object_or_404(
            Poll,
            slug=kwargs["slug"],
            is_active=True
        )

        self.pages = list(
            self.poll.pages.order_by("position")
        )
        number = kwargs["page_number"]

        if number < 1 or number > len(self.pages):
            return redirect(
                "polls:poll_detail",
                slug=self.poll.slug
            )

        self.page = self.pages[number - 1]
        self.page_number = number

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["questions"] = self.page.questions.all()

        saved = self.request.session.get(
            f"poll_answers_{self.poll.id}",
            {}
        )
        kwargs["initial"] = saved.get("answers", {})

        return kwargs

    def form_valid(self, form):
        key = f"poll_answers_{self.poll.id}"

        data = self.request.session.get(
            key,
            {"answers": {}}
        )

        data["answers"].update(form.cleaned_data)
        data["poll_id"] = self.poll.id
        data["page"] = self.page_number

        self.request.session[key] = data

        if self.page_number < len(self.pages):
            return redirect(
                "polls:poll_page",
                slug=self.poll.slug,
                page_number=self.page_number + 1
            )

        return redirect(
            "polls:poll_detail",
            slug=self.poll.slug
        )
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["poll"] = self.poll
        context["page"] = self.page
        context["page_number"] = self.page_number
        context["page_count"] = len(self.pages)

        return context