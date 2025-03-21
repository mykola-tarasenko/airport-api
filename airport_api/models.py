from django.db import models


class City(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "cities"

    def __str__(self):
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=255)
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="airports",
    )

    class Meta:
        ordering = ("city__country", "city__name", "name")

    def __str__(self):
        return f"{self.city.name} - {self.name}"
