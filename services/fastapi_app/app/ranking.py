from datetime import datetime, timezone
import math

def recency_score(created_at_iso: str, half_life_hours: float = 24.0) -> float:
    """
    Exponential decay score: newer -> higher.
    half_life_hours = how fast freshness decays.
    """
    created = datetime.fromisoformat(created_at_iso.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    age_hours = max((now - created).total_seconds() / 3600.0, 0.0)

    # exponential half-life decay
    return math.pow(0.5, age_hours / half_life_hours)

def blend_score(recency: float, popularity: float, w_recency: float = 1.0, w_pop: float = 0.15) -> float:
    return (w_recency * recency) + (w_pop * popularity)