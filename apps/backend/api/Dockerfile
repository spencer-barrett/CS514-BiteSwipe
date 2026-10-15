# Build context is this file's own directory (apps/backend/api) -- that is
# how Heroku builds from heroku.yml -- so every path below is relative to it.
# To build locally the same way:
#   docker build -t biteswipe-api apps/backend/api

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
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Now the application itself: src/, alembic.ini, migrations/, data/.
# .dockerignore keeps .venv and friends out -- a macOS .venv copied into a
# Linux image produces broken binaries and a much larger image.
COPY . ./
RUN uv sync --frozen --no-dev

# Shell form on purpose -- $PORT is injected by Heroku at runtime and has to
# be expanded by a shell. Exec form would pass the literal string "$PORT".
CMD uvicorn biteswipe_api.main:app --host 0.0.0.0 --port ${PORT:-8000}