import math

from fastapi import APIRouter, Depends, HTTPException, Query
from google.cloud.firestore import FieldFilter, GeoPoint

from biteswipe_api.firebase import get_db
from biteswipe_api.schemas.Restaurant import NearbyRestaurant, Restaurant

router = APIRouter(prefix="/api/restaurants", tags=["restaurants"])
EARTH_MI = 3958.8
DAY_ORDER = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]


def haversine_mi(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_MI * math.asin(math.sqrt(a))


def to_restaurant(doc) -> dict:
    d = doc.to_dict()
    gp = d["location"]
    d["location"] = {"lat": gp.latitude, "lng": gp.longitude}
    d["id"] = doc.id
    hours = d.get("hours", {})
    d["hours"] = {k: hours[k] for k in DAY_ORDER if k in hours}
    return d


@router.get("/nearby", response_model=list[NearbyRestaurant])
def nearby(
    lat: float = Query(ge=-90, le=90),
    lng: float = Query(ge=-180, le=180),
    radius_mi: float = Query(3, gt=0, le=30),
    limit: int = Query(50, ge=1, le=200),
    db=Depends(get_db),
):
    dlat = math.degrees(radius_mi / EARTH_MI)
    query = (
        db.collection("restaurants")
        .where(filter=FieldFilter("location", ">=", GeoPoint(max(lat - dlat, -90), -180)))
        .where(filter=FieldFilter("location", "<=", GeoPoint(min(lat + dlat, 90), 180)))
    )

    results = []
    for doc in query.stream():
        r = to_restaurant(doc)
        dist = haversine_mi(lat, lng, r["location"]["lat"], r["location"]["lng"])
        if dist <= radius_mi:
            r["distanceMi"] = round(dist, 2)
            results.append(r)

    results.sort(key=lambda r: r["distanceMi"])
    return results[:limit]


@router.get("/{restaurant_id}", response_model=Restaurant)
def get_restaurant(restaurant_id: str, db=Depends(get_db)):
    doc = db.collection("restaurants").document(restaurant_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return to_restaurant(doc)