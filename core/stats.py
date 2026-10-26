from .allocation import split
from .buckets import buckets
from . import settings
from .db import query
from .transactions import transactions

BASES = ("both", "bank", "cash")

def summary():
    """Bank and cash on hand are tracked separately. Spending comes out of the source you picked,
    and cash topped up from the bank lowers the bank. The plan uses the base chosen on the dashboard."""
    r = query("""SELECT
        COALESCE(SUM(CASE WHEN a.type='bank' THEN t.amount END), 0) bank_in,
        COALESCE(SUM(CASE WHEN a.type='cash' THEN t.amount END), 0) cash_in,
        COALESCE(SUM(CASE WHEN a.type='cash' AND t.source='bank' THEN t.amount END), 0) withdrawn,
        COALESCE(SUM(CASE WHEN a.type='spending' AND t.source='cash' THEN t.amount END), 0) spent_cash,
        COALESCE(SUM(CASE WHEN a.type='spending' AND IFNULL(t.source,'bank')!='cash' THEN t.amount END), 0) spent_bank
        FROM transactions t JOIN accounts a ON a.id=t.account_id""")[0]
    bank = r["bank_in"] - r["withdrawn"] - r["spent_bank"]
    cash = r["cash_in"] - r["spent_cash"]
    base = settings.get("calc_base")
    base = base if base in BASES else "both"
    available = {"both": bank + cash, "bank": bank, "cash": cash}[base]
    return {
        "bank": bank, "cash": cash, "spent": r["spent_bank"] + r["spent_cash"],
        "total": bank + cash, "base": base, "available": available,
        "allocation": split(max(available, 0), buckets.all()),  # the chosen money, split by bucket %
    }

def monthly(n=6):
    """Money added (to bank or cash) vs spending per month. The 'income' key means money
    added, because charts.bars() reads that key."""
    data = {}
    for r in query("""SELECT substr(t.date,1,7) month,
                             CASE a.type WHEN 'spending' THEN 'spending' ELSE 'income' END kind,
                             SUM(t.amount) total
                      FROM transactions t JOIN accounts a ON a.id=t.account_id
                      WHERE NOT (a.type='cash' AND IFNULL(t.source,'')='bank')  -- bank to cash is a transfer
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