from django import forms

from .models import Material


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = [
            "title",
            "description",
            "category",
            "material_type",
            "file",
            "image",
            "external_url",
            "youtube_url",
            "is_published",
        ]

    def clean(self):
        cleaned_data = super().clean()

        material_type = cleaned_data.get("material_type")
        file = cleaned_data.get("file")
        image = cleaned_data.get("image")
        external_url = cleaned_data.get("external_url")
        youtube_url = cleaned_data.get("youtube_url")

        if material_type == "file" and not file:
            self.add_error(
                "file",
                "Для типу file потрібно додати файл."
            )

        if material_type == "image" and not image:
            self.add_error(
                "image",
                "Для типу image потрібно додати зображення."
            )

        if material_type == "link" and not external_url:
            self.add_error(
                "external_url",
                "Для типу link потрібно вказати зовнішнє посилання."
            )

        if material_type == "youtube" and not youtube_url:
            self.add_error(
                "youtube_url",
                "Для типу youtube потрібно вказати YouTube-посилання."
            )

        return cleaned_data