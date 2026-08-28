from django import forms
from .models import ForumPost
from .models import ForumThread

class ForumPostForm(forms.ModelForm):
    class Meta:
        model = ForumPost
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 4, "placeholder": "Ваше повідомлення..."})
        }

    def clean_content(self):
        text = self.cleaned_data["content"]

        if not text.strip():
            raise forms.ValidationError("Текст не може бути порожнім або складатися лише з пробілів.")

        if len(text.strip()) < 3:
            raise forms.ValidationError("Повідомлення надто коротке.")

        if len(text) > 2000:
            raise forms.ValidationError("Повідомлення надто довге (максимум 2000 символів).")

        return text


class ForumThreadForm(forms.ModelForm):
    class Meta:
        model = ForumThread
        fields = [
            "category",
            "title",
            "description",
            "is_pinned",
            "is_closed",
        ]