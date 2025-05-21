from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport_api.models import AirplaneType
from airport_api.serializers import AirplaneTypeSerializer
from airport_api.tests.factories import sample_airplane_type

AIRPLANE_TYPE_URL = reverse("airport:airplanetype-list")


class AdminAirplaneTypeAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test123user", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.airplane_type_1 = sample_airplane_type(name="Mid")
        self.airplane_type_2 = sample_airplane_type(name="Heavy")

    def test_airplane_type_list(self):
        response = self.client.get(AIRPLANE_TYPE_URL)
        airplane_types = AirplaneType.objects.all()
        serializer = AirplaneTypeSerializer(airplane_types, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_airplane_type_create(self):
        payload = sample_airplane_type(as_dict=True)
        response = self.client.post(AIRPLANE_TYPE_URL, payload)
        airplane = AirplaneType.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for field in payload:
            self.assertEqual(getattr(airplane, field), payload[field])
