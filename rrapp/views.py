from typing import Any
from django.shortcuts import get_object_or_404, render
from django.db.models import Q

# Create your views here.
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from psycopg2.extras import NumericRange

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import Listing, Renter, Rentee, SavedListing
from .forms import MyUserCreationForm, ListingForm
from django.contrib.auth import get_user_model

User = get_user_model()


class HomeView(generic.View):
    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to
        # access the register page while logged in
        if request.user.is_authenticated:
            return HttpResponseRedirect(
                reverse('rrapp:rentee_listings', args=(request.user.id,))
            )
        # else process dispatch as it otherwise normally would
        return super(HomeView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, 'rrapp/home.html')


class LoginView(generic.View):
    context = {'page': 'login'}

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to
        # access the register page while logged in
        if request.user.is_authenticated:
            # if len(Renter.objects.all()) > 0 and request.user.id in [
            #     i.user.id for i in Renter.objects.all()
            # ]:
            #     login(request, request.user)
            #     return HttpResponseRedirect(
            #         reverse('rrapp:my_listings', args=(request.user.id,))
            #     )
            # else:
            #     login(request, request.user)
            #     return HttpResponseRedirect(
            #         reverse('rrapp:rentee_listings', args=(request.user.id,))
            #     )
            return HttpResponseRedirect(
                reverse('rrapp:rentee_listings', args=(request.user.id,))
            )
        # else process dispatch as it otherwise normally would
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, 'rrapp/login_register.html', self.context)

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
        except Exception:
            messages.error(request, 'User does not exist')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            # if len(Renter.objects.all()) > 0 and user.id in [
            #     i.user.id for i in Renter.objects.all()
            # ]:
            #     login(request, user)
            #     return HttpResponseRedirect(
            #         reverse('rrapp:my_listings', args=(request.user.id,))
            #     )
            # else:
            #     login(request, user)
            #     return HttpResponseRedirect(
            #         reverse('rrapp:rentee_listings', args=(request.user.id,))
            #     )
            login(request, user)
            return HttpResponseRedirect(
                reverse('rrapp:rentee_listings', args=(request.user.id,))
            )
        else:
            messages.error(request, 'Username OR password does not exit')
        return render(request, 'rrapp/login_register.html', self.context)


class LogoutView(generic.View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return render(request, 'rrapp/home.html')


class RegisterView(generic.View):
    initial = {'key': 'value'}

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to
        # access the register page while logged in
        if request.user.is_authenticated:
            return HttpResponseRedirect(
                reverse('rrapp:rentee_listings', args=(request.user.id,))
            )
        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = MyUserCreationForm(initial=self.initial)
        return render(request, 'rrapp/login_register.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if not user.email[-4:] == '.edu':
                messages.error(request, 'Email format is not correct')
                return render(request, 'rrapp/login_register.html', {'form': form})
            user.save()
            user_id = user.id

            type_renter = Renter.objects.create(user=user)
            type_rentee = Rentee.objects.create(user=user)
            type_renter.save()
            type_rentee.save()
            login(request, user)
            return HttpResponseRedirect(
                reverse('rrapp:rentee_listings', args=(user_id,))
            )
        else:
            messages.error(request, 'An error occurred during registration')

        return render(request, 'rrapp/login_register.html', {'form': form})


@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
class ListingDetailView(generic.DetailView):
    model = Listing
    template_name = "rrapp/listing_detail.html"

    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        context_data["user_id"] = self.kwargs["user_id"]
        return context_data


@method_decorator(login_required, name='dispatch')
class ListingDetailRenteeView(generic.DetailView):
    model = Listing
    template_name = "rrapp/rentee_listing_detail.html"

    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        context_data["user_id"] = self.kwargs["user_id"]
        context_data["saved"] = self.check_state(
            self.kwargs["user_id"], self.kwargs["pk"]
        )
        # print("saved: ", context_data["saved"])
        return context_data

    def check_state(self, user_id, listing_id):
        # print(user_id, listing_id)
        if SavedListing.objects.filter(
            rentee_id__user=user_id, saved_listings=listing_id
        ).exists():
            return True
        else:
            return False

    def post(self, request, *args, **kwargs):
        listing_id = self.kwargs['pk']
        user_id = self.kwargs['user_id']
        save_state = self.check_state(user_id, listing_id)
        if save_state:
            SavedListing.objects.filter(
                rentee_id__user=user_id, saved_listings=listing_id
            ).delete()
        else:
            rentee = Rentee.objects.get(user=user_id)
            listing = Listing.objects.get(id=listing_id)
            SavedListing.objects.create(rentee_id=rentee, saved_listings=listing)
        return HttpResponseRedirect(request.path_info)  # redirect to the same page


@method_decorator(login_required, name='dispatch')
class ListingResultsView(generic.ListView):
    template_name = "rrapp/rentee_listings.html"
    context_object_name = "queried_listings_page"

    def get_queryset(self):
        all_listings = Listing.objects.all().order_by('-created_at')
        sort_option = self.request.GET.get('sort', 'created_at')

        # Extract the sorting order (Low to High or High to Low)
        sorting_order = ''  # Default to ascending order
        if sort_option.startswith('-'):
            sort_option = sort_option[1:]
            sorting_order = '-'  # Set to descending order

        # Apply sorting
        if sort_option not in ['monthly_rent', 'number_of_bedrooms', 'number_of_bathrooms']:
            sort_option = 'created_at'
        all_listings = all_listings.order_by(f'{sorting_order}{sort_option}')

        # Apply filters
        filters = Q()

        monthly_rent = self.request.GET.get('monthly_rent')
        if monthly_rent:
            filters &= Q(monthly_rent__lte=monthly_rent)

        number_of_bedrooms = self.request.GET.get('number_of_bedrooms')
        if number_of_bedrooms:
            filters &= Q(number_of_bedrooms__lte=number_of_bedrooms)

        number_of_bathrooms = self.request.GET.get('number_of_bathrooms')
        if number_of_bathrooms:
            filters &= Q(number_of_bathrooms__lte=number_of_bathrooms)

        washer = self.request.GET.get('washer')
        if washer == 'on':
            filters &= Q(washer=True)

        dryer = self.request.GET.get('dryer')
        if dryer == 'on':
            filters &= Q(dryer=True)

        utilities_included = self.request.GET.get('utilities_included')
        if utilities_included == 'on':
            filters &= Q(utilities_included=True)

        furnished = self.request.GET.get('furnished')
        if furnished == 'on':
            filters &= Q(furnished=True)

        dishwasher = self.request.GET.get('dishwasher')
        if dishwasher == 'on':
            filters &= Q(dishwasher=True)

        parking = self.request.GET.get('parking')
        if parking == 'on':
            filters &= Q(parking=True)

        room_type = self.request.GET.get('room_type')
        if room_type:
            filters &= Q(room_type=room_type)

        food_groups_allowed = self.request.GET.get('food_groups_allowed')
        if food_groups_allowed:
            filters &= Q(food_groups_allowed=food_groups_allowed)

        pets_allowed = self.request.GET.get('pets_allowed')
        if pets_allowed:
            filters &= Q(pets_allowed=pets_allowed)

        # Continue filtering for other fields if needed

        # Combine filters
        all_listings = all_listings.filter(filters)

        paginator = Paginator(all_listings, 10)
        page_number = self.request.GET.get("page")
        queried_listings_page = paginator.get_page(page_number)
        return queried_listings_page

    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        context_data["user_id"] = self.kwargs["user_id"]
        return context_data


@method_decorator(login_required, name='dispatch')
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
        'state',
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
    success_url = 'rrapp:listing_detail'

    def get_success_url(self):
        user_id = self.kwargs['user_id']
        listing_id = self.kwargs['pk']
        return reverse('rrapp:listing_detail', args=(user_id, listing_id))


@method_decorator(login_required, name='dispatch')
class ListingNewView(generic.CreateView):
    model = Listing
    success_url = 'rrapp:my_listings'
    form_class = ListingForm
    template_name = "rrapp/listing_new.html"

    def get_success_url(self):
        user_id = self.kwargs['user_id']
        return reverse('rrapp:listing_new', args=(user_id,))

    def get_object(self, queryset=None):
        try:
            return self.request.user
        except Listing.DoesNotExist:
            return Listing.objects.create(user=self.request.user)

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
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
        return HttpResponseRedirect(
            reverse('rrapp:my_listings', args=(kwargs["user_id"],))
        )


@login_required(login_url='login')
def listing_delete(request, user_id, pk):
    # TODO:add the check  if request.user.is_authenticated():
    listing = get_object_or_404(Listing, pk=pk, user_id=user_id)
    listing.delete()
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    return HttpResponseRedirect(reverse('rrapp:my_listings', args=(user_id,)))
