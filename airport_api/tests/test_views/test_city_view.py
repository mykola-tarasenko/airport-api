from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport_api.models import City
from airport_api.serializers import CitySerializer
from airport_api.tests.factories import sample_city

CITY_URL = reverse("airport:city-list")


class AdminCityAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test123user", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.city_1 = sample_city()
        self.city_2 = sample_city(name="Kyiv")

    def test_city_list(self):
        response = self.client.get(CITY_URL)
        cities = City.objects.all()
        serializer = CitySerializer(cities, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_city_create(self):
        payload = sample_city(name="Lviv", as_dict=True)
        response = self.client.post(CITY_URL, payload)
        city = City.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for field in payload:
            self.assertEqual(getattr(city, field), payload[field])
