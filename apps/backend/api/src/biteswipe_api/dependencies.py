from __future__ import annotations

from typing import Annotated, Any, cast

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import (  # pyright: ignore[reportMissingTypeStubs]
    auth as firebase_auth,
)
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from biteswipe_api.db import get_session
from biteswipe_api.models import User


bearer_scheme = HTTPBearer(auto_error=False)

DbSession = Annotated[Session, Depends(get_session)]
Credentials = Annotated[
    HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
]


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def verify_token(credentials: Credentials) -> dict[str, Any]:
    """Validate the bearer token and return Firebase's decoded claims.

    Against the emulator (FIREBASE_AUTH_EMULATOR_HOST set) the signature
    check is skipped, so this works locally without a service account.
    """
    if credentials is None:
        raise _unauthorized("Missing bearer token")

    try:
        # firebase-admin ships no type information, so verify_id_token's
        # result is Unknown. cast() pins it here, once -- everything
        # downstream reads a known dict instead of propagating Unknown.
        claims = cast(
            "dict[str, Any]",
            firebase_auth.verify_id_token(credentials.credentials),  # pyright: ignore[reportUnknownMemberType]
        )
    except firebase_auth.ExpiredIdTokenError as exc:
        # The client SDK refreshes hourly; a retry usually succeeds.
        raise _unauthorized("Token expired") from exc
    except firebase_auth.RevokedIdTokenError as exc:
        raise _unauthorized("Token revoked") from exc
    except (firebase_auth.InvalidIdTokenError, ValueError) as exc:
        raise _unauthorized("Invalid token") from exc

    return claims


TokenClaims = Annotated[dict[str, Any], Depends(verify_token)]


def get_current_user(claims: TokenClaims, session: DbSession) -> User:
    """Return the local user for this token, creating the row if needed."""
    uid = claims.get("uid")
    if not isinstance(uid, str) or not uid:
        raise _unauthorized("Token has no uid")

    user = session.scalar(select(User).where(User.firebase_uid == uid))
    if user is not None:
        return user

    email = claims.get("email")
    name = claims.get("name")

    
    session.execute(
        insert(User)
        .values(
            firebase_uid=uid,
            email=email if isinstance(email, str) else "",
            display_name=name if isinstance(name, str) else None,
        )
        .on_conflict_do_nothing(index_elements=["firebase_uid"])
    )
    session.commit()

    user = session.scalar(select(User).where(User.firebase_uid == uid))
    if user is None:  # pragma: no cover -- insert and select both failed
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not provision user",
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]