from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint


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


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="departing_routs",
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="arriving_routs",
    )
    distance = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        constraints = (
            UniqueConstraint(
                fields=["source", "destination"],
                name="unique_route",
            ),
        )
        ordering = ("source", "destination")

    @staticmethod
    def validate_source_and_destination(
            source,
            destination,
            error_to_raise,
    ):
        if source == destination:
            raise error_to_raise("The source can`t equal destination.")

    def clean(self):
        Route.validate_source_and_destination(
            self.source,
            self.destination,
            ValidationError,
        )

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Route, self).save(
            force_insert, force_update, using, update_fields
        )

    @property
    def name(self):
        return f"{self.source.city.name} - {self.destination.city.name}"

    def __str__(self):
        return self.name


class AirplaneType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    model_name = models.CharField(max_length=255)
    rows = models.IntegerField(MinValueValidator(1))
    seats_in_row = models.IntegerField(MinValueValidator(1))
    type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes",
    )

    class Meta:
        ordering = ("type__name", "model_name")

    def __str__(self):
        return self.model_name
