from typing import List
import app.db as db
from psycopg.types.json import Jsonb

def claim_idempotency_key(key: str) -> bool:
    """
    Returns True if key was newly inserted (request should be processed).
    Returns False if key already exists (request already processed).
    """
    sql = "INSERT INTO feed_idempotency_key(key) VALUES (%s) ON CONFLICT DO NOTHING;"
    with db.pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (key,))
            return cur.rowcount == 1

def insert_events(
    user_id: str,
    session_id: str | None,
    variant: str | None,
    context: dict,
    events: List[dict],
) -> int:
    sql = """
    INSERT INTO feed_event(user_id, session_id, item_id, event_type, ts, dwell_ms, rank, variant, context)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    rows = [
        (
            user_id,
            session_id,
            e["item_id"],
            e["type"],
            e["ts"],
            e.get("dwell_ms"),
            e.get("rank"),
            variant,
            Jsonb(context),  
        )
        for e in events
    ]

    with db.pool.connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, rows)
            return len(rows)
