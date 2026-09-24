import os

from fastapi import FastAPI

app = FastAPI()
key = os.getenv("SERVICE_API_KEY")


@app.get("/health")
def health():
    return {"status": "ok"}
