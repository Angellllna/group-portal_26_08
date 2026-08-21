from django import forms
from django.contrib.auth import get_user_model

from .models import Grade, Subject

User = get_user_model()


class GradeForm(forms.ModelForm):
    """Форма виставлення оцінки.

    Поля created_by тут немає: автор проставляється у view з request.user,
    тому підмінити його через POST неможливо.
    """

    class Meta:
        model = Grade
        fields = ["student", "subject", "value", "comment"]
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "student": "Учень",
            "subject": "Предмет",
            "value": "Оцінка",
            "comment": "Коментар",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # у списку лише учні: модератору чи адміністратору оцінку не виставиш
        self.fields["student"].queryset = User.objects.filter(
            role=User.Role.USER,
            is_active=True,
        ).order_by("last_name", "first_name", "username")

        self.fields["subject"].queryset = Subject.objects.filter(
            is_active=True
        ).order_by("title")

        # у моделі value nullable, але оцінка без значення сенсу не має
        self.fields["value"].required = True

    def clean_value(self):
        value = self.cleaned_data.get("value")

        if value is not None and not 1 <= value <= 12:
            raise forms.ValidationError("Оцінка має бути від 1 до 12.")

        return value
