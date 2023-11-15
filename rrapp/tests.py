from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Listing, Rentee, SavedListing
from chat.models import DirectMessagePermission, Permission

User = get_user_model()


class ViewsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.user = User.objects.create_user(
            username="testuser", email="test@example.edu", password="testpassword123"
        )

    @classmethod
    def tearDownClass(cls):
        # Clean up any test-specific data
        super().tearDownClass()


class HomeViewTest(ViewsTestCase):
    def test_home_view_get(self):
        response = self.client.get(reverse("rrapp:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrapp/home.html")

    def test_home_view_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("rrapp:home"),
        )
        self.assertRedirects(
            response, reverse("rrapp:rentee_listings", args=(self.user.id,))
        )


class LoginViewTest(ViewsTestCase):
    def test_login_view_get(self):
        response = self.client.get(reverse("rrapp:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrapp/login_register.html")

    def test_login_view_post_valid_credentials(self):
        response = self.client.post(
            reverse("rrapp:login"),
            {"email": "test@example.edu", "password": "testpassword123"},
        )
        self.assertRedirects(
            response, reverse("rrapp:rentee_listings", args=(self.user.id,))
        )

    def test_login_view_post_invalid_credentials(self):
        response = self.client.post(
            reverse("rrapp:login"),
            {"email": "test@example.edu", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrapp/login_register.html")

    def test_login_view_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("rrapp:login"),
        )
        self.assertRedirects(
            response, reverse("rrapp:rentee_listings", args=(self.user.id,))
        )


class RegisterViewTest(ViewsTestCase):
    def test_register_view_get(self):
        response = self.client.get(reverse("rrapp:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrapp/login_register.html")

    def test_register_view_post_invalid_credentials(self):
        response = self.client.post(
            reverse("rrapp:register"),
            {
                "email": "test@example.edu",
                "password1": "testpassword",
                "password2": "wrongpassword",
                "first_name": "Test",
                "last_name": "User",
                "phone_number": "1234567890",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrapp/login_register.html")

    # def test_register_view_post_valid_credentials(self):
    #     response = self.client.post(
    #         reverse("rrapp:register"),
    #         {
    #             "email": "test2@example.edu",
    #             "password1": "test2password",
    #             "password2": "test2password",
    #             "first_name": "Test",
    #             "last_name": "User",
    #             "phone_number": "1234567890",
    #             "username": "testuser2",
    #         },
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     # self.assertRedirects(
    #     #     response, reverse("rrapp:rentee_listings", args=(self.user.id,))
    #     # )
    #     self.assertTrue(
    #         User.objects.filter(
    #             email="test2@example.edu",
    #         ).exists()
    #     )
    #     user=User.objects.filter(
    #             email="test2@example.edu",
    #         )[0]
    #     self.assertTrue(
    #         Renter.objects.filter(
    #             user = user,
    #         ).exists()
    #     )
    #     self.assertTrue(
    #         Rentee.objects.filter(
    #             user = user,
    #         ).exists()
    #     )

    def test_register_view_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("rrapp:register"),
        )
        self.assertRedirects(
            response, reverse("rrapp:rentee_listings", args=(self.user.id,))
        )


class ListingDetailViewTest(ViewsTestCase):
    def test_listing_detail_view_authenticated_user(self):
        self.client.force_login(self.user)
        listing = Listing.objects.create(
            user=self.user, title="Test Listing", monthly_rent=1000
        )
        response = self.client.get(
            reverse(
                "rrapp:listing_detail",
                args=(
                    self.user.id,
                    listing.id,
                ),
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrapp/listing_detail.html")


class ListingDetailRenteeViewTest(ViewsTestCase):
    def test_listing_detail_rentee_view_authenticated_user(self):
        self.client.force_login(self.user)
        # rentee = Rentee.objects.create(user=self.user)
        listing = Listing.objects.create(
            user=User.objects.create_user(
                username="testuser2", password="testpass2", email="testuser@example.edu"
            ),
            title="Test Listing",
            monthly_rent=1000,
        )
        response = self.client.get(
            reverse(
                "rrapp:rentee_listing_detail",
                args=(
                    self.user.id,
                    listing.id,
                ),
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrapp/rentee_listing_detail.html")

    def test_listing_detail_rentee_view_save_listing(self):
        self.client.force_login(self.user)
        rentee = Rentee.objects.create(user=self.user)
        print(rentee)
        listing = Listing.objects.create(
            user=User.objects.create_user(
                username="testuser2", password="testpass2", email="testuser@example.edu"
            ),
            title="Test Listing",
            monthly_rent=1000,
        )
        response = self.client.post(
            reverse(
                "rrapp:rentee_listing_detail",
                args=(
                    self.user.id,
                    listing.id,
                ),
            ),
            {"shortlist": "true"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            SavedListing.objects.filter(
                rentee_id__user=self.user.id, saved_listings=listing.id
            ).exists()
        )

    def test_listing_detail_rentee_view_connection_request_exists(self):
        self.client.force_login(self.user)
        rentee = Rentee.objects.create(user=self.user)
        print(rentee)
        user2 = User.objects.create_user(
            username="testuser2", password="testpass2", email="testuser2@example.edu"
        )
        listing = Listing.objects.create(
            user=user2,
            title="Test Listing",
            monthly_rent=1000,
        )
        DirectMessagePermission.objects.create(
            sender=self.user.username,
            receiver=user2.username,
            permission=Permission.ALLOWED,
        )
        response = self.client.post(
            reverse(
                "rrapp:rentee_listing_detail",
                args=(
                    self.user.id,
                    listing.id,
                ),
            ),
            {"connection_request": "true"},
        )
        self.assertEqual(response.status_code, 302)

    def test_listing_detail_rentee_view_connection_request_create(self):
        self.client.force_login(self.user)
        rentee = Rentee.objects.create(user=self.user)
        print(rentee)
        user2 = User.objects.create_user(
            username="testuser2", password="testpass2", email="testuser@example.edu"
        )
        listing = Listing.objects.create(
            user=user2,
            title="Test Listing",
            monthly_rent=1000,
        )
        response = self.client.post(
            reverse(
                "rrapp:rentee_listing_detail",
                args=(
                    self.user.id,
                    listing.id,
                ),
            ),
            {"connection_request": "true"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            DirectMessagePermission.objects.filter(
                sender=self.user.username,
                receiver=user2.username,
                permission=Permission.REQUESTED,
            ).exists()
        )


class ListingResultsViewTest(ViewsTestCase):
    def test_listing_results_view_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("rrapp:rentee_listings", args=(self.user.id,)),
            {
                "monthly_rent": 1000,
                "number_of_bedrooms": 2,
                "number_of_bathrooms": 2,
                "room_type": "private",
                "food_groups_allowed": "vegan",
                "pets_allowed": "all",
                "washer": "on",
                "Dryer": "on",
                "utilities_included": "on",
                "furnished": "on",
                "dishwasher": "on",
                "parking": "on",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrapp/rentee_listings.html")


class ConfirmPasswordResetViewTest(ViewsTestCase):
    def test_confirm_password_reset_view_get(self):
        # Assuming a valid uidb64 and token
        uidb64 = "<valid_uidb64>"
        token = "<valid_token>"
        response = self.client.get(
            reverse("rrapp:password_reset_confirm", args=(uidb64, token))
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrapp/password_reset_confirm.html")


class ActivateEmailViewTest(ViewsTestCase):
    def test_activate_email_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("rrapp:activate_email"))
        self.assertIn(response.status_code, [200, 302])
        self.assertTemplateUsed(response, "rrapp/template_activate_account.html")


# class ActivateViewTest(ViewsTestCase):
#     def test_activate_view(self):
#         # self.client.force_login(self.user)
#         uidb64 = "<valid_uidb64>"
#         token = "<valid_token>"
#         response = self.client.get(reverse("rrapp:activate", args=(uidb64, token)))
#         self.assertEqual(response.status_code, 302)
#         # self.assertTemplateUsed(response, "rrapp/template_activate_account.html")


class ListingIndexViewTest(ViewsTestCase):
    def test_listing_index_view_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("rrapp:my_listings", args=(self.user.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrapp/my_listings.html")


class ResetPasswordViewTest(TestCase):
    def test_reset_password_view_get(self):
        client = Client()
        response = client.get(reverse("rrapp:reset_password"))
        self.assertEqual(response.status_code, 200)

    def test_reset_password_view_post(self):
        client = Client()
        response = client.post(
            reverse("rrapp:reset_password"), {"email": "test@example.com"}
        )
        self.assertEqual(response.status_code, 302)


class LogoutViewTest(TestCase):
    def test_logout_view(self):
        client = Client()
        response = client.get(reverse("rrapp:logout"))
        self.assertEqual(response.status_code, 200)


class ListingNewViewTest(TestCase):
    def test_listing_new_view_post(self):
        client = Client()
        response = client.post(
            reverse("rrapp:listing_new", kwargs={"user_id": 1}),
            {"title": "Test Listing", "monthly_rent": 1000},
        )
        self.assertEqual(response.status_code, 302)


class ProfileViewTest(TestCase):
    def test_profile_view_get(self):
        client = Client()
        response = client.get(reverse("rrapp:profile", kwargs={"pk": 1}))
        self.assertIn(response.status_code, [200, 302])

    def test_profile_view_post(self):
        client = Client()
        response = client.post(
            reverse("rrapp:profile", kwargs={"pk": 1}),
            {"first_name": "Test", "last_name": "User"},
        )
        self.assertEqual(response.status_code, 302)


class PublicProfileViewTest(TestCase):
    def test_public_profile_view(self):
        client = Client()
        response = client.get(reverse("rrapp:public_profile", kwargs={"pk": 1}))
        self.assertIn(response.status_code, [200, 302])


class ShortListViewTest(TestCase):
    def test_shortlist_view(self):
        client = Client()
        response = client.get(reverse("rrapp:shortlist", kwargs={"user_id": 1}))
        self.assertIn(response.status_code, [200, 302])


class ListingUpdateViewTest(TestCase):
    def test_listing_update_view_get(self):
        client = Client()
        response = client.get(
            reverse("rrapp:listing_detail_modify", kwargs={"user_id": 1, "pk": 1})
        )
        self.assertIn(response.status_code, [200, 302])

    def test_listing_update_view_post(self):
        client = Client()
        response = client.post(
            reverse("rrapp:listing_detail_modify", kwargs={"user_id": 1, "pk": 1}),
            {"title": "Updated Listing"},
        )
        self.assertIn(response.status_code, [200, 302])
