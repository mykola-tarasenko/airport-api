from django.test import TestCase

from airport_api.tests.factories import (
    sample_city,
    sample_airport,
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
