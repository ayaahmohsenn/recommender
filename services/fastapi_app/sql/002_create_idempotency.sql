CREATE TABLE IF NOT EXISTS feed_idempotency_key (
  key TEXT PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Optional cleanup index if you later want TTL-based deletion
CREATE INDEX IF NOT EXISTS ix_feed_idempotency_created_at ON feed_idempotency_key (created_at);
