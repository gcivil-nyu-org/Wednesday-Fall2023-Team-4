from typing import Any
from django.shortcuts import get_object_or_404, render

# Create your views here.
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django import forms

from psycopg2.extras import NumericRange

from .models import Listing, User
from .forms import ListingForm


class IndexView(generic.View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Hello, world. You're at the rrapp index.")


class ListingIndexView(generic.ListView):
    template_name = "rrapp/my_listings.html"
    context_object_name = "latest_listings"

    def get_queryset(self):
        """Return the last five published questions."""
        user_id = self.kwargs["user_id"]
        all_listings = Listing.objects.filter(user=user_id).order_by("-created_at")
        paginator = Paginator(all_listings, 10)
        page_number = self.request.GET.get("page")
        latest_listings_page = paginator.get_page(page_number)
        return latest_listings_page

    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        context_data["user_id"] = self.kwargs["user_id"]
        return context_data


class ListingDetailView(generic.DetailView):
    model = Listing
    template_name = "rrapp/listing_detail.html"


class ListingDetailRenteeView(generic.DetailView):
    model = Listing
    template_name = "rrapp/rentee_listing_detail.html"


class ListingResultsView(generic.ListView):
    template_name = "rrapp/rentee_listings.html"
    context_object_name = "queried_listings_page"

    def get_queryset(self):
        """Return the last five published questions."""
        all_listings = Listing.objects.all().order_by('-created_at')
        paginator = Paginator(all_listings, 10)
        page_number = self.request.GET.get("page")
        queried_listings_page = paginator.get_page(page_number)
        return queried_listings_page

    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        context_data["user_id"] = self.kwargs["user_id"]
        return context_data


class ListingUpdateView(generic.UpdateView):
    model = Listing
    template_name = "rrapp/listing_detail_modify.html"
    fields = [
        'status',
        'title',
        'description',
        'monthly_rent',
        'date_available_from',
        'date_available_to',
        'property_type',
        'room_type',
        'address1',
        'address2',
        'zip_code',
        'city',
        'country',
        'washer',
        'dryer',
        'dishwasher',
        'microwave',
        'baking_oven',
        'parking',
        'number_of_bedrooms',
        'number_of_bathrooms',
        'furnished',
        'utilities_included',
        'age_range',
        'smoking_allowed',
        'pets_allowed',
        'food_groups_allowed',
    ]
    # TODO
    success_url = 'rrapp:listing_detail'

    # pass the arguments to the url
    def get_success_url(self):
        user_id = self.kwargs['user_id']
        listing_id = self.kwargs['pk']
        return reverse('rrapp:listing_detail', args=(user_id, listing_id))


class ListingNewView(generic.CreateView):
    
    model = Listing
    success_url = 'rrapp:my_listings'
    form_class = ListingForm
    template_name = "rrapp/listing_new.html"
    

    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        context_data["user_id"] = self.kwargs["user_id"]
        return context_data

    def post(self, request: HttpRequest, *args : str, **kwargs : Any) -> HttpResponse:
        """handle user login post req

        Args:
            request (HttpRequest): http request object

        Returns:
            HttpResponse: redirect or login view with error hints
        """
        form = self.form_class(request.POST)
        u = User.objects.get(pk=self.kwargs['user_id'])
        form_data = self.get_form().data

        if form.is_valid():
            print('valid form', form.data)
        
        listing = Listing.objects.create(
            user=u,
            status=form_data.get('status'),
            title=form_data.get('title'),
            description=form_data.get('description'),
            monthly_rent=form_data.get('monthly_rent'),
            date_available_from=form_data.get('date_available_from'),
            date_available_to=form_data.get('date_available_to'),
            property_type=form_data.get('property_type'),
            room_type=form_data.get('room_type'),
            address1=form_data.get('address1'),
            address2=form_data.get('address2'),
            zip_code=form_data.get('zip_code'),
            city=form_data.get('city'),
            country=form_data.get('country'),
            washer=form_data.get('washer') == 'true',
            dryer=form_data.get('dryer') == 'true',
            dishwasher=form_data.get('dishwasher') == 'true',
            microwave=form_data.get('microwave') == 'true',
            baking_oven=form_data.get('baking_oven') == 'true',
            parking=form_data.get('parking') == 'true',
            number_of_bedrooms=form_data.get('number_of_bedrooms'),
            number_of_bathrooms=form_data.get('number_of_bathrooms'),
            furnished=form_data.get('furnished') == 'true',
            utilities_included=form_data.get('utilities_included') == 'true',
            smoking_allowed=form_data.get('smoking_allowed') == 'true',
            pets_allowed=form_data.get('pets_allowed'),
            food_groups_allowed=form_data.get('food_groups_allowed'),
            age_range=NumericRange(
                int(form_data.get('age_range_0')), int(form_data.get('age_range_1'))
            ),
        )
        listing.save()
        return HttpResponseRedirect(reverse('rrapp:my_listings', args=(kwargs["user_id"],)))



def listing_delete(request, user_id, pk):
    listing = get_object_or_404(Listing, pk=pk, user_id=user_id)
    listing.delete()
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    return HttpResponseRedirect(reverse('rrapp:my_listings', args=(user_id,)))
