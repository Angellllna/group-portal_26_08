from django import forms

from .models import Question


class PollPageForm(forms.Form):
    """Форма одного етапу опитування.

    Поля будуються з питань поточної сторінки, тому користувач фізично
    не може надіслати варіант, який належить іншому питанню або іншій
    сторінці: ChoiceField приймає лише ті id, які є в choices.
    """

    def __init__(self, *args, questions=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.questions = list(questions or [])

        for question in self.questions:
            self.fields[self.field_name(question)] = self._build_field(question)

    @staticmethod
    def field_name(question):
        return f"question_{question.pk}"

    def _build_field(self, question):
        common = {
            "label": question.text,
            "required": question.is_required,
        }

        if question.question_type in Question.CHOICE_TYPES:
            choices = [
                (str(option.pk), option.text)
                for option in question.options.all()
            ]

            if question.question_type == Question.MULTIPLE_CHOICE:
                return forms.MultipleChoiceField(
                    choices=choices,
                    widget=forms.CheckboxSelectMultiple,
                    **common,
                )

            # single_choice — радіокнопки, тобто рівно один варіант
            return forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect,
                **common,
            )

        return forms.CharField(
            widget=forms.Textarea(attrs={"rows": 3}),
            **common,
        )
