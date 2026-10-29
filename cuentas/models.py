from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class UsuarioPersonalizado(AbstractUser):
    edad = models.PositiveIntegerField(null=True, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)