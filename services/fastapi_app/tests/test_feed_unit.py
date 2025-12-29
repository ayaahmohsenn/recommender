from fastapi.testclient import TestClient
import app.db as db
from app.main import app as fastapi_app  

def test_feed_returns_items_key(monkeypatch):
    monkeypatch.setattr(
        db,
        "fetch_published_items",
        lambda limit: [{"id": "1", "title": "x", "author": "", "created_at": "t", "published_at": "t"}],
    )

    client = TestClient(fastapi_app)
    r = client.get("/feed?limit=5")
    assert r.status_code == 200
    body = r.json()
    assert "items" in body
    assert len(body["items"]) == 1