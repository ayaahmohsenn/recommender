import os
import json
import pandas as pd
import psycopg
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

OUT_PATH = "/app/out/item_embeddings.parquet"

def fetch_items(conn) -> pd.DataFrame:
    # Django table for Item model: content_item
    sql = """
    SELECT
      id::text AS item_id,
      title,
      body,
      COALESCE(author, '') AS author,
      COALESCE(tags::text, '[]') AS tags_text,
      status
    FROM content_item
    WHERE status = 'published'
    ORDER BY created_at DESC;
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
    return pd.DataFrame(rows, columns=cols)

def normalize_text(row) -> str:
    # tags_text is like '["python", "django"]' because we selected tags::text
    try:
        tags = json.loads(row["tags_text"])
        if not isinstance(tags, list):
            tags = []
    except Exception:
        tags = []

    parts = [
        str(row.get("title") or ""),
        str(row.get("body") or ""),
        str(row.get("author") or ""),
        " ".join([str(t) for t in tags]),
    ]
    return " ".join(p.strip() for p in parts if p)

def main():
    dsn = os.environ["DATABASE_URL"]
    with psycopg.connect(dsn) as conn:
        items = fetch_items(conn)

    if items.empty:
        raise SystemExit("No published items found in content_item.")

    items["text"] = items.apply(normalize_text, axis=1)

    # TF-IDF: strong baseline for content-based similarity
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2,
        stop_words="english",
    )
    X = vectorizer.fit_transform(items["text"]).astype(np.float32)

    # Store vectors in a portable way
    # We'll convert sparse rows to lists for parquet (fine for small projects).
    vectors = []
    for i in range(X.shape[0]):
        row = X.getrow(i)
        # store as {index:value} to keep it compact
        idx = row.indices.tolist()
        val = row.data.tolist()
        vectors.append({"idx": idx, "val": val})

    out = pd.DataFrame({
        "item_id": items["item_id"],
        "tfidf": vectors,
    })

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    out.to_parquet(OUT_PATH, index=False)

    print(f"Wrote {len(out)} item vectors -> {OUT_PATH}")
    print(out.head(3).to_string(index=False))
    print(f"Vectorizer vocab size: {len(vectorizer.vocabulary_)}")

if __name__ == "__main__":
    main()
