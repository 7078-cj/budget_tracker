from .accounts import TYPES
from .allocation import split
from .buckets import buckets
from .db import query
from .transactions import transactions

def summary():
    """Money on hand = money added to bank + cash on hand - spending."""
    totals = dict.fromkeys(TYPES, 0.0)
    for r in query("""SELECT a.type, COALESCE(SUM(t.amount),0) total FROM accounts a
                      LEFT JOIN transactions t ON t.account_id=a.id GROUP BY a.type"""):
        totals[r["type"]] = r["total"]
    available = totals["bank"] + totals["cash"] - totals["spending"]
    return {
        "totals": totals,
        "available": available,
        "allocation": split(max(available, 0), buckets.all()),  # your money, split by bucket %
    }

def monthly(n=6):
    """Money added (to bank or cash) vs spending per month. The 'income' key means money
    added, because charts.bars() reads that key."""
    data = {}
    for r in query("""SELECT substr(t.date,1,7) month,
                             CASE a.type WHEN 'spending' THEN 'spending' ELSE 'income' END kind,
                             SUM(t.amount) total
                      FROM transactions t JOIN accounts a ON a.id=t.account_id
                      GROUP BY month, kind"""):
        data.setdefault(r["month"], {"income": 0.0, "spending": 0.0})[r["kind"]] = r["total"]
    return [{"month": m, **data[m]} for m in sorted(data)[-n:]]

def emergency_target(months=(3, 6)):
    """Common rule of thumb: 3 to 6 months of your average monthly spending."""
    spends = [m["spending"] for m in monthly(120) if m["spending"] > 0]
    avg = sum(spends) / len(spends) if spends else 0.0
    return tuple(avg * k for k in months)

def recent(n=5):
    return transactions.all()[:n]