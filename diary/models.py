from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy
from django.core.validators import MaxValueValidator, MinValueValidator


def title_validate(title):
    if " " in title:
        raise ValidationError(gettext_lazy("Назва предмету не повинна містити пробілів"))
# Create your models here.

class Subject(models.Model):
    POSITION_CHOICES = [
        ("secondary", "Secondary"),
        ("main", "Main"),
    ]
    title = models.CharField(max_length=150,blank=False,null=False,validators=[title_validate])
    description = models.TextField(max_length=500,blank=True,null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, blank=True, null=True)
    class Meta:
        verbose_name = "предмет"
        verbose_name_plural = "предмети"
        ordering = ["-position"]
    def __str__(self):
        return f'{self.title} - {self.description}'
    
class Grade(models.Model):
    value = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)],blank=True,null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name="grades")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,related_name="created_grades")
    comment = models.TextField(max_length=500,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)
    grade_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    class Meta:
        verbose_name = "оцінки"
        verbose_name_plural = "оцінки"
        ordering = ["-created_at"]
    def __str__(self):
            return f'{self.value} - {self.subject.title} - {self.student}'