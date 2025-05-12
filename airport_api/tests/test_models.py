from tkinter.font import names

from django.core.exceptions import ValidationError
from django.test import TestCase

from airport_api.tests.factories import (
    sample_city,
    sample_airport,
    sample_route,
    sample_airplane_type,
    sample_airplane,
)


class CityTest(TestCase):
    def test_str_method(self):
        city =  sample_city()
        self.assertEqual(str(city), city.name)


class AirportTest(TestCase):
    def test_str_method(self):
        airport = sample_airport()
        self.assertEqual(
            str(airport), f"{airport.city.name} - {airport.name}"
        )


class RouteTest(TestCase):
    def test_unique_source_and_destination_validation(self):
        airport = sample_airport(city=sample_city(name="Lviv"))
        with self.assertRaises(ValidationError):
            sample_route(source=airport, destination=airport)

    def test_name_property(self):
        route = sample_route()
        self.assertTrue(route.name)
        self.assertEqual(
            route.name,
            f"{route.source.city.name} - {route.destination.city.name}",
        )

    def test_str_method(self):
        route = sample_route()
        self.assertEqual(str(route), route.name)


class AirplaneTypeTest(TestCase):
    def test_str_method(self):
        airplane_type = sample_airplane_type()
        self.assertEqual(str(airplane_type), airplane_type.name)


class AirplaneTest(TestCase):
    def test_name_property(self):
        airplane = sample_airplane()
        self.assertTrue(airplane.capacity)
        self.assertEqual(
            airplane.capacity,
            airplane.rows * airplane.seats_in_row,
        )

    def test_str_method(self):
        airplane = sample_airplane()
        self.assertEqual(str(airplane), airplane.model_name)
