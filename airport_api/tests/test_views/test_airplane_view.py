from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport_api.models import Airplane
from airport_api.serializers import (
    AirplaneListSerializer,
    AirplaneRetrieveSerializer,
    AirplaneSerializer,
)
from airport_api.tests.factories import (
    sample_airplane_type,
    sample_airplane,
)

AIRPLANE_URL = reverse("airport:airplane-list")


def detail_url(airplane_id: int):
    return reverse("airport:airplane-detail", args=[airplane_id])


class AdminAirplaneAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test123user", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.airplane_type_1 = sample_airplane_type(name="Mid")
        self.airplane_type_2 = sample_airplane_type(name="Heavy")

        self.airplane_1 = sample_airplane(
            model_name="Boeing-747",
            airplane_type=self.airplane_type_1,
        )
        self.airplane_2 = sample_airplane(
            model_name="Boeing-777",
            airplane_type=self.airplane_type_2,
        )

    def test_airplane_list(self):
        response = self.client.get(AIRPLANE_URL)
        airplanes = Airplane.objects.all()
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_filter_airplanes_by_model_name(self):
        response = self.client.get(
            AIRPLANE_URL,
            {"model_name": self.airplane_1.model_name},
        )
        serializer_1 = AirplaneListSerializer(self.airplane_1)
        serializer_2 = AirplaneListSerializer(self.airplane_2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, response.data["results"])
        self.assertNotIn(serializer_2.data, response.data["results"])

    def test_filter_airplanes_by_airplane_type(self):
        response = self.client.get(
            AIRPLANE_URL,
            {"airplane_type": self.airplane_1.airplane_type},
        )
        serializer_1 = AirplaneListSerializer(self.airplane_1)
        serializer_2 = AirplaneListSerializer(self.airplane_2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, response.data["results"])
        self.assertNotIn(serializer_2.data, response.data["results"])

    def test_airplane_create(self):
        payload = sample_airplane(as_dict=True)
        response = self.client.post(AIRPLANE_URL, payload)
        airplane = Airplane.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["model_name"], airplane.model_name)
        self.assertEqual(payload["airplane_type"], airplane.airplane_type.id)

    def test_airplane_retrieve(self):
        response = self.client.get(detail_url(self.airplane_1.id))
        serializer = AirplaneRetrieveSerializer(self.airplane_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_airplane_partial_update(self):
        payload = {"model_name": "Boeing-737"}
        response = self.client.patch(detail_url(self.airplane_1.id), payload)

        self.airplane_1 = Airplane.objects.get(pk=self.airplane_1.id)
        serializer = AirplaneSerializer(self.airplane_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_airplane_update(self):
        payload = sample_airplane(
            model_name="Boeing-737",
            airplane_type=sample_airplane_type(),
            as_dict=True,
        )
        response = self.client.put(detail_url(self.airplane_1.id), payload)

        self.airplane_1 = Airplane.objects.get(pk=self.airplane_1.id)
        serializer = AirplaneSerializer(self.airplane_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_airplane_destroy(self):
        response = self.client.delete(detail_url(self.airplane_1.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(detail_url(self.airplane_1.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
