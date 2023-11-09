# Changes
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Listing, Rentee

User = get_user_model()


class ViewsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.user = User.objects.create_user(
            email="test@example.com", password="testpassword"
        )

    @classmethod
    def tearDownClass(cls):
        # Clean up any test-specific data
        super().tearDownClass()


class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="testuser1@example.com", password="testpass"
        )


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass", email="testuser2@example.com"
        )

    def test_login_view_get(self):
        response = self.client.get(reverse("rrapp:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrapp/login_register.html")

    def test_login_view_post_valid_credentials(self):
        response = self.client.post(
            reverse("rrapp:login"),
            {"email": "testuser2@example.com", "password": "testpass"},
        )
        self.assertRedirects(
            response, reverse("rrapp:rentee_listings", args=(self.user.id,))
        )

    def test_login_view_post_invalid_credentials(self):
        response = self.client.post(
            reverse("rrapp:login"),
            {"email": "testuser@example.com", "password": "wrongpass"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrapp/login_register.html")


class LogoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="testuser9@example.com", password="testpass"
        )


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_view_get(self):
        response = self.client.get(reverse("rrapp:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrapp/login_register.html")

    def test_register_view_post_invalid_credentials(self):
        response = self.client.post(
            reverse("rrapp:register"),
            {
                "email": "testuser@example.com",
                "password1": "testpass",
                "password2": "wrongpass",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrapp/login_register.html")


class ListingIndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="testuser8@example.com", password="testpass"
        )
        self.listing = Listing.objects.create(
            user=self.user, title="Test Listing", monthly_rent=1000
        )


class ListingDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="testuser7@example.com", password="testpass"
        )
        self.listing = Listing.objects.create(
            user=self.user, title="Test Listing", monthly_rent=1000
        )


class ListingDetailRenteeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass"
        )
        self.rentee = Rentee.objects.create(user=self.user)
        self.listing = Listing.objects.create(
            user=User.objects.create_user(
                username="testuser2",
                password="testpass2",
                email="testuser5@example.com",
            ),
            title="Test Listing",
            monthly_rent=1000,
        )


class ListingResultsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="testuser6@example.com", password="testpass"
        )
        self.listing = Listing.objects.create(
            user=User.objects.create_user(
                username="testuser2", password="testpass2", email="testuser@example.com"
            ),
            title="Test Listing",
            monthly_rent=1000,
        )
