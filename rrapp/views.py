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

from .models import Listing, Renter, Rentee, SavedListing, Photo, Rating, Quiz
from .forms import MyUserCreationForm, ListingForm, UserForm, LoginForm, QuizForm

from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib.messages.views import SuccessMessageMixin

from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token

from chat.utils import get_pending_connections_count
from django.conf import settings

from django.core.exceptions import PermissionDenied

User = get_user_model()


def healthcheck(request):
    return HttpResponse(status=200)


class HomeView(generic.View):
    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to
        # access the register page while logged in
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("rrapp:rentee_listings"))
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
            return HttpResponseRedirect(reverse("rrapp:rentee_listings"))
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
                return HttpResponseRedirect(reverse("rrapp:rentee_listings"))
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
            return HttpResponseRedirect(reverse("rrapp:rentee_listings"))
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

            type_renter = Renter.objects.create(user=user)
            type_rentee = Rentee.objects.create(user=user)
            type_renter.save()
            type_rentee.save()
            login(request, user)
            return HttpResponseRedirect(reverse("rrapp:rentee_listings"))

        return render(request, "rrapp/login_register.html", {"form": form})


def verificationCheck(request, uidb64, token):
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
            "Thank you for confirming. Your email is now verified!",
            extra_tags='alert alert-success',
        )
    else:
        messages.error(
            request, "Verification link is invalid!", extra_tags='alert alert-danger'
        )

    # return redirect('rrapp:home')
    return HttpResponseRedirect(reverse("rrapp:profile"))


@login_required
def verifyEmail(request):
    mail_subject = "Activate your user account."
    message = render_to_string(
        "rrapp/template_verify_account.html",
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
            f'Hi {request.user}, please check your email \
            {request.user.email}\'s inbox and click on \
                received activation link to confirm and \
                complete the verification. Don\'t forget to check your spam folder.',
            extra_tags='alert alert-primary',
        )
        # return render(request, 'rrapp/home.html')
        # return redirect('rrapp:home')
        return HttpResponseRedirect(reverse("rrapp:profile"))
    else:
        messages.error(
            request,
            f'Problem sending email to {request.user.email}, \
            please check if you typed it correctly.',
            extra_tags='alert alert-danger',
        )
        # return render(request, 'rrapp/home.html')
        # return redirect('rrapp:home')
        return HttpResponseRedirect(reverse("rrapp:profile"))


@method_decorator(login_required, name="dispatch")
class ListingIndexView(generic.ListView):
    template_name = "rrapp/my_listings.html"
    context_object_name = "latest_listings"

    def get_queryset(self):
        """Return the last five published questions."""
        user_id = self.request.user.id
        all_listings = Listing.objects.filter(user=user_id).order_by("-created_at")
        paginator = Paginator(all_listings, 10)
        page_number = self.request.GET.get("page")
        latest_listings_page = paginator.get_page(page_number)
        return latest_listings_page

    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        context_data["user_id"] = user_id
        context_data["user"] = self.request.user
        context_data["path"] = self.request.path_info.__contains__("renter")
        context_data["inbox"] = get_inbox_count(User.objects.get(id=user_id).username)
        return context_data


@method_decorator(login_required, name="dispatch")
class ShortListView(generic.ListView):
    template_name = "rrapp/shortListing.html"
    context_object_name = "latest_listings"

    def get_queryset(self):
        """Return the last five published questions."""
        user_id = self.request.user.id
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
        user_id = self.request.user.id
        context_data["user_id"] = user_id
        context_data["user"] = self.request.user
        context_data["path"] = self.request.path_info.__contains__("renter")
        context_data["inbox"] = get_inbox_count(User.objects.get(id=user_id).username)
        return context_data


@method_decorator(login_required, name="dispatch")
class ListingDetailView(generic.DetailView):
    model = Listing
    template_name = "rrapp/listing_detail.html"

    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        context_data["user_id"] = user_id
        context_data["user"] = self.request.user
        context_data["path"] = self.request.path_info.__contains__("renter")
        context_data["photos"] = Photo.objects.filter(listing=self.kwargs["pk"])
        context_data["inbox"] = get_inbox_count(User.objects.get(id=user_id).username)
        return context_data


@method_decorator(login_required, name="dispatch")
class ListingDetailRenteeView(generic.DetailView):
    model = Listing
    template_name = "rrapp/rentee_listing_detail.html"

    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        context_data["user_id"] = user_id
        context_data["user"] = User.objects.get(id=user_id)
        context_data["path"] = self.request.path_info.__contains__("renter")
        context_data["saved"] = self.check_state(user_id, self.kwargs["pk"])
        context_data["cur_permission"] = self.cur_permission(user_id, self.kwargs["pk"])
        context_data["photos"] = Photo.objects.filter(listing=self.kwargs["pk"])
        context_data["inbox"] = get_inbox_count(User.objects.get(id=user_id).username)
        context_data["quizState"] = check_quiz_state(user_id)
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
                    sender=cur_user, receiver=listing.user
                )
            )

            p_equivalent = list(
                DirectMessagePermission.objects.filter(
                    receiver=cur_user, sender=listing.user
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
        listing_id = self.kwargs["pk"]
        user_id = request.user.id
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
                        sender=cur_user, receiver=listing.user
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
                    sender=cur_user,
                    receiver=listing.user,
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

        try:
            monthly_rent_min = int(self.request.GET.get("monthly_rent_min", "0"))
            monthly_rent_max = int(self.request.GET.get("monthly_rent_max", "10000"))
            filters &= Q(
                monthly_rent__gte=monthly_rent_min, monthly_rent__lte=monthly_rent_max
            )
        except ValueError:
            # Handle error or ignore
            pass

        # Convert and apply Number of Bedrooms filter
        try:
            number_of_bedrooms_min = int(
                self.request.GET.get("number_of_bedrooms_min", "0")
            )
            number_of_bedrooms_max = int(
                self.request.GET.get("number_of_bedrooms_max", "10")
            )
            filters &= Q(
                number_of_bedrooms__gte=number_of_bedrooms_min,
                number_of_bedrooms__lte=number_of_bedrooms_max,
            )
        except ValueError:
            # Handle error or ignore
            pass

        # Convert and apply Number of Bathrooms filter
        try:
            number_of_bathrooms_min = int(
                self.request.GET.get("number_of_bathrooms_min", "0")
            )
            number_of_bathrooms_max = int(
                self.request.GET.get("number_of_bathrooms_max", "10")
            )
            filters &= Q(
                number_of_bathrooms__gte=number_of_bathrooms_min,
                number_of_bathrooms__lte=number_of_bathrooms_max,
            )
        except ValueError:
            # Handle error or ignore
            pass

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
        user_id = self.request.user.id
        context_data["user_id"] = user_id
        context_data["user"] = self.request.user
        context_data["path"] = self.request.path_info.__contains__("renter")
        context_data["inbox"] = get_inbox_count(self.request.user.username)
        return context_data


@method_decorator(login_required, name="dispatch")
class ListingUpdateView(generic.UpdateView):
    model = Listing
    template_name = "rrapp/listing_detail_modify.html"
    form_class = ListingForm
    success_url = "rrapp:listing_detail"

    def get_success_url(self):
        listing_id = self.kwargs["pk"]
        return reverse("rrapp:listing_detail", args=(listing_id,))

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return Listing.objects.get(id=self.kwargs["pk"])

    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        context_data["user_id"] = self.request.user.id
        context_data["listing_id"] = self.kwargs["pk"]
        context_data["list_title"] = Listing.objects.get(id=self.kwargs["pk"]).title
        context_data["user"] = self.request.user
        context_data["path"] = self.request.path_info.__contains__("renter")
        context_data["inbox"] = get_inbox_count(self.request.user.username)
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
        return reverse("rrapp:listing_new")

    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        context_data["user_id"] = self.request.user.id
        context_data["user"] = self.request.user
        context_data["path"] = self.request.path_info.__contains__("renter")
        context_data["inbox"] = get_inbox_count(self.request.user.username)
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

        if form.is_valid():
            form_data = form.cleaned_data

            listing = Listing.objects.create(
                user=request.user,
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
            for file in request.FILES.getlist('add_photos'):
                Photo.objects.create(image=file, listing=listing)
            return HttpResponseRedirect(reverse("rrapp:my_listings"))
        else:
            return self.form_invalid(form)


@method_decorator(login_required, name='dispatch')
class ProfileView(generic.UpdateView):
    model = User
    template_name = "rrapp/profile.html"
    form_class = UserForm
    success_url = 'rrapp:profile'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        context_data["user_id"] = self.request.user.id
        context_data["user"] = self.request.user
        context_data["path"] = self.request.path_info.__contains__("renter")
        context_data["inbox"] = get_inbox_count(self.request.user.username)
        return context_data

    def get_success_url(self):
        return reverse('rrapp:profile')

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
        'rating',
    ]

    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        context_data["user_id"] = self.request.user.id
        context_data["user"] = self.request.user
        context_data["tarUser"] = User.objects.get(id=self.kwargs["pk"])
        context_data["path"] = self.request.path_info.__contains__("renter")
        context_data["inbox"] = get_inbox_count(self.request.user.username)
        if self.check_rating_exists(self.request.user, context_data["tarUser"]):
            context_data["rated"] = True
            context_data["rating"] = Rating.objects.get(
                rater=self.request.user,
                ratee=context_data["tarUser"],
            ).rating
        else:
            context_data["rated"] = False
        return context_data

    def check_rating_exists(self, rater, ratee):
        if Rating.objects.filter(
            rater=rater,
            ratee=ratee,
        ).exists():
            return True
        else:
            return False

    def get_success_url(self):
        return reverse('rrapp:rentee_listings')


@method_decorator(login_required, name='dispatch')
class RatingView(generic.UpdateView):
    model = Rating
    template_name = "rrapp/rate_user.html"
    fields = []

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        context_data["pk"] = self.kwargs["ratee_id"]
        print(self.kwargs["ratee_id"])
        print('aaaaa')
        return context_data

    def get_success_url(self):
        return reverse("rrapp:rate_user", args=(self.kwargs["ratee_id"],))

    def post(self, request, *args, **kwargs):
        if not DirectMessagePermission.objects.filter(
                sender=request.user,
                receiver=User.objects.get(id=self.kwargs["ratee_id"]),
                permission=Permission.ALLOWED,
            ).exists():
            print(User.objects.get(id=self.kwargs["ratee_id"]))
            print(request.user)
            print('bbbbbb')
            raise PermissionDenied('You should get permission from the user.')

        # if request.method == 'POST':
        else:
            val = request.POST.get('val')
            ratee = User.objects.get(id=self.kwargs["ratee_id"])
            if Rating.objects.filter(
                rater=request.user,
                ratee=ratee,
            ).exists():
                rating = Rating.objects.get(
                    rater=request.user,
                    ratee=ratee,
                )
                rating.rating = val
                rating.save()
            else:
                Rating.objects.create(
                    rater=request.user,
                    ratee=ratee,
                    rating=val,
                )
            rating_list = Rating.objects.filter(
                ratee=ratee,
            )
            mean_rating = 0.0
            for item in rating_list:
                mean_rating += item.rating
            mean_rating /= len(rating_list)
            ratee.rating = mean_rating
            ratee.save()
            return JsonResponse({'success': 'true', 'score': val}, safe=False)
        return render(
            request,
            'rrapp/rate_user.html',
            {'pk': self.kwargs["ratee_id"]},
        )
        # return HttpResponseRedirect(
        #     reverse("rrapp:rate_user", args=(self.kwargs["pk"],))
        # )


class PersonalQuizView(generic.UpdateView):
    model = Quiz
    template_name = "rrapp/quiz.html"
    form_class = QuizForm

    def get_object(self, queryset=None):
        quiz, created = Quiz.objects.get_or_create(user=self.request.user)
        if created:
            self.request.user.quiz = quiz
            self.request.user.save()
        return quiz

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        context_data["user_id"] = self.request.user.id
        context_data["user"] = self.request.user
        context_data["path"] = self.request.path_info.__contains__("renter")
        context_data["inbox"] = get_inbox_count(self.request.user.username)
        return context_data

    def get_success_url(self):
        return reverse("rrapp:rentee_listings")

    # TODO: 怎么处理renter没做过match的情况。先做quiz然后返送请求和match level

    def post(self, request, *args, **kwargs):
        print("Call Post")
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            print("Form is valid")
            return self.form_valid(form)
        else:
            print("Form is invalid")
            return self.form_invalid(form)


@login_required
def listing_delete(request, pk):
    listing = get_object_or_404(Listing, pk=pk, user_id=request.user.id)

    if request.method == 'POST':
        listing.delete()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('rrapp:my_listings'))
    return render(
        request,
        'rrapp/confirm_delete_listing.html',
        {"user_id": request.user.id, "pk": pk},
    )


@login_required
def deleteAccount(request):
    user = get_object_or_404(User, pk=request.user.id)
    if request.method == 'POST':
        user.delete()
        logout(request)
        return HttpResponseRedirect(reverse('rrapp:home'))
    return render(
        request, 'rrapp/confirm_delete_user.html', {"user_id": request.user.id}
    )


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


def get_inbox_count(username):
    i = 0
    i += get_pending_connections_count(username)
    return i


def rrapp_403(request, exception):
    return render(request, "rrapp/403.html", {}, status=403)


def check_quiz_state(user_id):
    if Quiz.objects.filter(user=user_id).exists():
        cur_quiz = Quiz.objects.get(user=user_id)
        for i in range(1, 9):
            cur_field = "question" + str(i)
            if getattr(cur_quiz, cur_field, None) is None:
                return False
        return True
    else:
        return False
