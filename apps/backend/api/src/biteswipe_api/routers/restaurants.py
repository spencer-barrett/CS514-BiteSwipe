import math

from fastapi import APIRouter, Depends, HTTPException, Query
from google.cloud.firestore import FieldFilter, GeoPoint

from biteswipe_api.firebase import get_db
from biteswipe_api.schemas.Restaurant import NearbyRestaurant, Restaurant

router = APIRouter(prefix="/api/restaurants", tags=["restaurants"])
EARTH_KM = 6371.0
DAY_ORDER = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_KM * math.asin(math.sqrt(a))


def to_restaurant(doc) -> dict:
    d = doc.to_dict()
    gp = d["location"]
    d["location"] = {"lat": gp.latitude, "lng": gp.longitude}
    d["id"] = doc.id
    d["hours"] = {k: d["hours"][k] for k in DAY_ORDER if k in d.get("hours", {})}
    return d


@router.get("/nearby", response_model=list[NearbyRestaurant])
def nearby(
    lat: float = Query(ge=-90, le=90),
    lng: float = Query(ge=-180, le=180),
    radius_km: float = Query(5, gt=0, le=50),
    limit: int = Query(50, ge=1, le=200),
    db=Depends(get_db),
):
    dlat = math.degrees(radius_km / EARTH_KM)
    query = (
        db.collection("restaurants")
        .where(filter=FieldFilter("location", ">=", GeoPoint(max(lat - dlat, -90), -180)))
        .where(filter=FieldFilter("location", "<=", GeoPoint(min(lat + dlat, 90), 180)))
    )

    results = []
    for doc in query.stream():
        r = to_restaurant(doc)
        dist = haversine_km(lat, lng, r["location"]["lat"], r["location"]["lng"])
        if dist <= radius_km:
            r["distanceKm"] = round(dist, 2)
            results.append(r)

    results.sort(key=lambda r: r["distanceKm"])
    return results[:limit]


@router.get("/{restaurant_id}", response_model=Restaurant)
def get_restaurant(restaurant_id: str, db=Depends(get_db)):
    doc = db.collection("restaurants").document(restaurant_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return to_restaurant(doc)