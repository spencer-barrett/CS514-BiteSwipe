from pydantic import BaseModel


class Interval(BaseModel):
    open: str
    close: str


class Location(BaseModel):
    lat: float
    lng: float


class Restaurant(BaseModel):
    id: str
    name: str
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip: str | None = None
    location: Location
    cuisines: list[str] = []
    priceLevel: int | None = None
    rating: float | None = None
    ratingCount: int = 0
    photoRefs: list[str] = []
    hours: dict[str, list[Interval]] = {}
    phone: str | None = None
    website: str | None = None


class NearbyRestaurant(Restaurant):
    distanceKm: float