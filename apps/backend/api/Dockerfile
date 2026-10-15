# Build context is the REPO ROOT, not apps/backend/api -- heroku.yml builds
# from the directory it sits in and offers no way to change the context, so
# every COPY path below is written relative to the repo root.

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

RUN pip install --no-cache-dir uv

WORKDIR /app

# Dependencies first, in their own layer: these change far less often than
# source, so edits to the app skip the whole install step on rebuild.
# --no-install-project installs only the dependencies, not biteswipe_api.
COPY apps/backend/api/pyproject.toml apps/backend/api/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Now the application itself: src/, alembic.ini, migrations/, data/.
COPY apps/backend/api/ ./
RUN uv sync --frozen --no-dev

# Shell form on purpose -- $PORT is injected by Heroku at runtime and has to
# be expanded by a shell. Exec form would pass the literal string "$PORT".
CMD uvicorn biteswipe_api.main:app --host 0.0.0.0 --port ${PORT:-8000}