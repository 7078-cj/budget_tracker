"""Pure functions: no database, no UI."""

import math

REST_LABEL = "Needs & bills"

def validate(percents):
    if any(not math.isfinite(p) for p in percents):
        raise ValueError("Percentages must be finite numbers")
    if any(p < 0 for p in percents):
        raise ValueError("Percentages can't be negative")
    total = sum(percents)
    if abs(total - 100) > 0.0001:
        raise ValueError(f"Percentages must add up to 100% (currently {total:g}%)")

def split(amount, buckets):
    """Split `amount` across the explicitly configured allocation buckets."""
    return [{"label": b["label"], "percent": b["percent"], "amount": amount * b["percent"] / 100}
            for b in buckets]
