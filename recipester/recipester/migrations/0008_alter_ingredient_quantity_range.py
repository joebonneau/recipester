# Generated by Django 5.0.3 on 2024-03-18 04:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipester', '0007_rename_recipe_id_ingredient_recipe_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='quantity_range',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='recipester.quantityrange'),
        ),
    ]
