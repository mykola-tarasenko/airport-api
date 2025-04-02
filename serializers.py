from rest_framework import serializers

from airport_api.models import (
    City,
    Airport,
    Route,
    AirplaneType,
    Airplane,
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
