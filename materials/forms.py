from urllib.parse import urlparse

from django import forms

from .models import Material


class MaterialForm(forms.ModelForm):
    """Форма керування матеріалом.

    Поля author тут навмисно немає: автор проставляється у view з request.user,
    тому підмінити його через POST неможливо.
    """

    class Meta:
        model = Material
        # модель зберігає посилання в одному полі link (і для link, і для youtube),
        # а зображення — у тому самому FileField, що й файл
        fields = [
            "title",
            "description",
            "category",
            "material_type",
            "file",
            "link",
            "is_published",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }
        labels = {
            "file": "Файл або зображення",
            "link": "Посилання (зовнішній ресурс або YouTube)",
        }

    IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp")
    YOUTUBE_HOSTS = ("youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com")

    def clean_title(self):
        title = self.cleaned_data.get("title", "")

        if not title.strip():
            raise forms.ValidationError("Назва не може бути порожньою.")

        return title.strip()

    def clean_description(self):
        description = self.cleaned_data.get("description", "")

        if not description.strip():
            raise forms.ValidationError("Опис не може бути порожнім.")

        return description.strip()

    def clean(self):
        cleaned_data = super().clean()

        material_type = cleaned_data.get("material_type")
        link = cleaned_data.get("link")

        # при редагуванні без вибору нового файлу поле лишається старим —
        # cleaned_data["file"] тоді містить уже збережений FieldFile
        file = cleaned_data.get("file") or getattr(self.instance, "file", None)

        if material_type == Material.MaterialType.FILE and not file:
            self.add_error("file", "Для типу «Файл» потрібно додати файл.")

        if material_type == Material.MaterialType.IMAGE:
            if not file:
                self.add_error("file", "Для типу «Зображення» потрібно додати зображення.")
            elif not str(file).lower().endswith(self.IMAGE_EXTENSIONS):
                self.add_error(
                    "file",
                    "Файл не схожий на зображення: очікується "
                    + ", ".join(self.IMAGE_EXTENSIONS) + ".",
                )

        if material_type == Material.MaterialType.LINK and not link:
            self.add_error("link", "Для типу «Посилання» потрібно вказати зовнішнє посилання.")

        if material_type == Material.MaterialType.YOUTUBE:
            if not link:
                self.add_error("link", "Для типу «YouTube» потрібно вказати YouTube-посилання.")
            elif urlparse(link).hostname not in self.YOUTUBE_HOSTS:
                self.add_error("link", "Це не схоже на посилання YouTube.")

        return cleaned_data


    def _post_clean(self):
        super()._post_clean()

        # Material.clean() додає загальне "Додайте файл або посилання".
        # Коли вже є конкретна помилка про потрібне для цього типу поле,
        # дублювати загальну не треба — вона лише збиває з пантелику.
        if self.errors.get("file") or self.errors.get("link"):
            self.errors.pop("__all__", None)
