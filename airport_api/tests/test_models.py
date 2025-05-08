from django.test import TestCase

from airport_api.tests.factories import sample_city


class CityTest(TestCase):
    def test_str_method(self):
        city =  sample_city()
        self.assertEqual(str(city), city.name)
