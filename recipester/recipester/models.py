from django.contrib.auth.models import AbstractUser
from django.db import models


class Recipe(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField()
    description = models.TextField()
    date_saved = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)

    def __str__(self) -> str:
        return str(self.title)

class User(AbstractUser):
    ...
