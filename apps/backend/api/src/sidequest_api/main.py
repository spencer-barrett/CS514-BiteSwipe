from fastapi import FastAPI

from src.schemas.Health import HealthResponse

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello World!"}

@app.get("/api/health")
def health() -> HealthResponse:
    return HealthResponse(status="ok")