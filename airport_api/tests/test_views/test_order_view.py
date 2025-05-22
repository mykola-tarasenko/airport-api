from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport_api.models import Order
from airport_api.serializers import (
    OrderListSerializer,
    OrderRetrieveSerializer,
)
from airport_api.tests.factories import (
    sample_ticket,
    sample_order,
    sample_flight,
)

ORDER_URL = reverse("airport:order-list")


def detail_url(order_id: int):
    return reverse("airport:order-detail", args=[order_id])


class AdminOrderAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test123user", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.order = sample_order(user=self.user)

        self.ticket_1 = sample_ticket(row=1, order=self.order)
        self.ticket_2 = sample_ticket(row=2, order=self.order)

    def test_order_list(self):
        response = self.client.get(ORDER_URL)
        orders = Order.objects.filter(user=self.user)
        serializer = OrderListSerializer(orders, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_order_create(self):
        flight = sample_flight()

        payload = {
            "tickets": [
                {
                    "row": 3,
                    "seat": 3,
                    "passenger_first_name": "John",
                    "passenger_last_name": "Doe",
                    "flight": flight.id,
                },
                {
                    "row": 4,
                    "seat": 4,
                    "passenger_first_name": "Alice",
                    "passenger_last_name": "Smith",
                    "flight": flight.id,
                },
            ]
        }

        response = self.client.post(ORDER_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        order_id = response.data["id"]
        order = Order.objects.get(id=order_id)

        self.assertEqual(order.user, self.user)
        self.assertEqual(order.tickets.count(), 2)

    def test_order_retrieve(self):
        response = self.client.get(detail_url(self.order.id))
        serializer = OrderRetrieveSerializer(self.order)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
