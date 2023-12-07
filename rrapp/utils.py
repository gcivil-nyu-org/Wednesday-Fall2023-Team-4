import datetime

from .models import Pets, FoodGroup, Genders


def check_user_listing_match(user, listing):
    if (
        (
            user.pets == listing.pets_allowed
            or listing.pets_allowed == Pets.ALL
            or user.pets == Pets.NONE
        )
        and (
            user.food_group == listing.food_groups_allowed
            or listing.food_groups_allowed == FoodGroup.ALL
        )
        and (
            user.gender == listing.preferred_gender
            or listing.preferred_gender == Genders.ALL
        )
        and (user.smokes == listing.smoking_allowed or listing.smoking_allowed)
        and (
            listing.age_range.lower * 365
            <= (datetime.date.today() - user.birth_date).days
            < listing.age_range.upper * 365
        )
    ):
        return True
    return False
