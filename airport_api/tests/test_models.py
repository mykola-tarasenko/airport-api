from django.core.exceptions import ValidationError
from django.test import TestCase

from airport_api.tests.factories import (
    sample_city,
    sample_airport,
    sample_route,
    sample_airplane_type,
    sample_airplane,
    sample_role,
    sample_crew_member,
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


class RoleTest(TestCase):
    def test_str_method(self):
        role = sample_role()
        self.assertEqual(str(role), role.name)


class CrewMemberTest(TestCase):
    def test_name_property(self):
        crew_member = sample_crew_member()
        self.assertTrue(crew_member.full_name)
        self.assertEqual(
            crew_member.full_name,
            f"{crew_member.first_name} {crew_member.last_name}",
        )

    def test_str_method(self):
        crew_member = sample_crew_member()
        self.assertEqual(
            str(crew_member),
            f"{crew_member.full_name} ({crew_member.role.name})",
        )
