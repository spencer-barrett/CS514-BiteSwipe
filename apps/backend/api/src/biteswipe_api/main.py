from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from biteswipe_api.config import get_settings
from biteswipe_api.firebase import init_firebase
from biteswipe_api.routers import restaurants, users
from biteswipe_api.schemas.health import HealthResponse
from biteswipe_api.routers import restaurants, swipes, users

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    init_firebase()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[get_settings().frontend_origin],
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(restaurants.router)
app.include_router(users.router)
app.include_router(swipes.router)


@app.get("/api/health")
def health() -> HealthResponse:
    return HealthResponse(status="ok")
