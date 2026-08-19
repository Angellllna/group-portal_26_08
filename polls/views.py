from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView, FormView, ListView

from .forms import PollPageForm
from .models import AnswerOption, Poll, PollResult, Question, UserAnswer


def session_key(poll):
    return f"poll_answers_{poll.pk}"


class ActivePollMixin:
    """Спільна вибірка: неактивні опитування недоступні звичайним користувачам."""

    def get_queryset(self):
        return Poll.objects.filter(is_active=True)


class PollListView(LoginRequiredMixin, ActivePollMixin, ListView):
    model = Poll
    template_name = "polls/poll_list.html"
    context_object_name = "polls"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                pages_count=Count("pages", distinct=True),
                questions_count=Count("pages__questions", distinct=True),
            )
            .order_by("title")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # одним запитом, щоб не смикати базу на кожне опитування у циклі
        context["passed_ids"] = set(
            PollResult.objects
            .filter(user=self.request.user)
            .values_list("poll_id", flat=True)
        )

        return context


class PollDetailView(LoginRequiredMixin, ActivePollMixin, DetailView):
    model = Poll
    template_name = "polls/poll_detail.html"
    context_object_name = "poll"
    # <str:>, а не <slug:>: slug-и генеруються з українських назв (allow_unicode=True)
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        poll = self.object

        context["pages_count"] = poll.pages.count()
        context["questions_count"] = Question.objects.filter(page__poll=poll).count()
        context["result"] = (
            PollResult.objects.filter(poll=poll, user=self.request.user).first()
        )

        return context


class PollStartView(LoginRequiredMixin, View):
    """Скидає попередній прогрес у сесії й веде на перший етап."""

    def get(self, request, slug):
        poll = get_object_or_404(Poll, slug=slug, is_active=True)

        if not poll.pages.exists():
            messages.error(request, "В опитуванні ще немає жодного етапу.")
            return redirect("polls:poll_detail", slug=poll.slug)

        if not can_take(poll, request.user):
            messages.info(request, "Це опитування вже пройдене й не дозволяє повторне проходження.")
            return redirect("polls:poll_detail", slug=poll.slug)

        request.session[session_key(poll)] = {
            "poll_id": poll.pk,
            "page": 1,
            "max_page": 1,
            "answers": {},
        }

        return redirect("polls:poll_page", slug=poll.slug, page_number=1)


def can_take(poll, user):
    if poll.allow_retake:
        return True
    return not PollResult.objects.filter(poll=poll, user=user).exists()


class PollPageView(LoginRequiredMixin, FormView):
    template_name = "polls/poll_page.html"
    form_class = PollPageForm

    def dispatch(self, request, *args, **kwargs):
        # LoginRequiredMixin відпрацьовує в super().dispatch(), тому
        # анонімного користувача до роботи з сесією не допускаємо
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        self.poll = get_object_or_404(Poll, slug=kwargs["slug"], is_active=True)
        self.pages = list(self.poll.pages.order_by("position", "pk"))

        if not self.pages:
            messages.error(request, "В опитуванні ще немає жодного етапу.")
            return redirect("polls:poll_detail", slug=self.poll.slug)

        if not can_take(self.poll, request.user):
            messages.info(request, "Це опитування вже пройдене й не дозволяє повторне проходження.")
            return redirect("polls:poll_detail", slug=self.poll.slug)

        number = kwargs["page_number"]

        if number < 1 or number > len(self.pages):
            return redirect("polls:poll_detail", slug=self.poll.slug)

        self.state = self.get_state()

        # не даємо перестрибнути етап через змінений URL:
        # відкрити можна лише вже пройдені сторінки та наступну за ними
        if number > self.state["max_page"]:
            messages.warning(request, "Спочатку завершіть попередній етап.")
            return redirect(
                "polls:poll_page",
                slug=self.poll.slug,
                page_number=self.state["max_page"],
            )

        self.page = self.pages[number - 1]
        self.page_number = number
        self.questions = list(self.page.questions.prefetch_related("options"))

        return super().dispatch(request, *args, **kwargs)

    def get_state(self):
        state = self.request.session.get(session_key(self.poll))

        # сесії ще немає (зайшли одразу за URL) або вона з іншого опитування
        if not isinstance(state, dict) or state.get("poll_id") != self.poll.pk:
            state = {"poll_id": self.poll.pk, "page": 1, "max_page": 1, "answers": {}}
            self.request.session[session_key(self.poll)] = state

        state.setdefault("answers", {})
        state.setdefault("max_page", 1)

        return state

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["questions"] = self.questions

        # відповіді з попереднього проходу цієї сторінки підставляються назад у форму
        kwargs["initial"] = {
            name: value
            for name, value in self.state["answers"].items()
            if name in {PollPageForm.field_name(q) for q in self.questions}
        }

        return kwargs

    def form_valid(self, form):
        state = self.state
        # у сесії лежить лише JSON: рядки з id варіантів і текст, без об'єктів моделей
        state["answers"].update(form.cleaned_data)
        state["page"] = self.page_number
        state["max_page"] = max(state["max_page"], min(self.page_number + 1, len(self.pages)))
        self.request.session[session_key(self.poll)] = state
        self.request.session.modified = True

        if self.page_number < len(self.pages):
            return redirect(
                "polls:poll_page",
                slug=self.poll.slug,
                page_number=self.page_number + 1,
            )

        return self.finish(state)

    def finish(self, state):
        """PollResult створюється лише тут — після останнього етапу."""
        answers = state["answers"]
        questions = list(
            Question.objects
            .filter(page__poll=self.poll)
            .prefetch_related("options")
        )

        score = 0
        max_score = 0

        with transaction.atomic():
            # poll і user беруться з URL та request.user, а не з полів форми
            PollResult.objects.filter(poll=self.poll, user=self.request.user).delete()
            result = PollResult.objects.create(poll=self.poll, user=self.request.user)

            for question in questions:
                value = answers.get(PollPageForm.field_name(question))

                if question.question_type in Question.CHOICE_TYPES:
                    correct = {o.pk for o in question.options.all() if o.is_correct}
                    if correct:
                        max_score += 1

                    ids = value if isinstance(value, list) else ([value] if value else [])
                    selected = list(
                        AnswerOption.objects.filter(
                            question=question,
                            pk__in=[i for i in ids if str(i).isdigit()],
                        )
                    )

                    if correct and {o.pk for o in selected} == correct:
                        score += 1

                    if not selected:
                        continue

                    user_answer = UserAnswer.objects.create(
                        result=result, question=question
                    )
                    user_answer.selected_options.set(selected)
                    continue

                if value:
                    UserAnswer.objects.create(
                        result=result, question=question, text_answer=value
                    )

            result.score = score
            result.max_score = max_score
            result.save(update_fields=["score", "max_score"])

        self.request.session.pop(session_key(self.poll), None)

        if self.poll.show_result and max_score:
            messages.success(
                self.request,
                f"Опитування завершено. Правильних відповідей: {score} з {max_score}.",
            )
        else:
            messages.success(self.request, "Опитування завершено. Дякуємо за відповіді!")

        return redirect("polls:poll_detail", slug=self.poll.slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["poll"] = self.poll
        context["page"] = self.page
        context["page_number"] = self.page_number
        context["page_count"] = len(self.pages)

        return context
