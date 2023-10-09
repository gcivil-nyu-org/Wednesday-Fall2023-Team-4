from typing import Any
from django.shortcuts import render, get_object_or_404
from django.template import loader
# Create your views here.
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django import forms

from .models import Listing, User

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

class ListingNewView(generic.UpdateView):
    model = Listing
    template_name = "rrapp/listing_new.html"
    success_url = 'rrapp:listing_new'

    def get_success_url(self):
        user_id = self.kwargs['user_id']
        return reverse('rrapp:listing_new', args=(user_id,))

    def get_object(self, queryset=None):
        try:
            return self.request.user
        except Listing.DoesNotExist:
            return Listing.objects.create(user=self.request.user)

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        u = User.objects.get(pk = self.kwargs['user_id'])
        # l = Listing.objects.create(user=u)
        form_data = self.get_form().data
        print('@@@@@@@@@@@@@ ', form_data)
        # print(self.get_form().data.save())
        # self.get_form().data.save()
        l = Listing.objects.create(user = u, status = form_data.get('status'), title = form_data.get('title'),
                                    description = form_data.get('description'), monthly_rent = form_data.get('monthly_rent'),
                                    date_available_from = form_data.get('date_available_from'), 
                                    date_available_to = form_data.get('date_available_to'), 
                                    property_type = form_data.get('property_type'), room_type = form_data.get('room_type'), 
                                    number_of_bedrooms = form_data.get('number_of_bedrooms'), 
                                    number_of_bathrooms = form_data.get('number_of_bathrooms'), 
                                    furnished = form_data.get('furnished')=='on', 
                                    utilities_included = form_data.get('utilities_included')=='on' )
        l.save()
        return super().post(request, *args, **kwargs)
    
    def get_form_class(self):
        class _Form(forms.ModelForm):
            class Meta:
                model = Listing
                fields = ['status', 'title', 'description', 'monthly_rent', 'date_available_from', 
                          'date_available_to', 'property_type', 'room_type', 'number_of_bedrooms', 
                          'number_of_bathrooms', 'furnished', 'utilities_included']

        return _Form

    def form_valid(self, form):
        self.object = form.save(commit=False)

        self.object.user = self.request.user              
        self.object.save()

        form.save_m2m()

        return super(generic.edit.ModelFormMixin, self).form_valid(form)
    
    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        context_data["user_id"] = self.kwargs["user_id"]
        return context_data

    # @method_decorator(login_required)
    # def dispatch(self, request, *args, **kwargs):
    #     return super(CreateCustomerSubscription, self).dispatch(request, *args, **kwargs)


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

def listing_delete(request, user_id, pk):
    listing = get_object_or_404(Listing, pk=pk, user_id=user_id)
    listing.delete()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
    return HttpResponseRedirect(reverse('rrapp:my_listings', args=(user_id,)))

# def my_listings(request, user_id):
#     latest_listings = Listing.objects.order_by('-created_at')[:10]
#     template = loader.get_template('rrapp/my_listings.html')
#     context = {
#         'latest_listings': latest_listings,
#         'user_id': user_id
#     }
#     return HttpResponse(template.render(context, request))
