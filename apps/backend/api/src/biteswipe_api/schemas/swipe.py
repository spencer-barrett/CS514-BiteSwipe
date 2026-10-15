"""Request and response models for the swipe loop."""

from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict

from biteswipe_api.schemas.restaurant import RestaurantSummary


class SwipeCreate(BaseModel):
    """One swipe. `liked` is right-swipe; False is a pass."""

    restaurant_id: int
    liked: bool


class SwipeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    restaurant_id: int
    liked: bool
    created_at: dt.datetime


class SwipedRestaurant(RestaurantSummary):
    """A restaurant plus how this user swiped it -- the saved-list shape."""

    liked: bool
    swiped_at: dt.datetime