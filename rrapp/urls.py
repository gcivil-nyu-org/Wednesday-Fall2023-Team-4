from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = "rrapp"
urlpatterns = [
    # # ex: /rrapp/
    # path('', views.IndexView.as_view(), name='index'),
    # ex: /rrapp/
    path("", views.HomeView.as_view(), name="home"),
    # ex: /rrapp/login
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
        'reset/<uidb64>/<token>/',
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
    # ex: /rrapp/logout
    path("logout/", views.LogoutView.as_view(), name="logout"),
    # ex: /rrapp/register
    path('register/', views.RegisterView.as_view(), name="register"),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('activate_email', views.activateEmail, name='activate_email'),
    # ex: /rrapp/5/listings/1
    path(
        "renter/<int:user_id>/listings/<int:pk>/",
        views.ListingDetailView.as_view(),
        name="listing_detail",
    ),
    # ex: /rrapp/5/listings/
    path(
        "renter/<int:user_id>/listings/",
        views.ListingIndexView.as_view(),
        name="my_listings",
    ),
    # ex: /rrapp/5/listings/new
    path(
        "renter/<int:user_id>/listings/new",
        views.ListingNewView.as_view(),
        name="listing_new",
    ),
    # ex: /rrapp/5/delete/1
    path(
        "renter/<int:user_id>/delete/<int:pk>",
        views.listing_delete,
        name="listing_delete",
    ),
    path(
        "renter/<int:user_id>/listings/<int:pk>/modify",
        views.ListingUpdateView.as_view(),
        name="listing_detail_modify",
    ),
    # ex: /rrapp/rentee/5/listings/
    path(
        "rentee/<int:user_id>/listings/",
        views.ListingResultsView.as_view(),
        name="rentee_listings",
    ),
    # ex: /rrapp/rentee/5/listings/1
    path(
        "rentee/<int:user_id>/listings/<int:pk>",
        views.ListingDetailRenteeView.as_view(),
        name="rentee_listing_detail",
    ),
    # ex: /rrapp/rentee/5/listings/1/rent
    path(
        '<int:pk>/profile',
        views.ProfileView.as_view(),
        name='profile',
    ),
]
