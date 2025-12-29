from fastapi import FastAPI, Query
from app.db import fetch_published_items
from app.schemas import EventsIn, EventsOut
from app.events_repo import claim_idempotency_key, insert_events

app = FastAPI(title="Feed Recommender API")

@app.get("/health")
def health():
    return {"status": "ok", "service": "fastapi"}

@app.get("/feed")
def feed(limit: int = Query(30, ge=1, le=100)):
    return {"items": fetch_published_items(limit=limit)}

@app.post("/events", response_model=EventsOut)
def post_events(payload: EventsIn):
    is_new = claim_idempotency_key(payload.idempotency_key)
    if not is_new:
        # already processed; return success but mark as deduped
        return EventsOut(accepted=0, deduped=True)

    accepted = insert_events(
        user_id=payload.user_id,
        session_id=payload.session_id,
        variant=payload.variant,
        context=payload.context,
        events=[e.model_dump() for e in payload.events],
    )
    return EventsOut(accepted=accepted, deduped=False)