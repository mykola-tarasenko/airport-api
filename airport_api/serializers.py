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
    source = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()

    def get_source(self, obj):
        return obj.source.city.name

    def get_destination(self, obj):
        return obj.destination.city.name


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
        fields = ("id", "model_name", "type", "rows", "seats_in_row")


class AirplaneListSerializer(AirplaneSerializer):
    type = serializers.SlugRelatedField(read_only=True, slug_field="name")


class AirplaneRetrieveSerializer(AirplaneSerializer):
    type = AirplaneTypeSerializer()

    class Meta:
        model = Airplane
        fields = ("id", "model_name", "type", "capacity", "rows", "seats_in_row")


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
    class Meta:
        model = Flight
        fields = (
            "id",
            "flight_number",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "status",
            "crew",
        )


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
