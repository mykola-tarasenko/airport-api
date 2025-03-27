from rest_framework import serializers

from airport_api.models import (
    City,
    Airport,
)


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ("name", "country")


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
