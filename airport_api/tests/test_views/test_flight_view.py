from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import F, Count
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport_api.models import Flight
from airport_api.serializers import (
    FlightSerializer,
    FlightListSerializer,
    FlightRetrieveSerializer,
)
from airport_api.tests.factories import (
    sample_city,
    sample_airport,
    sample_flight,
    sample_route,
    sample_airplane,
)

FLIGHT_URL = reverse("airport:flight-list")


def detail_url(flight_id: int):
    return reverse("airport:flight-detail", args=[flight_id])


class AdminFlightAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test123user", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.city_1 = sample_city(name="Lviv")
        self.city_2 = sample_city(name="Kyiv")

        self.airport_1 = sample_airport(city=self.city_1)
        self.airport_2 = sample_airport(city=self.city_2)

        self.route_1 = sample_route(
            source=self.airport_1,
            destination=self.airport_2,
        )
        self.route_2 = sample_route(
            source=self.airport_2,
            destination=self.airport_1,
        )

        self.flight_1 = sample_flight(
            flight_number="LK1234",
            route=self.route_1,
            airplane=sample_airplane(),
            departure_time="2025-5-1 10:00+00:00",
            arrival_time="2025-5-1 14:00+00:00",
        )
        self.flight_2 = sample_flight(
            flight_number="KL1234",
            route=self.route_2,
            airplane=sample_airplane(),
            departure_time="2025-5-3 12:00+00:00",
            arrival_time="2025-5-3 16:00+00:00",
        )

        self.expected_data_1 = FlightListSerializer(Flight.objects.annotate(
            available_seats=(
                F("airplane__seats_in_row") * F("airplane__rows")
                - Count("tickets")
            )
        ).get(pk=self.flight_1.id)).data
        self.expected_data_2 = FlightListSerializer(Flight.objects.annotate(
            available_seats=(
                    F("airplane__seats_in_row") * F("airplane__rows")
                    - Count("tickets")
            )
        ).get(pk=self.flight_2.id)).data

    def test_flight_list(self):
        response = self.client.get(FLIGHT_URL)
        flights = Flight.objects.annotate(
            available_seats=(
                    F("airplane__seats_in_row") * F("airplane__rows")
                    - Count("tickets")
            )
        )
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_filter_flights_by_departure_time_after(self):
        response = self.client.get(
            FLIGHT_URL,
            {"departure_time_after": "2025-5-2"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.expected_data_1, response.data["results"])
        self.assertIn(self.expected_data_2, response.data["results"])

    def test_filter_flights_by_departure_time_before(self):
        response = self.client.get(
            FLIGHT_URL,
            {"departure_time_before": "2025-5-2"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.expected_data_1, response.data["results"])
        self.assertNotIn(self.expected_data_2, response.data["results"])

    def test_filter_flights_by_arrival_time_after(self):
        response = self.client.get(
            FLIGHT_URL,
            {"arrival_time_after": "2025-5-2"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.expected_data_1, response.data["results"])
        self.assertIn(self.expected_data_2, response.data["results"])

    def test_filter_flights_by_arrival_time_before(self):
        response = self.client.get(
            FLIGHT_URL,
            {"arrival_time_before": "2025-5-2"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.expected_data_1, response.data["results"])
        self.assertNotIn(self.expected_data_2, response.data["results"])

    def test_filter_flights_by_source_city(self):
        response = self.client.get(
            FLIGHT_URL,
            {"source_city": self.city_1},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.expected_data_1, response.data["results"])
        self.assertNotIn(self.expected_data_2, response.data["results"])

    def test_filter_flights_by_destination_city(self):
        response = self.client.get(
            FLIGHT_URL,
            {"destination_city": self.city_2},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.expected_data_1, response.data["results"])
        self.assertNotIn(self.expected_data_2, response.data["results"])

    def test_flight_create(self):
        payload = sample_flight(as_dict=True)
        response = self.client.post(FLIGHT_URL, payload)
        flight = Flight.objects.annotate(
            available_seats=(
                    F("airplane__seats_in_row") * F("airplane__rows")
                    - Count("tickets")
            )
        ).get(pk=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["flight_number"], flight.flight_number)
        self.assertEqual(payload["route"], flight.route.id)
        self.assertEqual(payload["airplane"], flight.airplane.id)
        self.assertEqual(
            datetime.strptime(
                payload["departure_time"],
                "%Y-%m-%d %H:%M%z",
            ),
            flight.departure_time,
        )
        self.assertEqual(
            datetime.strptime(
                payload["arrival_time"],
                "%Y-%m-%d %H:%M%z",
            ),
            flight.arrival_time,
        )
        self.assertEqual(payload["status"], flight.status)

    def test_flight_retrieve(self):
        response = self.client.get(detail_url(self.flight_1.id))

        flight = Flight.objects.annotate(
            available_seats=(
                F("airplane__seats_in_row") * F("airplane__rows")
                - Count("tickets")
            )
        ).get(pk=self.flight_1.id)

        serializer = FlightRetrieveSerializer(flight)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_flight_partial_update(self):
        payload = {"flight_number": "LK0987"}
        response = self.client.patch(detail_url(self.flight_1.id), payload)

        self.flight_1 = Flight.objects.get(pk=self.flight_1.id)
        serializer = FlightSerializer(self.flight_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_flight_update(self):
        payload = sample_flight(as_dict=True)
        response = self.client.put(detail_url(self.flight_1.id), payload)

        self.flight_1 = Flight.objects.get(pk=self.flight_1.id)
        serializer = FlightSerializer(self.flight_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_flight_destroy(self):
        response = self.client.delete(detail_url(self.flight_1.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(detail_url(self.flight_1.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
