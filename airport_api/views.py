from rest_framework import viewsets

from airport_api.models import (
    City,
    Airport,
)
from serializers import (
    CitySerializer,
    AirportSerializer,
    AirportListSerializer,
    AirportRetrieveSerializer,
)


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        if self.action == "retrieve":
            return AirportRetrieveSerializer
        return self.serializer_class