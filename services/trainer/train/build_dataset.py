import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import pandas as pd
import psycopg


EVENT_WEIGHTS = {
    "click": 3.0,
    "like": 4.0,
    "save": 5.0,
    "share": 6.0,
    "impression": 0.2,
    "hide": -2.0,   # optional negative signal
}

POSITIVE_EVENTS = {"click", "like", "save", "share"}


@dataclass
class Config:
    days: int = 7
    out_path: str = "/app/out/interactions.parquet"


def fetch_interactions(conn, since_ts: datetime) -> pd.DataFrame:
    sql = """
    SELECT
      user_id,
      item_id::text AS item_id,
      event_type,
      ts,
      COALESCE(variant, '') AS variant,
      COALESCE(context->>'surface', '') AS surface,
      dwell_ms
    FROM feed_event
    WHERE ts >= %s
    ORDER BY ts ASC;
    """
    with conn.cursor() as cur:
        cur.execute(sql, (since_ts,))
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]
    return pd.DataFrame(rows, columns=cols)



def transform(df: pd.DataFrame) -> pd.DataFrame:
    # normalize types
    df["event_type"] = df["event_type"].astype(str)

    # map weights
    df["weight"] = df["event_type"].map(EVENT_WEIGHTS).fillna(0.0)

    # label: 1 for positive events, 0 otherwise (we'll refine later)
    df["label"] = df["event_type"].isin(POSITIVE_EVENTS).astype(int)

    # minimal cleanup: drop unknown item/user
    df = df[df["user_id"].notna() & (df["user_id"] != "")]
    df = df[df["item_id"].notna() & (df["item_id"] != "")]

    # keep only columns we want downstream
    return df[["user_id", "item_id", "label", "ts", "weight", "surface", "variant", "event_type", "dwell_ms"]]


def main():
    cfg = Config()
    dsn = os.environ["DATABASE_URL"]

    since_ts = datetime.now(timezone.utc) - timedelta(days=cfg.days)

    with psycopg.connect(dsn) as conn:
        raw = fetch_interactions(conn, since_ts)
        out = transform(raw)

    # write parquet
    os.makedirs(os.path.dirname(cfg.out_path), exist_ok=True)
    out.to_parquet(cfg.out_path, index=False)

    print(f"Wrote {len(out)} rows -> {cfg.out_path}")
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", 50)
    print(out.head(5).to_string(index=False))



if __name__ == "__main__":
    main()
