# Generated by Django 5.0.3 on 2024-03-18 04:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipester', '0006_quantityrange_recipegroup_unit_alter_recipe_url_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredient',
            old_name='recipe_id',
            new_name='recipe',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='ingredients',
        ),
    ]