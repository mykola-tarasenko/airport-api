from rest_framework import serializers

from airport_api.models import City


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ("name", "country")
