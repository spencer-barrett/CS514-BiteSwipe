from __future__ import annotations

import datetime as dt
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from biteswipe_api.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    firebase_uid: Mapped[str] = mapped_column(Text, unique=True, index=True)
    email: Mapped[str] = mapped_column(Text)
    display_name: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    swipes: Mapped[list[Swipe]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Cuisine(Base):
    __tablename__ = "cuisines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True)

    restaurants: Mapped[list[Restaurant]] = relationship(
        secondary="restaurant_cuisines", back_populates="cuisines"
    )


class Restaurant(Base):
    __tablename__ = "restaurants"
    __table_args__ = (
        CheckConstraint(
            "price_level BETWEEN 1 AND 4", name="ck_restaurants_price_level"
        ),
        CheckConstraint(
            "external_rating BETWEEN 0 AND 5", name="ck_restaurants_rating"
        ),
        CheckConstraint("lat BETWEEN -90 AND 90", name="ck_restaurants_lat"),
        CheckConstraint("lng BETWEEN -180 AND 180", name="ck_restaurants_lng"),
        # No UNIQUE on google_place_id yet: six IDs in the seed data are each
        # shared by two different businesses.
        Index("ix_restaurants_place_id", "google_place_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    address_line1: Mapped[str] = mapped_column(Text)
    city: Mapped[str] = mapped_column(Text)
    state: Mapped[str] = mapped_column(String(2))
    zip: Mapped[str | None] = mapped_column(String(10))

    lat: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    lng: Mapped[Decimal] = mapped_column(Numeric(9, 6))

    price_level: Mapped[int | None] = mapped_column(SmallInteger)
    external_rating: Mapped[Decimal | None] = mapped_column(Numeric(2, 1))
    external_rating_count: Mapped[int] = mapped_column(Integer, default=0)

    phone: Mapped[str | None] = mapped_column(String(20))
    website: Mapped[str | None] = mapped_column(Text)
    google_place_id: Mapped[str | None] = mapped_column(Text)

    # Original id from the seed JSON, kept so a flagged row can be traced
    # back to its source record.
    source_id: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    cuisines: Mapped[list[Cuisine]] = relationship(
        secondary="restaurant_cuisines", back_populates="restaurants"
    )
    photos: Mapped[list[RestaurantPhoto]] = relationship(
        back_populates="restaurant",
        cascade="all, delete-orphan",
        order_by="RestaurantPhoto.position",
    )
    hours: Mapped[list[RestaurantHour]] = relationship(
        back_populates="restaurant", cascade="all, delete-orphan"
    )
    swipes: Mapped[list[Swipe]] = relationship(
        back_populates="restaurant", cascade="all, delete-orphan"
    )


class RestaurantCuisine(Base):
    """Association table. Composite PK means a pairing can't be duplicated."""

    __tablename__ = "restaurant_cuisines"
    __table_args__ = (Index("ix_restaurant_cuisines_cuisine", "cuisine_id"),)

    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id", ondelete="CASCADE"), primary_key=True
    )
    cuisine_id: Mapped[int] = mapped_column(
        ForeignKey("cuisines.id", ondelete="CASCADE"), primary_key=True
    )


class RestaurantPhoto(Base):
    __tablename__ = "restaurant_photos"
    __table_args__ = (
        UniqueConstraint(
            "restaurant_id", "position", name="uq_restaurant_photos_position"
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id", ondelete="CASCADE"), index=True
    )
    photo_ref: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column(SmallInteger)

    restaurant: Mapped[Restaurant] = relationship(back_populates="photos")


class RestaurantHour(Base):
    # One row per opening interval. No row for a day means closed.


    __tablename__ = "restaurant_hours"
    __table_args__ = (
        CheckConstraint(
            "day_of_week BETWEEN 0 AND 6", name="ck_restaurant_hours_dow"
        ),
        Index("ix_restaurant_hours_lookup", "restaurant_id", "day_of_week"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id", ondelete="CASCADE")
    )
    day_of_week: Mapped[int] = mapped_column(SmallInteger)  # 0 = Sunday
    open_time: Mapped[dt.time] = mapped_column(Time)
    close_time: Mapped[dt.time] = mapped_column(Time)
    closes_next_day: Mapped[bool] = mapped_column(Boolean, default=False)

    restaurant: Mapped[Restaurant] = relationship(back_populates="hours")


class Swipe(Base):
    __tablename__ = "swipes"
    __table_args__ = (
        UniqueConstraint("user_id", "restaurant_id", name="uq_swipes_user_restaurant"),
        Index("ix_swipes_user_recent", "user_id", "created_at"),
        Index(
            "ix_swipes_liked",
            "restaurant_id",
            postgresql_where=text("liked"),
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id", ondelete="CASCADE")
    )
    liked: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped[User] = relationship(back_populates="swipes")
    restaurant: Mapped[Restaurant] = relationship(back_populates="swipes")