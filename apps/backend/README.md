# BiteSwipe — API

The FastAPI backend for BiteSwipe. It lives in `apps/backend/api` within the monorepo.

## Prerequisites

Install these before anything else.

| Tool | Version | Check |
| --- | --- | --- |
| [Git](https://git-scm.com/downloads) | any recent | `git --version` |
| [uv](https://docs.astral.sh/uv/) | any recent | `uv --version` |
| Python | 3.12 or newer | installed by uv if missing |

### Installing uv

uv manages Python versions, the virtual environment, and dependencies. You don't need to install Python separately or activate a virtual environment.

**macOS / Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**macOS** with Homebrew (alternative):

```bash
brew install uv
```

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart your terminal afterward so `uv` is on your PATH.

## 1. Clone the repository

```bash
git clone https://github.com/spencer-barrett/CS514-BiteSwipe.git
cd CS514-BiteSwipe
```

## 2. Install dependencies

```bash
cd apps/backend/api
uv sync
```

This creates `.venv/`, installs Python 3.12 if needed, and installs every dependency (including dev tools) at the exact versions pinned in `uv.lock`.

## 3. Run the server

```bash
uv run uvicorn biteswipe_api.main:app --reload
```

- Health check: http://localhost:8000/api/health
- Interactive API docs: http://localhost:8000/docs

`--reload` restarts the server whenever you save a file.

> Always run commands from `apps/backend/api` and prefix them with `uv run`. That guarantees they use the project's environment rather than your system Python.

## Common commands

| Command | What it does |
| --- | --- |
| `uv run uvicorn biteswipe_api.main:app --reload` | Start the dev server |
| `uv run pytest` | Run the tests |
| `uv run pyright` | Type-check (strict mode) |
| `uv run ruff check .` | Lint |
| `uv run ruff check . --fix` | Lint and auto-fix what's fixable |
| `uv run ruff format .` | Format code |
| `uv add <package>` | Add a dependency |
| `uv add --dev <package>` | Add a dev-only dependency |

Run `pyright`, `ruff check`, and `ruff format` before pushing.

## Project structure

```
apps/backend/api/
├── pyproject.toml        # project metadata, dependencies, tool config
├── uv.lock               # pinned dependency versions (commit this)
├── src/
│   └── biteswipe_api/
│       ├── __init__.py
│       ├── main.py       # FastAPI app and routes
│       └── schemas/      # Pydantic request/response models
└── tests/
```


## Troubleshooting

**`command not found: uv`** — restart your terminal after installing, or check that `~/.local/bin` is on your PATH.

**`command not found: uvicorn`** — you ran it without `uv run`. Uvicorn lives in the project's `.venv`, not globally.

**`No module named biteswipe_api`** — run `uv sync` from `apps/backend/api`. If it persists, confirm `src/biteswipe_api/__init__.py` exists.

**Errors after pulling new changes** — dependencies may have changed. Run `uv sync` again.

**Strange import or path errors after moving or renaming the folder** — delete `.venv/` and run `uv sync`. Virtual environments store absolute paths.

**Port 8000 already in use** — stop the other process, or run with `--port 8001`.

**Pydantic validation error on startup** — a required value in `.env` is missing or commented out.
