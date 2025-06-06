# Generated by Django 5.1.7 on 2025-05-15 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("airport_api", "0003_crewmember_photo"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="ticket",
            options={"ordering": ("row", "seat")},
        ),
        migrations.AddConstraint(
            model_name="ticket",
            constraint=models.UniqueConstraint(
                fields=("flight", "row", "seat"), name="unique_flight_seat"
            ),
        ),
    ]
