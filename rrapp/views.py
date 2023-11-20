from django.shortcuts import get_object_or_404, render
from typing import Any, List
from django.db.models import Q

# Create your views here.
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views import generic

from psycopg2.extras import NumericRange

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.mixins import LoginRequiredMixin

from chat.models import DirectMessagePermission, Permission

from .models import Listing, Renter, Rentee, SavedListing, Photo
from .forms import MyUserCreationForm, ListingForm, UserForm, LoginForm

from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib.messages.views import SuccessMessageMixin

from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token

from django.conf import settings

# from roomierendezvous.mixins import Directions

User = get_user_model()


class HomeView(generic.View):
    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to
        # access the register page while logged in
        if request.user.is_authenticated:
            return HttpResponseRedirect(
                reverse("rrapp:rentee_listings", args=(request.user.id,))
            )
        # else process dispatch as it otherwise normally would
        return super(HomeView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, "rrapp/home.html")


class LoginView(generic.View):
    context = {"page": "login"}

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to
        # access the register page while logged in
        if request.user.is_authenticated:
            return HttpResponseRedirect(
                reverse("rrapp:rentee_listings", args=(request.user.id,))
            )
        # else process dispatch as it otherwise normally would
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = LoginForm()
        self.context["form"] = form
        return render(request, "rrapp/login_register.html", self.context)

    def post(self, request, *args, **kwargs):
        loginForm = LoginForm(request.POST)
        if loginForm.is_valid():
            email = loginForm.cleaned_data.get("email")
            password = loginForm.cleaned_data.get("password")
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(
                    reverse("rrapp:rentee_listings", args=(request.user.id,))
                )
            else:
                messages.error(request, "Username OR password does not exist")
        else:
            self.context["form"] = loginForm
        return render(request, "rrapp/login_register.html", self.context)


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'rrapp/password_reset.html'
    email_template_name = 'rrapp/password_reset_email.html'
    subject_template_name = 'rrapp/password_reset_subject.txt'
    success_url = reverse_lazy('rrapp:password_reset_done')


class ConfirmPasswordResetView(PasswordResetConfirmView):
    success_url = reverse_lazy('rrapp:password_reset_complete')


class LogoutView(generic.View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return render(request, "rrapp/home.html")


class RegisterView(generic.View):
    initial = {"key": "value"}

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to
        # access the register page while logged in
        if request.user.is_authenticated:
            return HttpResponseRedirect(
                reverse("rrapp:rentee_listings", args=(request.user.id,))
            )
        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = MyUserCreationForm(initial=self.initial)
        return render(request, "rrapp/login_register.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            user_id = user.id

            type_renter = Renter.objects.create(user=user)
            type_rentee = Rentee.objects.create(user=user)
            type_renter.save()
            type_rentee.save()
            login(request, user)
            return HttpResponseRedirect(
                reverse("rrapp:rentee_listings", args=(user_id,))
            )

        return render(request, "rrapp/login_register.html", {"form": form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_verified = True
        user.save()
        # login(request, user)
        # return redirect('home')
        messages.success(
            request,
            "Thank you for your email confirmation. Your email is now activated!",
            extra_tags='alert alert-success',
        )
    else:
        messages.error(
            request, "Activation link is invalid!", extra_tags='alert alert-danger'
        )

    # return redirect('rrapp:home')
    return HttpResponseRedirect(reverse("rrapp:profile", args=(uid,)))


@login_required(login_url='login')
def activateEmail(request):
    mail_subject = "Activate your user account."
    message = render_to_string(
        "rrapp/template_activate_account.html",
        {
            'user': request.user.username,
            'domain': get_current_site(request).domain,
            'uid': urlsafe_base64_encode(force_bytes(request.user.pk)),
            'token': account_activation_token.make_token(request.user),
            "protocol": 'https' if request.is_secure() else 'http',
        },
    )
    email = EmailMessage(mail_subject, message, to=[request.user.email])
    if email.send():
        # return HttpResponse(f'Dear {request.user}, please go to your email \
        #     {request.user.email} inbox and click on \
        #         received activation link to confirm and \
        #         complete the registration. Note: Check your spam folder.')
        messages.success(
            request,
            f'Dear {request.user}, please go to your email \
            {request.user.email} inbox and click on \
                received activation link to confirm and \
                complete the registration. Note: Check your spam folder.',
            extra_tags='alert alert-primary',
        )
        # return render(request, 'rrapp/home.html')
        # return redirect('rrapp:home')
        return HttpResponseRedirect(reverse("rrapp:profile", args=(request.user.id,)))
    else:
        messages.error(
            request,
            f'Problem sending email to {request.user.email}, \
            check if you typed it correctly.',
            extra_tags='alert alert-danger',
        )
        # return render(request, 'rrapp/home.html')
        # return redirect('rrapp:home')
        return HttpResponseRedirect(reverse("rrapp:profile", args=(request.user.id,)))


@method_decorator(login_required, name="dispatch")
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
        user_id = self.kwargs["user_id"]
        context_data["user_id"] = user_id
        context_data["user"] = User.objects.get(id=user_id)
        context_data["path"] = self.request.path_info.__contains__("renter")
        return context_data


@method_decorator(login_required, name="dispatch")
class ShortListView(generic.ListView):
    template_name = "rrapp/shortListing.html"
    context_object_name = "latest_listings"

    def get_queryset(self):
        """Return the last five published questions."""
        user_id = self.kwargs["user_id"]
        # shortlistings = Listing.objects.filter(user=user_id).order_by("-created_at")
        shortlistings = SavedListing.objects.filter(rentee_id__user=user_id).order_by(
            "-saved_listings__created_at"
        )
        paginator = Paginator(shortlistings, 10)
        page_number = self.request.GET.get("page")
        latest_listings_page = paginator.get_page(page_number)
        return latest_listings_page

    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        user_id = self.kwargs["user_id"]
        context_data["user_id"] = user_id
        context_data["user"] = User.objects.get(id=user_id)
        context_data["path"] = self.request.path_info.__contains__("renter")
        return context_data


@method_decorator(login_required, name="dispatch")
class ListingDetailView(generic.DetailView):
    model = Listing
    template_name = "rrapp/listing_detail.html"

    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        user_id = self.kwargs["user_id"]
        context_data["user_id"] = user_id
        context_data["user"] = User.objects.get(id=user_id)
        context_data["path"] = self.request.path_info.__contains__("renter")
        context_data["photos"] = Photo.objects.filter(listing=self.kwargs["pk"])
        return context_data


@method_decorator(login_required, name="dispatch")
class ListingDetailRenteeView(generic.DetailView):
    model = Listing
    template_name = "rrapp/rentee_listing_detail.html"

    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        user_id = self.kwargs["user_id"]
        context_data["user_id"] = user_id
        context_data["user"] = User.objects.get(id=user_id)
        context_data["path"] = self.request.path_info.__contains__("renter")
        context_data["saved"] = self.check_state(
            self.kwargs["user_id"], self.kwargs["pk"]
        )
        context_data["cur_permission"] = self.cur_permission(
            self.kwargs["user_id"], self.kwargs["pk"]
        )
        context_data["photos"] = Photo.objects.filter(listing=self.kwargs["pk"])

        return context_data

    def check_state(self, user_id, listing_id):
        # print(user_id, listing_id)
        if SavedListing.objects.filter(
            rentee_id__user=user_id, saved_listings=listing_id
        ).exists():
            return True
        else:
            return False

    def cur_permission(self, user_id, listing_id):
        # print(user_id, listing_id)
        listing = Listing.objects.get(id=listing_id)
        cur_user = User.objects.get(id=user_id)
        try:
            p = list(
                DirectMessagePermission.objects.filter(
                    sender=cur_user.username, receiver=listing.user.username
                )
            )

            p_equivalent = list(
                DirectMessagePermission.objects.filter(
                    receiver=cur_user.username, sender=listing.user.username
                )
            )
        except DirectMessagePermission.DoesNotExist:
            p = None

        if len(p) > 0:
            print(p[0].permission)
            return p[0].permission
        else:
            if len(p_equivalent) > 0:
                return p_equivalent[0].permission
            return None

    def post(self, request, *args, **kwargs):
        print('RRAPP :', request.POST, args, kwargs)
        listing_id = self.kwargs["pk"]
        user_id = self.kwargs["user_id"]
        save_state = self.check_state(user_id, listing_id)
        if "shortlist" in request.POST:
            if save_state:
                SavedListing.objects.filter(
                    rentee_id__user=user_id, saved_listings=listing_id
                ).delete()
            else:
                rentee = Rentee.objects.get(user=user_id)
                listing = Listing.objects.get(id=listing_id)
                SavedListing.objects.create(rentee_id=rentee, saved_listings=listing)

        if "connection_request" in request.POST:
            listing = Listing.objects.get(id=listing_id)
            cur_user = User.objects.get(id=user_id)
            try:
                p = list(
                    DirectMessagePermission.objects.filter(
                        sender=cur_user.username, receiver=listing.user.username
                    )
                )
            except DirectMessagePermission.DoesNotExist:
                p = None

            if len(p) > 0:
                print("permission already exists", p)
            else:
                # create DirectMessagePermission object in db
                print("creating permission")
                DirectMessagePermission.objects.create(
                    sender=cur_user.username,
                    receiver=listing.user.username,
                    permission=Permission.REQUESTED,
                )

        return HttpResponseRedirect(request.path_info)  # redirect to the same page


@method_decorator(login_required, name="dispatch")
class ListingResultsView(generic.ListView):
    template_name = "rrapp/rentee_listings.html"
    context_object_name = "queried_listings_page"

    def get_queryset(self):
        all_listings = Listing.objects.all().order_by("-created_at")
        sort_option = self.request.GET.get("sort", "created_at")

        # Extract the sorting order (Low to High or High to Low)
        sorting_order = ""  # Default to ascending order
        if sort_option.startswith("-"):
            sort_option = sort_option[1:]
            sorting_order = "-"  # Set to descending order

        # Apply sorting
        if sort_option not in [
            "monthly_rent",
            "number_of_bedrooms",
            "number_of_bathrooms",
        ]:
            sort_option = "created_at"
        all_listings = all_listings.order_by(f"{sorting_order}{sort_option}")

        # Apply filters
        filters = Q()

        monthly_rent = self.request.GET.get("monthly_rent")
        if monthly_rent:
            filters &= Q(monthly_rent__lte=monthly_rent)

        number_of_bedrooms = self.request.GET.get("number_of_bedrooms")
        if number_of_bedrooms:
            filters &= Q(number_of_bedrooms__lte=number_of_bedrooms)

        number_of_bathrooms = self.request.GET.get("number_of_bathrooms")
        if number_of_bathrooms:
            filters &= Q(number_of_bathrooms__lte=number_of_bathrooms)

        washer = self.request.GET.get("washer")
        if washer == "on":
            filters &= Q(washer=True)

        dryer = self.request.GET.get("dryer")
        if dryer == "on":
            filters &= Q(dryer=True)

        utilities_included = self.request.GET.get("utilities_included")
        if utilities_included == "on":
            filters &= Q(utilities_included=True)

        furnished = self.request.GET.get("furnished")
        if furnished == "on":
            filters &= Q(furnished=True)

        dishwasher = self.request.GET.get("dishwasher")
        if dishwasher == "on":
            filters &= Q(dishwasher=True)

        parking = self.request.GET.get("parking")
        if parking == "on":
            filters &= Q(parking=True)

        room_type = self.request.GET.get("room_type")
        if room_type:
            filters &= Q(room_type=room_type)

        food_groups_allowed = self.request.GET.get("food_groups_allowed")
        if food_groups_allowed:
            filters &= Q(food_groups_allowed=food_groups_allowed)

        pets_allowed = self.request.GET.get("pets_allowed")
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
        user_id = self.kwargs["user_id"]
        context_data["user_id"] = user_id
        context_data["user"] = User.objects.get(id=user_id)
        context_data["path"] = self.request.path_info.__contains__("renter")
        return context_data


@method_decorator(login_required, name="dispatch")
class ListingUpdateView(generic.UpdateView):
    model = Listing
    template_name = "rrapp/listing_detail_modify.html"
    form_class = ListingForm
    success_url = "rrapp:listing_detail"

    def get_success_url(self):
        user_id = self.kwargs["user_id"]
        listing_id = self.kwargs["pk"]
        return reverse("rrapp:listing_detail", args=(user_id, listing_id))

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return Listing.objects.get(id=self.kwargs["pk"])

    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        context_data["user_id"] = self.kwargs["user_id"]
        context_data["listing_id"] = self.kwargs["pk"]
        context_data["list_title"] = Listing.objects.get(id=self.kwargs["pk"]).title
        context_data["user"] = User.objects.get(id=self.kwargs["user_id"])
        context_data["path"] = self.request.path_info.__contains__("renter")
        context_data['google_api_key'] = settings.GOOGLE_API_KEY
        context_data['base_country'] = settings.BASE_COUNTRY
        return context_data

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            listing = form.save()
            existing_photos_pks = request.POST.getlist('existing_photos')
            Photo.objects.filter(listing=listing).exclude(
                pk__in=existing_photos_pks
            ).delete()
            listing.save()
            for file in request.FILES.getlist('add_photos'):
                Photo.objects.create(image=file, listing=listing)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


@method_decorator(login_required, name="dispatch")
class ListingNewView(generic.CreateView):
    model = Listing
    template_name = "rrapp/listing_new.html"
    form_class = ListingForm
    success_url = "rrapp:my_listings"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        user_id = self.kwargs["user_id"]
        return reverse("rrapp:listing_new", args=(user_id,))

    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        context_data["user_id"] = self.kwargs["user_id"]
        context_data["user"] = User.objects.get(id=self.kwargs["user_id"])
        context_data["path"] = self.request.path_info.__contains__("renter")
        context_data['google_api_key'] = settings.GOOGLE_API_KEY
        context_data['base_country'] = settings.BASE_COUNTRY

        return context_data

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        """handle user login post req

        Args:
            request (HttpRequest): http request object

        Returns:
            HttpResponse: redirect or login view with error hints
        """
        self.object = self.get_object()
        form = self.get_form()
        u = User.objects.get(pk=self.kwargs["user_id"])

        # form = MyUserCreationForm(request.POST)
        # print(request.is_ajax())
        if form.is_valid():
            form_data = form.cleaned_data

            listing = Listing.objects.create(
                user=u,
                status=form_data.get("status"),
                title=form_data.get("title"),
                description=form_data.get("description"),
                monthly_rent=form_data.get("monthly_rent"),
                date_available_from=form_data.get("date_available_from"),
                date_available_to=form_data.get("date_available_to"),
                property_type=form_data.get("property_type"),
                room_type=form_data.get("room_type"),
                address1=form_data.get("address1"),
                address2=form_data.get("address2"),
                zip_code=form_data.get("zip_code"),
                city=form_data.get("city"),
                country=form_data.get("country"),
                washer=form_data.get("washer") == "true",
                dryer=form_data.get("dryer") == "true",
                dishwasher=form_data.get("dishwasher") == "true",
                microwave=form_data.get("microwave") == "true",
                baking_oven=form_data.get("baking_oven") == "true",
                parking=form_data.get("parking") == "true",
                number_of_bedrooms=form_data.get("number_of_bedrooms"),
                number_of_bathrooms=form_data.get("number_of_bathrooms"),
                furnished=form_data.get("furnished") == "true",
                utilities_included=form_data.get("utilities_included") == "true",
                smoking_allowed=form_data.get("smoking_allowed") == "true",
                pets_allowed=form_data.get("pets_allowed"),
                food_groups_allowed=form_data.get("food_groups_allowed"),
                age_range=NumericRange(
                    int(form_data.get("age_range").lower),
                    int(form_data.get("age_range").upper),
                ),
            )
            listing.save()
            print(listing)
            for file in request.FILES.getlist('add_photos'):
                Photo.objects.create(image=file, listing=listing)
            return HttpResponseRedirect(
                reverse("rrapp:my_listings", args=(kwargs["user_id"],))
            )
        else:
            return self.form_invalid(form)


@method_decorator(login_required, name='dispatch')
class ProfileView(generic.UpdateView):
    model = User
    template_name = "rrapp/profile.html"
    form_class = UserForm
    success_url = 'rrapp:rentee_listings'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        # return self.request.user
        return User.objects.get(id=self.kwargs["pk"])

    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        context_data["user_id"] = self.kwargs["pk"]
        context_data["user"] = User.objects.get(id=self.kwargs["pk"])
        context_data["path"] = self.request.path_info.__contains__("renter")
        return context_data

    def get_success_url(self):
        user_id = self.kwargs['pk']
        return reverse('rrapp:rentee_listings', args=(user_id,))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


@method_decorator(login_required, name='dispatch')
class PublicProfileView(generic.DetailView):
    model = User
    template_name = "rrapp/public_profile.html"
    fields = [
        'username',
        'first_name',
        'last_name',
        'bio',
        'smokes',
        'pets',
        'food_group',
    ]
    # success_url = 'rrapp:rentee_listings'

    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        context_data["user_id"] = self.kwargs["pk"]
        context_data["user"] = User.objects.get(id=self.kwargs["pk"])
        context_data["path"] = self.request.path_info.__contains__("renter")
        return context_data

    def get_success_url(self):
        user_id = self.kwargs['pk']
        return reverse('rrapp:rentee_listings', args=(user_id,))


@login_required(login_url='login')
def listing_delete(request, user_id, pk):
    # TODO:add the check  if request.user.is_authenticated():
    listing = get_object_or_404(Listing, pk=pk, user_id=user_id)

    if request.method == 'POST':
        listing.delete()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('rrapp:my_listings', args=(user_id,)))
    return render(
        request, 'rrapp/confirm_delete_listing.html', {"user_id": user_id, "pk": pk}
    )


@login_required(login_url='login')
def deleteAccount(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        user.delete()
        logout(request)
        return HttpResponseRedirect(reverse('rrapp:home'))
    return render(request, 'rrapp/confirm_delete_user.html', {"user_id": user_id})


class UsersListView(LoginRequiredMixin, generic.ListView):
    http_method_names = [
        'get',
    ]

    def get_queryset(self):
        return User.objects.all().exclude(id=self.request.user.id)

    def render_to_response(self, context, **response_kwargs):
        users: List[AbstractBaseUser] = context['object_list']

        data = [{"username": usr.get_username(), "pk": str(usr.pk)} for usr in users]
        return JsonResponse(data, safe=False, **response_kwargs)


def route(request):
    context = {
        "google_api_key": settings.GOOGLE_API_KEY,
        "base_country": settings.BASE_COUNTRY,
    }
    return render(request, 'main/route.html', context)


'''
Basic view for displaying a map 
'''


def map(request):
    lat_a = request.GET.get("lat_a", None)
    long_a = request.GET.get("long_a", None)
    lat_b = request.GET.get("lat_b", None)
    long_b = request.GET.get("long_b", None)
    lat_c = request.GET.get("lat_c", None)
    long_c = request.GET.get("long_c", None)
    lat_d = request.GET.get("lat_d", None)
    long_d = request.GET.get("long_d", None)

    # only call API if all 4 addresses are added
    if lat_a and lat_b and lat_c and lat_d:
        directions = Directions(
            lat_a=lat_a,
            long_a=long_a,
            lat_b=lat_b,
            long_b=long_b,
            lat_c=lat_c,
            long_c=long_c,
            lat_d=lat_d,
            long_d=long_d,
        )
    else:
        return redirect(reverse('main:route'))

    context = {
        "google_api_key": settings.GOOGLE_API_KEY,
        "base_country": settings.BASE_COUNTRY,
        "lat_a": lat_a,
        "long_a": long_a,
        "lat_b": lat_b,
        "long_b": long_b,
        "lat_c": lat_c,
        "long_c": long_c,
        "lat_d": lat_d,
        "long_d": long_d,
        "origin": f'{lat_a}, {long_a}',
        "destination": f'{lat_b}, {long_b}',
        "directions": directions,
    }
    return render(request, 'main/map.html', context)
