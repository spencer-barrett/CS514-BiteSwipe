from biteswipe_api.schemas.Health import HealthResponse
from fastapi import FastAPI


app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello World!"}

@app.get("/api/health")
def health() -> HealthResponse:
    return HealthResponse(status="ok")