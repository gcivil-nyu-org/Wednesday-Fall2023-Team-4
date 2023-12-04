from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

import datetime

from rrapp.forms import QuizForm

from .models import Listing, Rentee, Renter, SavedListing, Rating, Pets
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
        self.assertRedirects(response, reverse("rrapp:rentee_listings"))


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
        self.assertRedirects(response, reverse("rrapp:rentee_listings"))

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
        self.assertRedirects(response, reverse("rrapp:rentee_listings"))


class RegisterViewTest(ViewsTestCase):
    def test_register_view_get(self):
        response = self.client.get(reverse("rrapp:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrapp/login_register.html")

    def test_register_view_post_invalid_data(self):
        response = self.client.post(
            reverse("rrapp:register"),
            {
                "email": "test@example.com",
                "password1": "testpassword",
                "password2": "wrongpassword",
                "first_name": "Test1",
                "last_name": "User1",
                "phone_number": "1234",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrapp/login_register.html")
        self.assertFormError(response, "form", "username", "This field is required.")
        self.assertFormError(
            response,
            "form",
            "email",
            "Please enter a valid school email. End with .edu",
        )
        self.assertFormError(
            response, "form", "first_name", "First name must only contain letters"
        )
        self.assertFormError(
            response, "form", "last_name", "Last name must only contain letters"
        )
        self.assertFormError(
            response,
            "form",
            "phone_number",
            "Please enter a valid phone number with length 10-12",
        )

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

    def test_register_view_post_valid_credentials(self):
        data = {
            "email": "test2@example.edu",
            "password1": "test2password",
            "password2": "test2password",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "1234567890",
            "username": "testuser222",
            "pets": "dogs",
            "food_group": "all",
            "birth_date": timezone.now().date() - timedelta(days=5),
        }

        response = self.client.post(
            reverse("rrapp:register"),
            data,
        )

        self.assertTrue(
            User.objects.filter(
                email="test2@example.edu",
            ).exists()
        )
        newUser = User.objects.get(
            email="test2@example.edu",
        )
        self.assertRedirects(
            response,
            expected_url=reverse("rrapp:rentee_listings"),
            status_code=302,
        )

        self.assertTrue(
            Renter.objects.filter(
                user=newUser,
            ).exists()
        )
        self.assertTrue(
            Rentee.objects.filter(
                user=newUser,
            ).exists()
        )

    def test_register_view_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("rrapp:register"),
        )
        self.assertRedirects(response, reverse("rrapp:rentee_listings"))


class ListingDetailViewTest(ViewsTestCase):
    def test_listing_detail_view_unauthenticated_user(self):
        # self.client.force_login(self.user)
        listing = Listing.objects.create(
            user=self.user, title="Test Listing", monthly_rent=1000
        )
        response = self.client.get(
            reverse(
                "rrapp:listing_detail",
                args=(listing.id,),
            )
        )
        self.assertEqual(response.status_code, 302)

    def test_listing_detail_view_authenticated_user(self):
        self.client.force_login(self.user)
        listing = Listing.objects.create(
            user=self.user, title="Test Listing", monthly_rent=1000
        )
        response = self.client.get(
            reverse(
                "rrapp:listing_detail",
                args=(listing.id,),
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrapp/listing_detail.html")

    def test_listing_detail_view_authenticated_malicious_user(self):
        self.client.force_login(self.user)
        user2 = User.objects.create_user(
            username="testuser2", email="test2@example.edu", password="test2password123"
        )
        listing = Listing.objects.create(
            user=user2, title="Test Listing", monthly_rent=1000
        )
        response = self.client.get(
            reverse(
                "rrapp:listing_detail",
                args=(listing.id,),
            )
        )
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "rrapp/403.html")


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
                args=(listing.id,),
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrapp/rentee_listing_detail.html")

    def test_listing_detail_rentee_view_matching_user(self):
        self.user.pets = Pets.DOGS
        self.user.birth_date = datetime.date.today() - datetime.timedelta(365 * 20)
        self.user.save()
        self.client.force_login(self.user)
        self.assertTrue(self.user.pets == Pets.DOGS)
        listing = Listing.objects.create(
            user=User.objects.create_user(
                username="testuser2", password="testpass2", email="testuser@example.edu"
            ),
            title="Test Listing",
            monthly_rent=1000,
            restrict_to_matches=True,
            pets_allowed=Pets.DOGS,
        )
        response = self.client.get(
            reverse(
                "rrapp:rentee_listing_detail",
                args=(listing.id,),
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrapp/rentee_listing_detail.html")

    def test_listing_detail_rentee_view_nonmatching_user(self):
        self.user.pets = Pets.DOGS
        self.user.birth_date = datetime.date.today() - datetime.timedelta(365 * 20)
        self.user.save()
        self.client.force_login(self.user)
        self.assertTrue(self.user.pets == Pets.DOGS)
        listing = Listing.objects.create(
            user=User.objects.create_user(
                username="testuser2", password="testpass2", email="testuser@example.edu"
            ),
            title="Test Listing",
            monthly_rent=1000,
            restrict_to_matches=True,
            pets_allowed=Pets.CATS,
        )
        response = self.client.get(
            reverse(
                "rrapp:rentee_listing_detail",
                args=(listing.id,),
            )
        )
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "rrapp/403.html")

    def test_listing_detail_rentee_view_save_listing(self):
        self.client.force_login(self.user)
        Rentee.objects.create(user=self.user)
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
                args=(listing.id,),
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
        Rentee.objects.create(user=self.user)
        user2 = User.objects.create_user(
            username="testuser2", password="testpass2", email="testuser2@example.edu"
        )
        listing = Listing.objects.create(
            user=user2,
            title="Test Listing",
            monthly_rent=1000,
        )
        DirectMessagePermission.objects.create(
            sender=self.user,
            receiver=user2,
            permission=Permission.ALLOWED,
        )
        response = self.client.post(
            reverse(
                "rrapp:rentee_listing_detail",
                args=(listing.id,),
            ),
            {"connection_request": "true"},
        )
        self.assertEqual(response.status_code, 302)

    def test_listing_detail_rentee_view_connection_request_create(self):
        self.client.force_login(self.user)
        Rentee.objects.create(user=self.user)
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
                args=(listing.id,),
            ),
            {"connection_request": "true"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            DirectMessagePermission.objects.filter(
                sender=self.user,
                receiver=user2,
                permission=Permission.REQUESTED,
            ).exists()
        )


class ListingResultsViewTest(ViewsTestCase):
    def test_listing_results_view_unauthenticated_user(self):
        # self.client.force_login(self.user)
        response = self.client.get(
            reverse("rrapp:rentee_listings"),
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
        self.assertEqual(response.status_code, 302)

    def test_listing_results_view_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("rrapp:rentee_listings"),
            {
                "monthly_rent_min": 500,
                "monthly_rent_max": 1500,
                "number_of_bedrooms_min": 2,
                "number_of_bedrooms_max": 5,
                "number_of_bathrooms_min": 2,
                "number_of_bathrooms_max": 4,
                "room_type": "private",
                "food_groups_allowed": "vegan",
                "pets_allowed": "all",
                "washer": "on",
                "dryer": "on",
                "utilities_included": "on",
                "furnished": "on",
                "dishwasher": "on",
                "parking": "on",
                "sort": "-monthly_rent",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrapp/rentee_listings.html")

    def test_listing_results_view_recommendation_all_0_authenticated_user(self):
        self.client.force_login(self.user)
        self.user.birth_date = timezone.now().date() - timedelta(days=0)
        self.user.save()
        user2 = User.objects.create_user(
            username="testuser2",
            password="testpass2",
            email="testuser2@example.edu",
        )
        user2.smokes = True
        user2.birth_date = timezone.now().date() - timedelta(days=0)
        user2.save()
        print(user2.birth_date)
        user3 = User.objects.create_user(
            username="testuser3",
            password="testpass3",
            email="testuser3@example.edu",
        )
        user3.pets = Pets.DOGS
        user3.birth_date = timezone.now().date() - timedelta(days=0)
        user3.save()
        Listing.objects.create(
            user=user2,
            title="Test Listing 2-1",
            monthly_rent=1000,
        )
        Listing.objects.create(
            user=user3,
            title="Test Listing 3-1",
            monthly_rent=1000,
        )
        Listing.objects.create(
            user=user2,
            title="Test Listing 2-2",
            monthly_rent=1100,
        )
        Rating.objects.create(rater=self.user, ratee=user2, rating=4.0)
        Rating.objects.create(rater=user3, ratee=user2, rating=1.0)
        Rating.objects.create(rater=user2, ratee=user3, rating=5.0)
        response = self.client.get(
            reverse("rrapp:rentee_listings"),
            {
                "sort": "recommendation",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrapp/rentee_listings.html")

    # def test_listing_results_view_recommendation_not_all_0_authenticated_user(self):
    #     self.client.force_login(self.user)
    #     self.user.birth_date = timezone.now().date() - timedelta(days=6000)
    #     self.user.save()
    #     user2 = User.objects.create_user(
    #         username="testuser2",
    #         password="testpass2",
    #         email="testuser2@example.edu",
    #     )
    #     user2.smokes=True
    #     user2.birth_date = timezone.now().date() - timedelta(days=7000)
    #     user2.save()
    #     print(user2.birth_date)
    #     user3 = User.objects.create_user(
    #         username="testuser3",
    #         password="testpass3",
    #         email="testuser3@example.edu",
    #     )
    #     user3.pets=Pets.DOGS
    #     user3.birth_date = timezone.now().date() - timedelta(days=5500)
    #     user3.save()
    #     Listing.objects.create(
    #         user=user2,
    #         title="Test Listing 2-1",
    #         monthly_rent=1000,
    #     )
    #     Listing.objects.create(
    #         user=user3,
    #         title="Test Listing 3-1",
    #         monthly_rent=1000,
    #     )
    #     Listing.objects.create(
    #         user=user2,
    #         title="Test Listing 2-2",
    #         monthly_rent=1100,
    #     )
    #     Rating.objects.create(rater=self.user, ratee=user2, rating=4.0)
    #     Rating.objects.create(rater=user3, ratee=user2, rating=1.0)
    #     Rating.objects.create(rater=user2, ratee=user3, rating=5.0)
    #     response = self.client.get(
    #         reverse("rrapp:rentee_listings"),
    #         {
    #             "sort": "recommendation",
    #         },
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "rrapp/rentee_listings.html")

    def test_listing_results_view_recommendation_no_rating_authenticated_user(self):
        self.client.force_login(self.user)
        user2 = User.objects.create_user(
            username="testuser2",
            password="testpass2",
            email="testuser2@example.edu",
        )
        user2.smokes = True
        user3 = User.objects.create_user(
            username="testuser3",
            password="testpass3",
            email="testuser3@example.edu",
        )
        user3.pets = Pets.DOGS
        Listing.objects.create(
            user=user2,
            title="Test Listing 2-1",
            monthly_rent=1000,
        )
        Listing.objects.create(
            user=user3,
            title="Test Listing 3-1",
            monthly_rent=1000,
        )
        Listing.objects.create(
            user=user2,
            title="Test Listing 2-2",
            monthly_rent=1100,
        )
        response = self.client.get(
            reverse("rrapp:rentee_listings"),
            {
                "sort": "recommendation",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrapp/rentee_listings.html")

    def test_listing_results_view_authenticated_user_matched(self):
        self.client.force_login(self.user)
        user2 = User.objects.create_user(
            username="testuser2", password="testpass2", email="testuser@example.edu"
        )
        listing1 = Listing.objects.create(
            user=user2,
            title="Test Listing",
            monthly_rent=1000,
        )
        listing2 = Listing.objects.create(
            user=user2,
            title="Test Listing 2",
            monthly_rent=2000,
        )
        response = self.client.get(
            reverse("rrapp:rentee_listings"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrapp/rentee_listings.html")
        self.assertEqual(len(response.context['queried_listings_page']), 2)
        self.assertEqual(response.context['queried_listings_page'][0], listing1)
        self.assertEqual(response.context['queried_listings_page'][1], listing2)

    def test_listing_results_view_authenticated_user_unmatched(self):
        self.user.smokes = True
        self.user.save()
        self.client.force_login(self.user)
        user2 = User.objects.create_user(
            username="testuser2", password="testpass2", email="testuser@example.edu"
        )
        listing1 = Listing.objects.create(
            user=user2,
            title="Test Listing",
            monthly_rent=1000,
        )
        listing2 = Listing.objects.create(
            user=user2,
            title="Test Listing 2",
            monthly_rent=2000,
            restrict_to_matches=True,
            smoking_allowed=False,
        )
        response = self.client.get(
            reverse("rrapp:rentee_listings"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rrapp/rentee_listings.html")
        # only the first listing should be available
        self.assertEqual(len(response.context['queried_listings_page']), 1)
        self.assertEqual(response.context['queried_listings_page'][0], listing1)
        self.assertNotEqual(response.context['queried_listings_page'][0], listing2)


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


class VerifyEmailViewTest(ViewsTestCase):
    def test_verify_email_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("rrapp:verify_email"))
        self.assertIn(response.status_code, [200, 302])
        self.assertTemplateUsed(response, "rrapp/template_verify_account.html")


class ListingIndexViewTest(ViewsTestCase):
    def test_listing_index_view_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("rrapp:my_listings"))
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
            reverse("rrapp:listing_new"),
            {"title": "Test Listing", "monthly_rent": 1000},
        )
        self.assertEqual(response.status_code, 302)


class ProfileViewTest(TestCase):
    def test_profile_view_get(self):
        client = Client()
        response = client.get(reverse("rrapp:profile"))
        self.assertIn(response.status_code, [200, 302])

    def test_profile_view_post(self):
        client = Client()
        response = client.post(
            reverse("rrapp:profile"),
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
        response = client.get(reverse("rrapp:shortlist"))
        self.assertIn(response.status_code, [200, 302])


class ListingUpdateViewTest(TestCase):
    def test_listing_update_view_get(self):
        client = Client()
        response = client.get(reverse("rrapp:listing_detail_modify", kwargs={"pk": 1}))
        self.assertIn(response.status_code, [200, 302])

    def test_listing_update_view_post(self):
        client = Client()
        response = client.post(
            reverse("rrapp:listing_detail_modify", kwargs={"pk": 1}),
            {"title": "Updated Listing"},
        )
        self.assertIn(response.status_code, [200, 302])


class PersonalQuizViewTest(TestCase):
    def test_personal_quiz_view_get(self):
        client = Client()
        response = client.get(reverse("rrapp:personal_quiz"))
        self.assertIn(response.status_code, [200, 302])

    def test_personal_quiz_view_post(self):
        client = Client()
        data = {
            "question1": 1,
            "question2": 1,
            "question3": 1,
            "question4": 1,
            "question5": 1,
            "question6": 1,
            "question7": 1,
            "question8": 1,
        }
        form = QuizForm(data)
        response = client.post(reverse("rrapp:personal_quiz"), data)
        self.assertTrue(form.is_valid())
        self.assertIn(response.status_code, [200, 302])

    def test_personal_quiz_view_post_invalid(self):
        client = Client()
        data = {
            "question1": "In your roommate's bed",
            "question2": 1,
            "question3": 1,
            "question4": 1,
            "question5": 1,
            "question6": 1,
            "question7": 1,
            "question8": 1,
        }
        form = QuizForm(data)
        response = client.post(reverse("rrapp:personal_quiz"), data)
        self.assertFalse(form.is_valid())
        self.assertIn(response.status_code, [200, 302])


class RatingViewTest(ViewsTestCase):
    def test_rating_view_get(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("rrapp:rate_user", kwargs={"ratee_id": self.user.id})
        )
        self.assertIn(response.status_code, [200, 302])
        self.assertTemplateUsed(response, "rrapp/rate_user.html")

    def test_rating_view_post_unpermitted(self):
        self.client.force_login(self.user)
        user2 = User.objects.create_user(
            username="testuser2", password="testpass2", email="testuser2@example.edu"
        )
        response = self.client.post(
            reverse("rrapp:rate_user", kwargs={"ratee_id": user2.id}),
            {
                "pk": user2.id,
                "val": 5.0,
            },
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            Rating.objects.filter(rater=self.user, ratee=user2, rating=5.0).exists()
        )

    def test_rating_view_post_permitted_rating_exists(self):
        self.client.force_login(self.user)
        user2 = User.objects.create_user(
            username="testuser2", password="testpass2", email="testuser2@example.edu"
        )
        DirectMessagePermission.objects.create(
            sender=self.user,
            receiver=user2,
            permission=Permission.ALLOWED,
        )
        Rating.objects.create(rater=self.user, ratee=user2, rating=4.0)
        response = self.client.post(
            reverse("rrapp:rate_user", kwargs={"ratee_id": user2.id}),
            {
                "pk": user2.id,
                "val": 5.0,
            },
        )
        self.assertIn(response.status_code, [200, 302])
        self.assertTrue(
            Rating.objects.filter(rater=self.user, ratee=user2, rating=5.0).exists()
        )
        user = User.objects.get(id=user2.id)
        self.assertTrue(user.rating == 5.0)

    def test_rating_view_post_permitted_rating_unexists(self):
        self.client.force_login(self.user)
        user2 = User.objects.create_user(
            username="testuser2", password="testpass2", email="testuser2@example.edu"
        )
        DirectMessagePermission.objects.create(
            sender=self.user,
            receiver=user2,
            permission=Permission.ALLOWED,
        )
        response = self.client.post(
            reverse("rrapp:rate_user", kwargs={"ratee_id": user2.id}),
            {
                "pk": user2.id,
                "val": 5.0,
            },
        )
        self.assertIn(response.status_code, [200, 302])
        self.assertTrue(
            Rating.objects.filter(rater=self.user, ratee=user2, rating=5.0).exists()
        )
        user = User.objects.get(id=user2.id)
        self.assertTrue(user.rating == 5.0)
