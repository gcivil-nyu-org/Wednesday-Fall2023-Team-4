from django.urls import path

from . import views

app_name = "rrapp"
urlpatterns = [
    # # ex: /rrapp/
    # path('', views.IndexView.as_view(), name='index'),
    # ex: /rrapp/
    path('', views.HomeView.as_view(), name='home'),
    # ex: /rrapp/login
    path('login/', views.LoginView.as_view(), name="login"),
    # ex: /rrapp/logout
    path('logout/', views.LogoutView.as_view(), name="logout"),
    # ex: /rrapp/register
    path('register/', views.RegisterView.as_view(), name="register"),
    # ex: /rrapp/5/listings/1
    path(
        '<int:user_id>/listings/<int:pk>',
        views.ListingDetailView.as_view(),
        name='listing_detail',
    ),
    # ex: /rrapp/5/listings/
    path(
        '<int:user_id>/listings/', views.ListingIndexView.as_view(), name='my_listings'
    ),
    # ex: /rrapp/5/listings/new
    path(
        '<int:user_id>/listings/new', views.ListingNewView.as_view(), name='listing_new'
    ),
    # ex: /rrapp/5/delete/1
    path('<int:user_id>/delete/<int:pk>', views.listing_delete, name='listing_delete'),
    path(
        '<int:user_id>/listings/<int:pk>/modify',
        views.ListingUpdateView.as_view(),
        name='listing_detail_modify',
    ),
    # ex: /rrapp/rentee/5/listings/
    path(
        'rentee/<int:user_id>/listings/',
        views.ListingResultsView.as_view(),
        name='rentee_listings',
    ),
    # ex: /rrapp/rentee/5/listings/1
    path(
        'rentee/<int:user_id>/listings/<int:pk>',
        views.ListingDetailRenteeView.as_view(),
        name='rentee_listing_detail',
    ),
]
