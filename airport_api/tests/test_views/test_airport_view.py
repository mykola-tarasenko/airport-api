from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport_api.models import Airport
from airport_api.serializers import (
    AirportSerializer,
    AirportListSerializer,
    AirportRetrieveSerializer,
)
from airport_api.tests.factories import sample_city, sample_airport

AIRPORT_URL = reverse("airport:airport-list")


def detail_url(airport_id: int):
    return reverse("airport:airport-detail", args=[airport_id])


class AdminAirportAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test123user", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.uk_city = sample_city(country="UK")
        self.usa_city = sample_city(country="USA")

        self.uk_airport = sample_airport(city=self.uk_city)
        self.usa_airport = sample_airport(city=self.usa_city)

    def test_airport_list(self):
        response = self.client.get(AIRPORT_URL)
        airports = Airport.objects.all()
        serializer = AirportListSerializer(airports, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_filter_airports_by_country(self):
        response = self.client.get(AIRPORT_URL,
                                   {"country": f"{self.uk_city.country}"})
        uk_serializer = AirportListSerializer(self.uk_airport)
        usa_serializer = AirportListSerializer(self.usa_airport)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(uk_serializer.data, response.data["results"])
        self.assertNotIn(usa_serializer.data, response.data["results"])

    def test_airport_create(self):
        payload = sample_airport(as_dict=True)
        response = self.client.post(AIRPORT_URL, payload)
        airport = Airport.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["name"], airport.name)
        self.assertEqual(payload["city"], airport.city.id)

    def test_airport_retrieve(self):
        response = self.client.get(detail_url(self.uk_airport.id))
        serializer = AirportRetrieveSerializer(self.uk_airport)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_airport_partial_update(self):
        payload = {"name": "Main"}
        response = self.client.patch(detail_url(self.uk_airport.id), payload)

        self.uk_airport = Airport.objects.get(pk=self.uk_airport.id)
        serializer = AirportSerializer(self.uk_airport)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_airport_update(self):
        payload = sample_airport(name="Main", as_dict=True)
        response = self.client.put(detail_url(self.uk_airport.id), payload)

        self.uk_airport = Airport.objects.get(pk=self.uk_airport.id)
        serializer = AirportSerializer(self.uk_airport)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_airport_destroy(self):
        response = self.client.delete(detail_url(self.uk_airport.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(detail_url(self.uk_airport.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
