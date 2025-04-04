from rest_framework import serializers

from airport_api.models import (
    City,
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Role,
    CrewMember,
    Flight,
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
