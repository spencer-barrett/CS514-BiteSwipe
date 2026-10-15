from __future__ import annotations

import os
from typing import Any

import firebase_admin  # pyright: ignore[reportMissingTypeStubs]
from firebase_admin import (  # pyright: ignore[reportMissingTypeStubs]
    credentials,
)

from biteswipe_api.config import get_settings

TOKEN_URI = "https://oauth2.googleapis.com/token"


def _bridge_emulator_env() -> None:

    host = get_settings().firebase_auth_emulator_host
    if host:
        os.environ.setdefault("FIREBASE_AUTH_EMULATOR_HOST", host)


def _using_emulator() -> bool:
    return bool(os.environ.get("FIREBASE_AUTH_EMULATOR_HOST"))


def _service_account_credentials() -> credentials.Certificate | None:

    settings = get_settings()
    project_id = settings.firebase_project_id
    client_email = settings.firebase_client_email
    private_key = settings.firebase_private_key

    if not (project_id and client_email and private_key):
        return None

    return credentials.Certificate(  # pyright: ignore[reportUnknownMemberType]
        {
            "type": "service_account",
            "project_id": project_id,
            "client_email": client_email,
            # The key is a multi-line PEM stored on one line in .env, so the
            # escaped newlines have to be turned back into real ones.
            "private_key": private_key.get_secret_value().replace("\\n", "\n"),
            "token_uri": TOKEN_URI,
        }
    )


def init_firebase() -> None:

    _bridge_emulator_env()

    try:
        firebase_admin.get_app()  # pyright: ignore[reportUnknownMemberType]
        return
    except ValueError:
        pass

    project_id = get_settings().firebase_project_id
    options: dict[str, Any] | None = {"projectId": project_id} if project_id else None

    if _using_emulator():
        # The emulator accepts any caller; credentials would be ignored.
        firebase_admin.initialize_app(options=options)  # pyright: ignore[reportUnknownMemberType]
        return

    firebase_admin.initialize_app(  # pyright: ignore[reportUnknownMemberType]
        credential=_service_account_credentials(),
        options=options,
    )
