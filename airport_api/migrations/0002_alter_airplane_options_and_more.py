# Generated by Django 5.1.7 on 2025-04-14 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("airport_api", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="airplane",
            options={"ordering": ("airplane_type__name", "model_name")},
        ),
        migrations.RenameField(
            model_name="airplane",
            old_name="type",
            new_name="airplane_type",
        ),
        migrations.AddConstraint(
            model_name="city",
            constraint=models.UniqueConstraint(
                fields=("name", "country"), name="unique_city"
            ),
        ),
    ]
