from django.test import TestCase
from rrapp.models import Listing

# Create your tests here.

class ListingTestCase(TestCase):
    def setUp(self):
        pass

    def test_animals_can_speak(self):
        """Question should be returned with the query"""
        return True