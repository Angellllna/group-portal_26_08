from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import (
    Poll,
    PollPage,
    Question,
    AnswerOption,
    PollResult,
    UserAnswer,
)

class AnswerOptionInlineFormSet(BaseInlineFormSet):
    """Питання типу single_choice / multiple_choice повинно мати варіанти."""

    def clean(self):
        super().clean()
        question_type = self.instance.question_type
        if question_type not in Question.CHOICE_TYPES:
            return

        kept = 0
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get("DELETE"):
                continue
            if form.cleaned_data.get("text"):
                kept += 1

        if kept == 0:
            raise ValidationError(
                "Питання з вибором повинно мати хоча б один варіант відповіді."
            )


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    formset = AnswerOptionInlineFormSet
    extra = 1

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1

class PollPageInline(admin.StackedInline):
    model = PollPage
    extra = 1

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "is_active",
        "allow_retake",
        "show_result",
        "created_at",
    )

    list_filter = (
        "is_active",
        "allow_retake",
        "show_result",
    )

    search_fields = (
        "title",
        "description",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

    inlines = [
        PollPageInline,
    ]

@admin.register(PollPage)
class PollPageAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "poll",
        "position",
    )

    ordering = (
        "poll",
        "position",
    )

    inlines = [
        QuestionInline,
    ]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "text",
        "page",
        "question_type",
        "is_required",
        "position",
    )

    list_filter = (
        "question_type",
        "is_required",
    )

    ordering = (
        "page",
        "position",
    )

    inlines = [
        AnswerOptionInline,
    ]


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = (
        "text",
        "question",
        "is_correct",
        "position",
    )

    ordering = (
        "question",
        "position",
    )

@admin.register(PollResult)
class PollResultAdmin(admin.ModelAdmin):
    list_display = (
        "poll",
        "user",
        "score",
        "max_score",
        "completed_at",
    )

    list_filter = (
        "poll",
    )

@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = (
        "result",
        "question",
        "text_answer",
    )

    filter_horizontal = (
        "selected_options",
    )
