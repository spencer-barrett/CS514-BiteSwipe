"""Load the cleaned restaurant CSVs into Postgres.

Stage 2 of 2. Run after `alembic upgrade head`, against the CSVs produced by
the ingestion project's clean_restaurants.py.

    uv run python -m biteswipe_api.scripts.seed ../restaurant_ingestion/data/clean
    uv run python -m biteswipe_api.scripts.seed <dir> --reset

The CSVs carry explicit surrogate ids so the foreign keys line up without a
lookup pass. Those ids are inserted verbatim, which leaves each table's
sequence behind the data, so the sequences are advanced at the end -- skip
that and the first API-created row collides with a seeded one.

Only restaurant reference data is touched. `users` and `swipes` are never
read or written here.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import sys
from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import insert, select, text
from sqlalchemy.orm import Session

from biteswipe_api.db import SessionLocal
from biteswipe_api.models import (
    Cuisine,
    Restaurant,
    RestaurantCuisine,
    RestaurantHour,
    RestaurantPhoto,
)

CHUNK = 500


# --------------------------------------------------------------------------
# CSV value coercion
#
# csv.DictReader hands back strings for everything, including "" for NULL
# and "True"/"False" for booleans. Postgres will not take those as-is for
# typed columns, so each value is converted explicitly.
# --------------------------------------------------------------------------


def as_str(value: str) -> str | None:
    value = value.strip()
    return value or None


def as_int(value: str) -> int | None:
    value = value.strip()
    return int(value) if value else None


def as_decimal(value: str) -> Decimal | None:
    value = value.strip()
    return Decimal(value) if value else None


def as_bool(value: str) -> bool:
    return value.strip().lower() in {"true", "t", "1", "yes"}


def as_time(value: str) -> dt.time:
    return dt.time.fromisoformat(value.strip())


def read_csv(path: Path) -> Iterator[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"missing CSV: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        yield from csv.DictReader(handle)


def chunked(rows: list[dict[str, Any]], size: int = CHUNK) -> Iterator[list[dict[str, Any]]]:
    for start in range(0, len(rows), size):
        yield rows[start : start + size]


# --------------------------------------------------------------------------
# Row builders
# --------------------------------------------------------------------------


def build_cuisines(data_dir: Path) -> list[dict[str, Any]]:
    return [
        {"id": int(row["id"]), "name": row["name"].strip()}
        for row in read_csv(data_dir / "cuisines.csv")
    ]


def build_restaurants(data_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in read_csv(data_dir / "restaurants.csv"):
        rows.append(
            {
                "id": int(row["id"]),
                "name": row["name"].strip(),
                "address_line1": row["address_line1"].strip(),
                "city": row["city"].strip(),
                "state": row["state"].strip().upper(),
                "zip": as_str(row["zip"]),
                "lat": as_decimal(row["lat"]),
                "lng": as_decimal(row["lng"]),
                "price_level": as_int(row["price_level"]),
                "external_rating": as_decimal(row["external_rating"]),
                "external_rating_count": as_int(row["external_rating_count"]) or 0,
                "phone": as_str(row["phone"]),
                "website": as_str(row["website"]),
                "google_place_id": as_str(row["google_place_id"]),
                "source_id": as_str(row["source_id"]),
            }
        )
    return rows


def build_links(data_dir: Path) -> list[dict[str, Any]]:
    return [
        {
            "restaurant_id": int(row["restaurant_id"]),
            "cuisine_id": int(row["cuisine_id"]),
        }
        for row in read_csv(data_dir / "restaurant_cuisines.csv")
    ]


def build_photos(data_dir: Path) -> list[dict[str, Any]]:
    return [
        {
            "restaurant_id": int(row["restaurant_id"]),
            "photo_ref": row["photo_ref"].strip(),
            "position": int(row["position"]),
        }
        for row in read_csv(data_dir / "restaurant_photos.csv")
    ]


def build_hours(data_dir: Path) -> list[dict[str, Any]]:
    return [
        {
            "restaurant_id": int(row["restaurant_id"]),
            "day_of_week": int(row["day_of_week"]),
            "open_time": as_time(row["open_time"]),
            "close_time": as_time(row["close_time"]),
            "closes_next_day": as_bool(row["closes_next_day"]),
        }
        for row in read_csv(data_dir / "restaurant_hours.csv")
    ]


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------


def reset(session: Session) -> None:
    """Clear seeded reference data.

    RESTART IDENTITY resets the sequences; CASCADE reaches `swipes`, which is
    why --reset is opt-in rather than the default.
    """
    session.execute(
        text(
            "TRUNCATE restaurants, cuisines, restaurant_cuisines, "
            "restaurant_photos, restaurant_hours "
            "RESTART IDENTITY CASCADE"
        )
    )


def already_seeded(session: Session) -> bool:
    return session.scalar(select(Restaurant.id).limit(1)) is not None


def sync_sequences(session: Session) -> None:
    """Advance each sequence past the highest explicitly inserted id."""
    for table, column in (
        ("restaurants", "id"),
        ("cuisines", "id"),
        ("restaurant_photos", "id"),
        ("restaurant_hours", "id"),
    ):
        session.execute(
            text(
                f"SELECT setval(pg_get_serial_sequence('{table}', '{column}'), "
                f"COALESCE((SELECT MAX({column}) FROM {table}), 1), true)"
            )
        )


def seed(data_dir: Path, *, do_reset: bool) -> int:
    payloads = (
        (Cuisine, build_cuisines(data_dir)),
        (Restaurant, build_restaurants(data_dir)),
        (RestaurantCuisine, build_links(data_dir)),
        (RestaurantPhoto, build_photos(data_dir)),
        (RestaurantHour, build_hours(data_dir)),
    )

    with SessionLocal() as session:
        if do_reset:
            reset(session)
        elif already_seeded(session):
            print(
                "restaurants table is not empty; pass --reset to replace "
                "(this also deletes swipes via CASCADE)",
                file=sys.stderr,
            )
            return 1

        # One transaction: a failure part-way leaves no partial seed behind.
        for model, rows in payloads:
            if not rows:
                continue
            for batch in chunked(rows):
                session.execute(insert(model), batch)
            print(f"  {model.__tablename__:24} {len(rows):>6}")

        sync_sequences(session)
        session.commit()

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir", type=Path, help="directory holding the cleaned CSVs")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="truncate seeded tables first (CASCADEs to swipes)",
    )
    args = parser.parse_args()

    print(f"seeding from {args.data_dir}")
    status = seed(args.data_dir, do_reset=args.reset)
    if status == 0:
        print("done")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
