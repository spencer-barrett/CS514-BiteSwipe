from __future__ import annotations

import math
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import Float, cast, func, select
from sqlalchemy.orm import selectinload

from biteswipe_api.dependencies import DbSession
from biteswipe_api.models import Restaurant
from biteswipe_api.schemas.restaurant import (
    NearbyRestaurant,
    RestaurantDetail,
    RestaurantSummary,
)

router = APIRouter(prefix="/api/restaurants", tags=["restaurants"])

EARTH_MI = 3958.8

# Shared eager-loads for anything serialized as a RestaurantSummary.
# selectinload issues one extra query per relationship instead of one per
# row -- without it, serializing 50 cards runs 100+ queries.
CARD_LOADERS = (
    selectinload(Restaurant.cuisines),
    selectinload(Restaurant.photos),
)


@router.get("", response_model=list[RestaurantSummary])
def list_restaurants(
    session: DbSession,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    cuisine: Annotated[str | None, Query(description="filter by cuisine name")] = None,
) -> list[Restaurant]:
    stmt = (
        select(Restaurant)
        .options(*CARD_LOADERS)
        .order_by(Restaurant.id)
        .limit(limit)
        .offset(offset)
    )
    if cuisine:
        stmt = stmt.where(Restaurant.cuisines.any(name=cuisine.strip().lower()))
    return list(session.scalars(stmt))


@router.get("/nearby", response_model=list[NearbyRestaurant])
def nearby(
    session: DbSession,
    lat: Annotated[float, Query(ge=-90, le=90)],
    lng: Annotated[float, Query(ge=-180, le=180)],
    radius_mi: Annotated[float, Query(gt=0, le=30)] = 3.0,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> list[NearbyRestaurant]:
    origin_lat = math.radians(lat)
    origin_lng = math.radians(lng)

    
    row_lat = func.radians(cast(Restaurant.lat, Float), type_=Float())
    row_lng = func.radians(cast(Restaurant.lng, Float), type_=Float())


    distance = (
        2
        * EARTH_MI
        * func.asin(
            func.sqrt(
                func.power(func.sin((row_lat - origin_lat) / 2), 2)
                + math.cos(origin_lat)
                * func.cos(row_lat)
                * func.power(func.sin((row_lng - origin_lng) / 2), 2)
            )
        )
    ).label("distance_mi")

   
    d_lat = math.degrees(radius_mi / EARTH_MI)
    d_lng = d_lat / max(math.cos(origin_lat), 1e-6)

    stmt = (
        select(Restaurant, distance)
        .options(*CARD_LOADERS)
        .where(Restaurant.lat.between(lat - d_lat, lat + d_lat))
        .where(Restaurant.lng.between(lng - d_lng, lng + d_lng))
        .where(distance <= radius_mi)
        .order_by(distance)
        .limit(limit)
    )

    results: list[NearbyRestaurant] = []
    for restaurant, distance_mi in session.execute(stmt).all():
        summary = RestaurantSummary.model_validate(restaurant)
        results.append(
            NearbyRestaurant(**summary.model_dump(), distance_mi=round(distance_mi, 2))
        )
    return results


@router.get("/{restaurant_id}", response_model=RestaurantDetail)
def get_restaurant(restaurant_id: int, session: DbSession) -> Restaurant:
    stmt = (
        select(Restaurant)
        .where(Restaurant.id == restaurant_id)
        .options(*CARD_LOADERS, selectinload(Restaurant.hours))
    )
    restaurant = session.scalar(stmt)
    if restaurant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found"
        )
    return restaurant