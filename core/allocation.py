"""Pure functions: no database, no UI."""

REST_LABEL = "Needs & bills (rest)"

def validate(percents):
    if any(p < 0 for p in percents):
        raise ValueError("Percentages can't be negative")
    if sum(percents) > 100.0001:
        raise ValueError(f"Total is {sum(percents):g}%, it can't exceed 100%")

def split(amount, buckets):
    """Split `amount` across buckets; whatever is left goes to needs & bills."""
    parts = [{"label": b["label"], "percent": b["percent"], "amount": amount * b["percent"] / 100}
             for b in buckets]
    rest = 100 - sum(b["percent"] for b in buckets)
    parts.append({"label": REST_LABEL, "percent": rest, "amount": amount * rest / 100})
    return parts