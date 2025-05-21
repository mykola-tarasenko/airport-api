from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport_api.models import CrewMember
from airport_api.serializers import (
    CrewMemberSerializer,
    CrewMemberListSerializer,
    CrewMemberRetrieveSerializer,
)
from airport_api.tests.factories import sample_role, sample_crew_member

CREW_MEMBER_URL = reverse("airport:crewmember-list")


def detail_url(crew_member_id: int):
    return reverse("airport:crewmember-detail", args=[crew_member_id])


class AdminCrewMemberAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test123user", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.role_1 = sample_role(name="Steward")
        self.role_2 = sample_role(name="Mechanic")

        self.crew_member_1 = sample_crew_member(
            first_name="Anton",
            last_name="Antonenko",
            role=self.role_1,
        )
        self.crew_member_2 = sample_crew_member(
            first_name="Kateryna",
            last_name="Katerynych",
            role=self.role_2,
        )

    def test_crew_member_list(self):
        response = self.client.get(CREW_MEMBER_URL)
        crew_members = CrewMember.objects.all()
        serializer = CrewMemberListSerializer(crew_members, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_filter_crew_members_by_role(self):
        response = self.client.get(
            CREW_MEMBER_URL,
            {"role": self.role_1.name},
        )
        serializer_1 = CrewMemberListSerializer(self.crew_member_1)
        serializer_2 = CrewMemberListSerializer(self.crew_member_2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, response.data["results"])
        self.assertNotIn(serializer_2.data, response.data["results"])

    def test_filter_crew_members_by_name(self):
        response = self.client.get(
            CREW_MEMBER_URL,
            {"name": self.crew_member_1.first_name},
        )
        serializer_1 = CrewMemberListSerializer(self.crew_member_1)
        serializer_2 = CrewMemberListSerializer(self.crew_member_2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, response.data["results"])
        self.assertNotIn(serializer_2.data, response.data["results"])

    def test_crew_member_create(self):
        payload = sample_crew_member(as_dict=True)
        response = self.client.post(CREW_MEMBER_URL, payload)
        crew_member = CrewMember.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["first_name"], crew_member.first_name)
        self.assertEqual(payload["last_name"], crew_member.last_name)
        self.assertEqual(payload["role"], crew_member.role.id)

    def test_crew_member_retrieve(self):
        response = self.client.get(detail_url(self.crew_member_1.id))
        serializer = CrewMemberRetrieveSerializer(self.crew_member_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_crew_member_partial_update(self):
        payload = {"first_name": "Andrii"}
        response = self.client.patch(detail_url(self.crew_member_1.id), payload)

        self.crew_member_1 = CrewMember.objects.get(pk=self.crew_member_1.id)
        serializer = CrewMemberSerializer(self.crew_member_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_crew_member_update(self):
        payload = sample_crew_member(
            first_name="Andrii",
            last_name="Andriienko",
            as_dict=True,
        )
        response = self.client.put(detail_url(self.crew_member_1.id), payload)

        self.crew_member_1 = CrewMember.objects.get(pk=self.crew_member_1.id)
        serializer = CrewMemberSerializer(self.crew_member_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_crew_member_destroy(self):
        response = self.client.delete(detail_url(self.crew_member_1.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(detail_url(self.crew_member_1.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
