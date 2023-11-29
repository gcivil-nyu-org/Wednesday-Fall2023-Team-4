from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = "rrapp"
urlpatterns = [
    path("healthcheck", views.healthcheck, name="healthcheck"),
    # ex: /rrapp/
    path("", views.HomeView.as_view(), name="home"),
    path('login/', views.LoginView.as_view(), name="login"),
    path(
        'reset_password/',
        views.ResetPasswordView.as_view(template_name="rrapp/password_reset.html"),
        name='reset_password',
    ),
    path(
        'reset_password_sent/',
        auth_views.PasswordResetDoneView.as_view(
            template_name="rrapp/password_reset_sent.html"
        ),
        name='password_reset_done',
    ),
    path(
        'reset_password/<uidb64>/<token>/',
        views.ConfirmPasswordResetView.as_view(
            template_name='rrapp/password_reset_confirm.html'
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset_password_complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='rrapp/password_reset_complete.html'
        ),
        name='password_reset_complete',
    ),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path('register/', views.RegisterView.as_view(), name="register"),
    path(
        'verification_check/<uidb64>/<token>',
        views.verificationCheck,
        name='verification_check',
    ),
    path('verify_email', views.verifyEmail, name='verify_email'),
    # ex: /rrapp/5/listings/1
    path(
        "renter/listings/<int:pk>/",
        views.ListingDetailView.as_view(),
        name="listing_detail",
    ),
    # ex: /rrapp/5/listings/
    path(
        "renter/listings/",
        views.ListingIndexView.as_view(),
        name="my_listings",
    ),
    # ex: /rrapp/5/listings/new
    path(
        "renter/listings/new",
        views.ListingNewView.as_view(),
        name="listing_new",
    ),
    # ex: /rrapp/5/delete/1
    path(
        "renter/listings/<int:pk>/delete",
        views.listing_delete,
        name="listing_delete",
    ),
    path(
        "renter/listings/<int:pk>/modify",
        views.ListingUpdateView.as_view(),
        name="listing_detail_modify",
    ),
    # ex: /rrapp/rentee/5/listings/
    path(
        "rentee/listings/",
        views.ListingResultsView.as_view(),
        name="rentee_listings",
    ),
    # ex: /rrapp/rentee/5/listings/1
    path(
        "rentee/listings/<int:pk>",
        views.ListingDetailRenteeView.as_view(),
        name="rentee_listing_detail",
    ),
    # ex: /rrapp/user/profile/1
    path(
        'user/profile',
        views.ProfileView.as_view(),
        name='profile',
    ),
    # ex: /rrapp/user/profile/1/delete
    path(
        'user/profile/delete',
        views.deleteAccount,
        name='deleteAccount',
    ),
    # ex: /rrapp/rentee/2/shortlist
    path(
        'rentee/shortlist/',
        views.ShortListView.as_view(),
        name='shortlist',
    ),
    # ex: /rrapp/user/public_profile/2
    path(
        'user/public_profile/<int:pk>',
        views.PublicProfileView.as_view(),
        name='public_profile',
    ),
    # ex: /rrapp/user/rating/2
    path(
        'user/rating/<int:ratee_id>',
        views.RatingView.as_view(),
        name='rate_user',
    ),
    path(
        'user/quiz',
        views.PersonalQuizView.as_view(),
        name='personal_quiz',
    ),
]
