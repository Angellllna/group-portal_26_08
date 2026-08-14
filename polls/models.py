from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

class Poll(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, allow_unicode=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    allow_retake = models.BooleanField(default=False)
    show_result = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    class Meta:
        verbose_name = "Опитування"
        verbose_name_plural = "Опитування"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._build_unique_slug()
        super().save(*args, **kwargs)

    def _build_unique_slug(self):
        # allow_unicode=True — інакше кирилиця перетворюється на порожній рядок
        base = slugify(self.title, allow_unicode=True) or "opytuvannia"
        slug = base
        counter = 2
        while Poll.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base}-{counter}"
            counter += 1
        return slug

    def clean(self):
        if not self.title.strip():
            raise ValidationError("Назва не може бути порожньою.")


class PollPage(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="pages")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    position = models.PositiveIntegerField(default=0)


    class Meta:
        verbose_name = "Сторінка"
        verbose_name_plural = "Сторінки"
        ordering = ["position"]

    def __str__(self):
        return self.title


class Question(models.Model):
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    TEXT = "text"

    QUESTION_TYPES = [
        (SINGLE_CHOICE, "Один варіант"),
        (MULTIPLE_CHOICE, "Декілька варіантів"),
        (TEXT, "Текст"),
    ]

    CHOICE_TYPES = (SINGLE_CHOICE, MULTIPLE_CHOICE)

    page = models.ForeignKey(PollPage, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    question_type = models.CharField(
        max_length=30,
        choices=QUESTION_TYPES,
        default=SINGLE_CHOICE
    )
    is_required = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)


    class Meta:
        verbose_name = "Питання"
        verbose_name_plural = "Питання"
        ordering = ["position"]

    def __str__(self):
        return self.text


    def clean(self):
        if not self.text.strip():
            raise ValidationError("Питання не може бути порожнім.")
        # питання з вибором має містити хоча б один варіант відповіді;
        # перевіряємо лише для збережених питань — у нового ще немає pk,
        # для нього варіанти перевіряє QuestionAdmin через inline-формсет
        if self.pk and self.question_type in self.CHOICE_TYPES:
            if not self.options.exists():
                raise ValidationError(
                    "Питання з вибором повинно мати хоча б один варіант відповіді."
                )


class AnswerOption(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="options" )
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Варіант відповіді"
        verbose_name_plural = "Варіанти відповідей"
        ordering = ["position"]

    def __str__(self):
        return self.text

    def clean(self):
        if not self.text.strip():
            raise ValidationError("Варіант не може бути порожнім.")


class PollResult(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="results")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="poll_results"
    )
    score = models.PositiveIntegerField(default=0)
    max_score = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Результат"
        verbose_name_plural = "Результати"
        constraints = [
            models.UniqueConstraint(
                fields=["poll", "user"],
                name="unique_poll_user_result"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.poll}"


class UserAnswer(models.Model):
    result = models.ForeignKey(
        PollResult,
        on_delete=models.CASCADE,
        related_name="answers"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="user_answers"
    )
    selected_options = models.ManyToManyField(
        AnswerOption,
        blank=True
    )
    text_answer = models.TextField(blank=True)

    class Meta:
        verbose_name = "Відповідь користувача"
        verbose_name_plural = "Відповіді користувачів"

    def __str__(self):
        return f"{self.result.user} - {self.question}"

    def clean(self):
        # питання повинно належати тому самому опитуванню, що й результат
        if self.question.page.poll_id != self.result.poll_id:
            raise ValidationError(
                "Питання належить іншому опитуванню, ніж результат."
            )
