from django.urls import path

from . import views

app_name = "rrapp"
urlpatterns = [
    # ex: /rrapp/
    path('', views.IndexView.as_view(), name='index'),
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
]
