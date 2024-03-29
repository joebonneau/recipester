from django.contrib.auth.models import AbstractUser
from django.db import models


class Recipe(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField(unique=True)
    site_name = models.CharField(max_length=200)
    description = models.TextField()
    date_saved = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    # ingredients = models.ManyToManyField("Ingredient")
    notes = models.ManyToManyField("Note")
    groups = models.ManyToManyField("RecipeGroup")

    def __str__(self) -> str:
        return str(self.title)


class RecipeGroup(models.Model):
    name = models.CharField(max_length=200)
    created_on = models.DateTimeField(auto_now_add=True)


class ShoppingList(models.Model):
    name = models.CharField(max_length=200)
    created_on = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    ingredients = models.ManyToManyField("Ingredient")

    def __str__(self) -> str:
        return str(self.name)


class User(AbstractUser): ...


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    quantity = models.CharField(max_length=200, null=True)
    unit = models.ManyToManyField("Unit")
    quantity_range = models.ForeignKey(
        "QuantityRange", on_delete=models.CASCADE, null=True
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.quantity} {self.name}"


class Unit(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self) -> str:
        return str(self.name)


class QuantityRange(models.Model):
    min = models.FloatField()
    max = models.FloatField()


class Note(models.Model):
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    recipe_id = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return str(self.content)
