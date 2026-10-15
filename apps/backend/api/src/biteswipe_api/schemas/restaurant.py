from __future__ import annotations

import datetime as dt
from collections.abc import Sequence
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


class HoursResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    day_of_week: int = Field(description="0 = Sunday")
    open_time: dt.time
    close_time: dt.time
    closes_next_day: bool


class RestaurantSummary(BaseModel):
    """Enough to render one swipe card."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address_line1: str
    city: str
    state: str
    # Declared as float, not Decimal: Pydantic serializes Decimal to a JSON
    # string, and the frontend needs numbers for map and sort math.
    lat: float
    lng: float
    price_level: int | None
    external_rating: float | None
    external_rating_count: int
    cuisines: list[str]
    # Reads `photos` off the ORM object, but also accepts its own name so a
    # dumped model can be re-validated (NearbyRestaurant does this).
    photo_urls: list[str] = Field(
        validation_alias=AliasChoices("photos", "photo_urls")
    )

    @field_validator("cuisines", mode="before")
    @classmethod
    def _flatten_cuisines(cls, value: Sequence[Any]) -> list[str]:
        return [getattr(item, "name", item) for item in value]

    @field_validator("photo_urls", mode="before")
    @classmethod
    def _flatten_photos(cls, value: Sequence[Any]) -> list[str]:
        # Items are RestaurantPhoto rows on the first pass and plain strings
        # when a dumped model is re-validated, so handle both. Photos with no
        # fetched url are dropped rather than emitting nulls.
        urls = [
            item if isinstance(item, str) else getattr(item, "url", None)
            for item in value
        ]
        return [u for u in urls if u]


class RestaurantDetail(RestaurantSummary):
    """Everything on one restaurant's page."""

    zip: str | None
    phone: str | None
    website: str | None
    hours: list[HoursResponse]


class NearbyRestaurant(RestaurantSummary):
    distance_mi: float
