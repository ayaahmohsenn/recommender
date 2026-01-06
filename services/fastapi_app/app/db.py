import os
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
pool = ConnectionPool(conninfo=DATABASE_URL, min_size=1, max_size=5)

def fetch_published_items(limit: int = 30):
    sql = """
    SELECT id::text, title, author, created_at, published_at
    FROM content_item
    WHERE status = 'published'
    ORDER BY created_at DESC
    LIMIT %s;
    """
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (limit,))
            rows = cur.fetchall()

    return [
        {
            "id": r[0],
            "title": r[1],
            "author": r[2],
            "created_at": r[3].isoformat(),
            "published_at": r[4].isoformat() if r[4] else None,
        }
        for r in rows
    ]

def fetch_popular_item_scores(hours:int = 24, limit:int = 100):
    sql = """
    SELECT item_id::text,
           SUM(
             CASE event_type
               WHEN 'click' THEN 3
               WHEN 'like' THEN 4
               WHEN 'save' THEN 5
               WHEN 'share' THEN 6
               WHEN 'impression' THEN 0.2
               ELSE 0
             END
           ) AS score
    FROM feed_event
    WHERE ts >= now() - (%s || ' hours')::interval
    GROUP BY item_id
    ORDER BY score DESC
    LIMIT %s;
    """
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (hours, limit))
            rows = cur.fetchall()

    return {item_id: float(score) for item_id, score in rows}