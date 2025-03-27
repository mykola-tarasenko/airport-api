from rest_framework import viewsets

from airport_api.models import City
from serializers import CitySerializer


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
