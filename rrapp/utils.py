import datetime

from .models import Pets, FoodGroup
def check_user_listing_match(user, l):
  print((
            l.age_range.lower * 365
            <= (datetime.date.today() - user.birth_date).days
            < l.age_range.upper * 365
        ), l.age_range.lower * 365, datetime.date.today(), user.birth_date, (datetime.date.today() - user.birth_date).days, l.age_range.upper * 365)
  if (
        (user.pets == l.pets_allowed or l.pets_allowed == Pets.ALL or user.pets == Pets.NONE)
        and (
            user.food_group == l.food_groups_allowed
            or l.food_groups_allowed == FoodGroup.ALL
        )
        and (user.smokes == l.smoking_allowed or l.smoking_allowed == True)
        and (
            l.age_range.lower * 365
            <= (datetime.date.today() - user.birth_date).days
            < l.age_range.upper * 365
        )
    ):
    return True
  return False