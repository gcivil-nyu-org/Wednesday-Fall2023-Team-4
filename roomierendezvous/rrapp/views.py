from typing import Any
from django.shortcuts import render, get_object_or_404
from django.template import loader
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from .models import Listing

class IndexView(generic.View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Hello, world. You're at the rrapp index.")

class ListingIndexView(generic.ListView):
    template_name = "rrapp/my_listings.html"
    context_object_name = "latest_listings"

    def get_queryset(self):
        """Return the last five published questions."""
        user_id = self.kwargs["user_id"]
        return Listing.objects.filter(user = user_id).order_by("-created_at")[:10]

    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        context_data["user_id"] = self.kwargs["user_id"]
        return context_data

class ListingDetailView(generic.DetailView):
    model = Listing
    template_name = "rrapp/listing_detail.html"


# def index(request):
#     return HttpResponse("Hello, world. You're at the rrapp index.")

# def listing_detail(request, user_id, listing_id):
#     listing = get_object_or_404(Listing, pk=listing_id, user_id=user_id)
#     template = loader.get_template('rrapp/listing_detail.html')
#     context = {
#         'listing': listing,
#         'user_id': user_id
#     }
#     return HttpResponse(template.render(context, request))

# def listing_update(request, user_id, listing_id):
#     listing = get_object_or_404(Listing, pk=listing_id, user_id=user_id)
#     print(request.POST)
#     try:
#         keys = ['status', 'title', 'description', 'monthly_rent', 'date_available_from', 
#                 'date_available_to', 'property_type', 'room_type', 'number_of_bedrooms', 
#                 'number_of_bathrooms', 'furnished', 'utilities_included']
        
#         for key in keys:
#             if key in request.POST:
#                 new_value = request.POST[key]
#                 listing.key = new_value
#     except (KeyError, Listing.DoesNotExist):
#         # Redisplay the question voting form.
#         return render(request, 'rrapp/listing_detail.html', {
#             'listing': listing,
#             'user_id': user_id,
#             'error_message': 'You did not make any changes.'
#         })
#     else:
#         print('saving')
#         listing.save()
#         # Always return an HttpResponseRedirect after successfully dealing
#         # with POST data. This prevents data from being posted twice if a
#         # user hits the Back button.
#         return HttpResponseRedirect(reverse('rrapp:listing_detail', args=(user_id,listing.id)))


# def my_listings(request, user_id):
#     latest_listings = Listing.objects.order_by('-created_at')[:10]
#     template = loader.get_template('rrapp/my_listings.html')
#     context = {
#         'latest_listings': latest_listings,
#         'user_id': user_id
#     }
#     return HttpResponse(template.render(context, request))
