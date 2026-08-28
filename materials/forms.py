from django import forms

from .models import Material, MaterialCategory


class MaterialCategoryForm(forms.ModelForm):
    class Meta:
        model = MaterialCategory
        fields = [
            "title",
            "description",
            "is_active",
            "position",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Назва категорії",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Опис категорії",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
            "position": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                }
            ),
        }


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
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Назва матеріалу",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Опис матеріалу",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "material_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "file": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "external_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://example.com",
                }
            ),
            "youtube_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://www.youtube.com/watch?v=...",
                }
            ),
            "is_published": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Користувач бачить тільки активні категорії
        self.fields["category"].queryset = MaterialCategory.objects.filter(
            is_active=True
        )

    def clean(self):
        cleaned_data = super().clean()

        material_type = cleaned_data.get("material_type")

        uploaded_file = cleaned_data.get("file")
        uploaded_image = cleaned_data.get("image")
        external_url = cleaned_data.get("external_url")
        youtube_url = cleaned_data.get("youtube_url")

        # Під час редагування старий файл/зображення
        # залишається, якщо новий не завантажили.
        old_file = self.instance.file if self.instance.pk else None
        old_image = self.instance.image if self.instance.pk else None

        if material_type == Material.TYPE_FILE:
            if not uploaded_file and not old_file:
                self.add_error(
                    "file",
                    "Для типу «Файл» потрібно додати файл.",
                )

        elif material_type == Material.TYPE_IMAGE:
            if not uploaded_image and not old_image:
                self.add_error(
                    "image",
                    "Для типу «Зображення» потрібно додати зображення.",
                )

        elif material_type == Material.TYPE_LINK:
            if not external_url:
                self.add_error(
                    "external_url",
                    "Для типу «Посилання» потрібно вказати коректне URL.",
                )

        elif material_type == Material.TYPE_YOUTUBE:
            if not youtube_url:
                self.add_error(
                    "youtube_url",
                    "Для типу «YouTube-відео» потрібно вказати YouTube-посилання.",
                )
            else:
                youtube_patterns = (
                    "youtube.com/watch?v=",
                    "www.youtube.com/watch?v=",
                    "youtu.be/",
                )

                if not any(
                    pattern in youtube_url
                    for pattern in youtube_patterns
                ):
                    self.add_error(
                        "youtube_url",
                        "Вкажіть коректне YouTube-посилання.",
                    )

        return cleaned_data