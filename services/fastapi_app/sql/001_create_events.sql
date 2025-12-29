CREATE TABLE IF NOT EXISTS feed_event (
  id BIGSERIAL PRIMARY KEY,
  user_id TEXT NOT NULL,
  session_id TEXT,
  item_id UUID NOT NULL,
  event_type TEXT NOT NULL,
  ts TIMESTAMPTZ NOT NULL,
  dwell_ms INTEGER,
  rank INTEGER,
  variant TEXT,
  context JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS ix_feed_event_user_ts ON feed_event (user_id, ts DESC);
CREATE INDEX IF NOT EXISTS ix_feed_event_item_ts ON feed_event (item_id, ts DESC);
CREATE INDEX IF NOT EXISTS ix_feed_event_type_ts ON feed_event (event_type, ts DESC);