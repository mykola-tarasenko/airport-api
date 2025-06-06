from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport_api.models import Route
from airport_api.serializers import (
    RouteSerializer,
    RouteListSerializer,
    RouteRetrieveSerializer,
)
from airport_api.tests.factories import (
    sample_city,
    sample_airport,
    sample_route,
)

ROUTE_URL = reverse("airport:route-list")


def detail_url(route_id: int):
    return reverse("airport:route-detail", args=[route_id])


class AdminRouteAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test123user", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.uk_city = sample_city(name="London", country="UK")
        self.usa_city = sample_city(name="New York", country="USA")

        self.uk_airport = sample_airport(city=self.uk_city)
        self.usa_airport = sample_airport(city=self.usa_city)

        self.route_uk_usa = sample_route(
            source=self.uk_airport,
            destination=self.usa_airport,
        )
        self.route_usa_uk = sample_route(
            source=self.usa_airport,
            destination=self.uk_airport,
        )

    def test_route_list(self):
        response = self.client.get(ROUTE_URL)
        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_filter_routes_by_source_city(self):
        response = self.client.get(
            ROUTE_URL,
            {"source_city": self.uk_city.name},
        )
        route_uk_usa_serializer = RouteListSerializer(self.route_uk_usa)
        route_usa_uk_serializer = RouteListSerializer(self.route_usa_uk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(route_uk_usa_serializer.data, response.data["results"])
        self.assertNotIn(route_usa_uk_serializer.data, response.data["results"])

    def test_filter_routes_by_source_id(self):
        response = self.client.get(
            ROUTE_URL,
            {"source_id": self.uk_airport.id},
        )
        route_uk_usa_serializer = RouteListSerializer(self.route_uk_usa)
        route_usa_uk_serializer = RouteListSerializer(self.route_usa_uk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(route_uk_usa_serializer.data, response.data["results"])
        self.assertNotIn(route_usa_uk_serializer.data, response.data["results"])

    def test_filter_routes_by_destination_city(self):
        response = self.client.get(
            ROUTE_URL,
            {"destination_city": self.uk_city.name},
        )
        route_uk_usa_serializer = RouteListSerializer(self.route_uk_usa)
        route_usa_uk_serializer = RouteListSerializer(self.route_usa_uk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(route_uk_usa_serializer.data, response.data["results"])
        self.assertIn(route_usa_uk_serializer.data, response.data["results"])

    def test_filter_routes_by_destination_id(self):
        response = self.client.get(
            ROUTE_URL,
            {"destination_id": self.uk_airport.id},
        )
        route_uk_usa_serializer = RouteListSerializer(self.route_uk_usa)
        route_usa_uk_serializer = RouteListSerializer(self.route_usa_uk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(route_uk_usa_serializer.data, response.data["results"])
        self.assertIn(route_usa_uk_serializer.data, response.data["results"])

    def test_route_create(self):
        payload = sample_route(as_dict=True)
        response = self.client.post(ROUTE_URL, payload)
        route = Route.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["source"], route.source.id)
        self.assertEqual(payload["destination"], route.destination.id)
        self.assertEqual(payload["distance"], route.distance)

    def test_route_retrieve(self):
        response = self.client.get(detail_url(self.route_uk_usa.id))
        serializer = RouteRetrieveSerializer(self.route_uk_usa)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_route_partial_update(self):
        payload = {"source": sample_airport().id}
        response = self.client.patch(detail_url(self.route_uk_usa.id), payload)

        self.route_uk_usa = Route.objects.get(pk=self.route_uk_usa.id)
        serializer = RouteSerializer(self.route_uk_usa)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_route_update(self):
        payload = sample_route(distance=300, as_dict=True)
        response = self.client.put(detail_url(self.route_uk_usa.id), payload)

        self.route_uk_usa = Route.objects.get(pk=self.route_uk_usa.id)
        serializer = RouteSerializer(self.route_uk_usa)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_route_destroy(self):
        response = self.client.delete(detail_url(self.route_uk_usa.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(detail_url(self.route_uk_usa.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
