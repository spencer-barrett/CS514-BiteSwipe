"""The swipe loop: what to show next, recording a swipe, and what was kept.

Everything here is scoped to the authenticated user -- `user_id`
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import exists, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from biteswipe_api.dependencies import CurrentUser, DbSession
from biteswipe_api.models import Restaurant, Swipe
from biteswipe_api.schemas.swipe import (
    SwipeCreate,
    SwipedRestaurant,
    SwipeResponse,
)
from biteswipe_api.schemas.restaurant import RestaurantSummary

router = APIRouter(prefix="/api", tags=["swipes"])

CARD_LOADERS = (
    selectinload(Restaurant.cuisines),
    selectinload(Restaurant.photos),
)


@router.get("/feed", response_model=list[RestaurantSummary])
def feed(
    user: CurrentUser,
    session: DbSession,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    cuisine: Annotated[str | None, Query(description="filter by cuisine name")] = None,
) -> list[Restaurant]:
    """Restaurants this user has not swiped yet.
    """
    already_swiped = exists().where(
        Swipe.user_id == user.id,
        Swipe.restaurant_id == Restaurant.id,
    )

    stmt = (
        select(Restaurant)
        .options(*CARD_LOADERS)
        .where(~already_swiped)
        # Best-rated first so the top of the feed is worth looking at.
        # nullslast() keeps the 4 unrated restaurants from leading.
        .order_by(Restaurant.external_rating.desc().nullslast(), Restaurant.id)
        .limit(limit)
    )
    if cuisine:
        stmt = stmt.where(Restaurant.cuisines.any(name=cuisine.strip().lower()))

    return list(session.scalars(stmt))


@router.post("/swipes", response_model=SwipeResponse)
def create_swipe(
    payload: SwipeCreate,
    user: CurrentUser,
    session: DbSession,
) -> Swipe:
    """Record a swipe, or change one that already exists.
    """
    stmt = (
        insert(Swipe)
        .values(
            user_id=user.id,
            restaurant_id=payload.restaurant_id,
            liked=payload.liked,
        )
        .on_conflict_do_update(
            index_elements=["user_id", "restaurant_id"],
            set_={"liked": payload.liked},
        )
        .returning(Swipe)
    )

    try:
        swipe = session.scalars(stmt).one()
    except IntegrityError as exc:
        # The only FK that can fail here is restaurant_id
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurant {payload.restaurant_id} not found",
        ) from exc

    session.commit()
    return swipe


@router.get("/swipes", response_model=list[SwipedRestaurant])
def list_swipes(
    user: CurrentUser,
    session: DbSession,
    liked: Annotated[bool | None, Query(description="filter to likes or passes")] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[SwipedRestaurant]:
    """This user's swipes, newest first, with the restaurant card attached."""
    stmt = (
        select(Restaurant, Swipe.liked, Swipe.created_at)
        .join(Swipe, Swipe.restaurant_id == Restaurant.id)
        .options(*CARD_LOADERS)
        .where(Swipe.user_id == user.id)
        .order_by(Swipe.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if liked is not None:
        stmt = stmt.where(Swipe.liked == liked)

    results: list[SwipedRestaurant] = []
    for restaurant, was_liked, swiped_at in session.execute(stmt).all():
        summary = RestaurantSummary.model_validate(restaurant)
        results.append(
            SwipedRestaurant(
                **summary.model_dump(), liked=was_liked, swiped_at=swiped_at
            )
        )
    return results