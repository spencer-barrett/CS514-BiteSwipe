from contextlib import asynccontextmanager

from fastapi import FastAPI

from biteswipe_api.firebase import init_firebase
from biteswipe_api.schemas.Health import HealthResponse
from fastapi import Depends
from biteswipe_api.firebase import get_db
from biteswipe_api.routers import restaurants




@asynccontextmanager
async def lifespan(app: FastAPI):
    init_firebase()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(restaurants.router)


@app.get("/")
async def read_root():
    return {"message": "Hello World!"}


@app.get("/api/health")
def health() -> HealthResponse:
    return HealthResponse(status="ok")
