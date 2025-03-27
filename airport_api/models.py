from dataclasses import field

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from core import settings


class City(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "cities"
        indexes = [
            models.Index(fields=["name", "country"])
        ]

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
        indexes = [
            models.Index(fields=["name"])
        ]

    def __str__(self):
        return f"{self.city.name} - {self.name}"


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="departing_routes",
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="arriving_routes",
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

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Route, self).save(*args, **kwargs)

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
    rows = models.IntegerField(validators=[MinValueValidator(1)])
    seats_in_row = models.IntegerField(validators=[MinValueValidator(1)])
    type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes",
    )

    class Meta:
        ordering = ("type__name", "model_name")

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.model_name


class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class CrewMember(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="crew_members",
    )

    class Meta:
        ordering = ("role__name", "first_name", "last_name")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.full_name} ({self.role.name})"


class Flight(models.Model):
    STATUS_CHOICES = [
        (0, "Scheduled"),
        (1, "In air"),
        (2, "Landed"),
        (3, "Canceled"),
    ]
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights",
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE,
        related_name="flights",
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=0,
    )
    crew = models.ManyToManyField(CrewMember, related_name="flights")

    class Meta:
        ordering = ("departure_time", "status")

    def clean(self):
        if self.departure_time > self.arrival_time:
            raise ValidationError("Departure can`t be later than arrival.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Flight, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return (f"Flight {self.route}: "
                f"{self.departure_time} - {self.arrival_time}")


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Order: {self.created_at}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    passenger_first_name = models.CharField(max_length=255)
    passenger_last_name = models.CharField(max_length=255)
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets",
    )

    @staticmethod
    def validate_row_and_seat(airplane, row, seat, error_to_raise):
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} number "
                                          f"must be in available "
                                          f"range: (1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_row_and_seat(
            self.flight.airplane,
            self.row,
            self.seat,
            ValidationError,
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Ticket, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.flight} (row: {self.row}, seat: {self.seat})"
