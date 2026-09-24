import os

from fastapi import FastAPI

app = FastAPI()
service_key = os.getenv("SERVICE_API_KEY")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
