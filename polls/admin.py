from django.contrib import admin

from .models import (
    Poll,
    PollPage,
    Question,
    AnswerOption,
    PollResult,
    UserAnswer,
)

class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
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
