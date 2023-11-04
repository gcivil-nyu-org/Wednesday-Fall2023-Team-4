from django.test import TestCase
from rrapp.models import Listing  
class ListingTestCase(TestCase):
    def setUp(self):
        # Create a sample listing for testing
        Listing.objects.create(title="Test Listing", monthly_rent=1000, number_of_bedrooms=2)

    def test_listing_attributes(self):
        """Test if listing attributes are set correctly"""
        # Retrieve the listing from the database
        test_listing = Listing.objects.get(title="Test Listing")

        # Test the attributes
        self.assertEqual(test_listing.monthly_rent, 1000)
        self.assertEqual(test_listing.number_of_bedrooms, 2)
        # Add more assertions as needed based on your model's attributes

    def test_create_listing(self):
        """Test creating a new listing"""
        Listing.objects.create(title="New Listing", monthly_rent=1200, number_of_bedrooms=3)
        new_listing = Listing.objects.get(title="New Listing")
        self.assertEqual(new_listing.monthly_rent, 1200)
        self.assertEqual(new_listing.number_of_bedrooms, 3)

    def test_update_listing(self):
        """Test updating an existing listing"""
        test_listing = Listing.objects.get(title="Test Listing")
        test_listing.monthly_rent = 1500
        test_listing.save()
        updated_listing = Listing.objects.get(title="Test Listing")
        self.assertEqual(updated_listing.monthly_rent, 1500)

    def test_delete_listing(self):
        """Test deleting a listing"""
        test_listing = Listing.objects.get(title="Test Listing")
        test_listing.delete()
        with self.assertRaises(Listing.DoesNotExist):
            Listing.objects.get(title="Test Listing")

    def test_animals_can_speak(self):
        """Question should be returned with the query"""
        # Add meaningful assertions related to your test scenario
        self.assertTrue(True)  # Replace this with actual assertions

# Add more test methods as needed to cover different aspects of your code
