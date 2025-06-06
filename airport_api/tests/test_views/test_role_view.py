from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport_api.models import Role
from airport_api.serializers import RoleSerializer
from airport_api.tests.factories import sample_role

ROLE_URL = reverse("airport:role-list")


class AdminRoleAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test123user", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.role_1 = sample_role(name="Mechanic")
        self.role_2 = sample_role(name="Steward")

    def test_role_list(self):
        response = self.client.get(ROLE_URL)
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_role_create(self):
        payload = sample_role(as_dict=True)
        response = self.client.post(ROLE_URL, payload)
        role = Role.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for field in payload:
            self.assertEqual(getattr(role, field), payload[field])
