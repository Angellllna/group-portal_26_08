from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

class Poll(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
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
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def clean(self):
        if not self.title.strip():
            raise ValidationError("Назва не може бути порожньою.")


class PollPage(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
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
    QUESTION_TYPES = [
        ("single_choice", "Один варіант"),
        ("multiple_choice", "Декілька варіантів"),
        ("text", "Текст"),
    ]

    page = models.ForeignKey(PollPage, on_delete=models.CASCADE)
    text = models.TextField()
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPES
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


class AnswerOption(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE )
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
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
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
                name="unique_poll_user"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.poll}"


class UserAnswer(models.Model):
    result = models.ForeignKey(
        PollResult,
        on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
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

