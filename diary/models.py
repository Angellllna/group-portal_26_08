from django.db import models
from config import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy

# Create your models here.
class Subject(models.Model):
    title = models.CharField(max_length=150,blank=False,null=False)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    position = models.IntegerField(blank=True,null=True)
class Grade(models.Model):
    value = models.IntegerField(min=1,max=12,blank=True,null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True)
    comment = models.TextField(max_length=500,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    grade_at = models.DateTimeField(auto_now_add=True)