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
