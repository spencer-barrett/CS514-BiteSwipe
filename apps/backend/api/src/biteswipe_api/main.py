from contextlib import asynccontextmanager

from fastapi import FastAPI

from biteswipe_api.firebase import init_firebase
from biteswipe_api.schemas.Health import HealthResponse
from fastapi import Depends
from biteswipe_api.firebase import get_db
from biteswipe_api.routers import restaurants
from biteswipe_api.routers import restaurants, users
from fastapi.middleware.cors import CORSMiddleware




@asynccontextmanager
async def lifespan(app: FastAPI):
    init_firebase()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(restaurants.router)
app.include_router(users.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/")
async def read_root():
    return {"message": "Hello World!"}


@app.get("/api/health")
def health() -> HealthResponse:
    return HealthResponse(status="ok")
