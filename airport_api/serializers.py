from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.db import transaction

from airport_api.models import (
    City,
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Role,
    CrewMember,
    Flight,
    Ticket,
    Order,
)


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ("id", "name", "country")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "city")


class AirportListSerializer(AirportSerializer):
    city = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name",
    )


class AirportRetrieveSerializer(AirportSerializer):
    city = CitySerializer()


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.PrimaryKeyRelatedField(
        queryset=Airport.objects.select_related("city")
    )
    destination = serializers.PrimaryKeyRelatedField(
        queryset=Airport.objects.select_related("city")
    )

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")

    def validate(self, attrs):
        Route.validate_source_and_destination(
            attrs["source"],
            attrs["destination"],
            serializers.ValidationError,
        )
        return attrs


class RouteListSerializer(RouteSerializer):
    source = serializers.StringRelatedField()
    destination = serializers.StringRelatedField()


class RouteRetrieveSerializer(RouteSerializer):
    source = AirportRetrieveSerializer()
    destination = AirportRetrieveSerializer()


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "model_name", "airplane_type", "rows", "seats_in_row")


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.SlugRelatedField(read_only=True, slug_field="name")


class AirplaneRetrieveSerializer(AirplaneSerializer):
    airplane_type = AirplaneTypeSerializer()

    class Meta:
        model = Airplane
        fields = ("id", "model_name", "airplane_type", "capacity", "rows", "seats_in_row")


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("id", "name")


class CrewMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrewMember
        fields = ("id", "first_name", "last_name", "role")


class CrewMemberListSerializer(CrewMemberSerializer):
    role = serializers.SlugRelatedField(read_only=True, slug_field="name")


class CrewMemberRetrieveSerializer(CrewMemberSerializer):
    role = RoleSerializer()


class FlightSerializer(serializers.ModelSerializer):
    available_seats = serializers.IntegerField(read_only=True)
    route = serializers.PrimaryKeyRelatedField(
        queryset=Route.objects.select_related(
            "source__city",
            "destination__city",
        )
    )
    crew = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CrewMember.objects.select_related("role"),
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "flight_number",
            "available_seats",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "status",
            "crew",
        )


class FlightFilterSerializer(serializers.ModelSerializer):
    departure_time_after = serializers.DateField(required=False)
    departure_time_before = serializers.DateField(required=False)
    arrival_time_after = serializers.DateField(required=False)
    arrival_time_before = serializers.DateField(required=False)

    source_city = serializers.CharField(required=False)
    destination_city = serializers.CharField(required=False)

    class Meta:
        model = Flight
        fields = (
            "departure_time_after",
            "departure_time_before",
            "arrival_time_after",
            "arrival_time_before",
            "source_city",
            "destination_city",
        )

    def validate(self, data):
        if "departure_time_after" in data and "departure_time_before" in data:
            if data["departure_time_after"] > data["departure_time_before"]:
                raise serializers.ValidationError(
                    "departure_time_after must be earlier than departure_time_before."
                )

        if "arrival_time_after" in data and "arrival_time_before" in data:
            if data["arrival_time_after"] > data["arrival_time_before"]:
                raise serializers.ValidationError(
                    "arrival_time_after must be earlier than arrival_time_before."
                )

        if "source_city" in data and "destination_city" in data:
            Route.validate_source_and_destination(
                data["source_city"],
                data["destination_city"],
                serializers.ValidationError,
            )

        return data


class FlightListSerializer(FlightSerializer):
    route = serializers.SlugRelatedField(read_only=True, slug_field="name")
    airplane = serializers.SlugRelatedField(
        read_only=True,
        slug_field="model_name",
    )
    departure_time = serializers.DateTimeField(format="%d %b %Y, %H:%M")
    arrival_time = serializers.DateTimeField(format="%d %b %Y, %H:%M")
    status = serializers.CharField(read_only=True, source="get_status_display")
    crew = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="full_name",
    )


class FlightRetrieveSerializer(FlightSerializer):
    route = RouteListSerializer()
    airplane = AirplaneListSerializer()
    departure_time = serializers.DateTimeField(format="%d %b %Y, %H:%M")
    arrival_time = serializers.DateTimeField(format="%d %b %Y, %H:%M")
    status = serializers.CharField(read_only=True, source="get_status_display")
    crew = CrewMemberListSerializer(many=True)


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "passenger_first_name",
            "passenger_last_name",
            "flight",
        )

    def validate(self, attrs):
        Ticket.validate_row_and_seat(
            attrs["flight"].airplane,
            attrs["row"],
            attrs["seat"],
            ValidationError,
        )
        return attrs


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id","created_at", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets", None)
            order = Order.objects.create(**validated_data)
            Ticket.objects.bulk_create([
                Ticket(order=order, **ticket)
                for ticket in tickets_data
            ])
            return order


class TicketListSerializer(TicketSerializer):
    trip = serializers.CharField(
        source="flight.route.name",
        read_only=True,
    )
    passenger = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = (
            "id",
            "passenger",
            "trip",
        )

    def get_passenger(self, obj):
        return f"{obj.passenger_first_name} {obj.passenger_last_name}"


class TicketRetrieveSerializer(TicketSerializer):
    flight = serializers.SlugRelatedField(
        read_only=True,
        slug_field="flight_number",
    )
    source = serializers.CharField(
        read_only=True,
        source="flight.route.source",
    )
    destination = serializers.CharField(
        read_only=True,
        source="flight.route.destination",
    )
    departure_time = serializers.DateTimeField(
        format="%d %b %Y, %H:%M",
        source="flight.departure_time",
    )
    arrival_time = serializers.DateTimeField(
        format="%d %b %Y, %H:%M",
        source="flight.arrival_time",
    )

    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "passenger_first_name",
            "passenger_last_name",
            "flight",
            "source",
            "destination",
            "departure_time",
            "arrival_time",
        )


class OrderListSerializer(OrderSerializer):
    created_at = serializers.DateTimeField(format="%d %b %Y, %H:%M")
    tickets = TicketListSerializer(many=True, read_only=True)


class OrderRetrieveSerializer(OrderListSerializer):
    tickets = TicketRetrieveSerializer(many=True, read_only=True)
