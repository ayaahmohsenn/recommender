from fastapi import FastAPI, Query
import app.db as db
from app.schemas import EventsIn, EventsOut
from app.events_repo import claim_idempotency_key, insert_events
from app.ranking import recency_score, blend_score
from app.cache import cache_get, cache_set

app = FastAPI(title="Feed Recommender API")

@app.get("/health")
def health():
    return {"status": "ok", "service": "fastapi"}

@app.get("/feed")
def feed(
    limit: int = Query(30, ge=1, le=100),
    user_id: str | None = None,
    nocache: int = 0,
):
    cache_key = f"feed:v1:user={user_id or 'anon'}:limit={limit}"
    if not nocache:
        cached = cache_get(cache_key)
        if cached:
            return cached

    items = db.fetch_published_items(limit=200)
    pop = db.fetch_popular_item_scores(hours=24, limit=500)

    scored = []
    for it in items:
        r = recency_score(it["created_at"])
        p = pop.get(it["id"], 0.0)
        score = blend_score(r, p)
        scored.append({**it, "score": score, "recency": r, "popularity": p})

    scored.sort(key=lambda x: x["score"], reverse=True)
    resp = {"items": scored[:limit]}
    cache_set(cache_key, resp, ttl_seconds=10)
    return resp

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