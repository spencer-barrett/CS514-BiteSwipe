from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from biteswipe_api.config import get_settings


class Base(DeclarativeBase):
    pass


engine = create_engine(
    get_settings().database_url,
    # Verifies a pooled connection before handing it out. Essential against a
    # serverless Postgres: Neon drops idle connections when it scales to zero,
    # and without this the first request after an idle period fails.
    pool_pre_ping=True,
    # Kept small on purpose. One Heroku dyno runs a handful of workers, and
    # every worker holds its own pool -- an unbounded default is how a free
    # Postgres tier runs out of connections.
    pool_size=5,
    max_overflow=5,
    # Recycle before any proxy or provider idle timeout can close a connection
    # underneath us.
    pool_recycle=300,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session() -> Generator[Session]:
    with SessionLocal() as session:
        yield session