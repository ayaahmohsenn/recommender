from fastapi import FastAPI, Query
from app.db import fetch_published_items


app = FastAPI(title="Feed Recommender API")

@app.get("/health")
def health():
    return {"status": "ok", "service": "fastapi"}

@app.get("/feed")
def feed(limit: int = Query(30, ge=1, le=100)):
    return {"items": fetch_published_items(limit=limit)}