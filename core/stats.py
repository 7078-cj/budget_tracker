from datetime import date

from .allocation import split
from .buckets import buckets
from . import settings
from .db import query
from .transactions import transactions

BASES = ("both", "bank", "cash")

def average_monthly_added(base, months=6):
    """Average new money added per tracked month, excluding transfers and spending."""
    if base not in BASES:
        base = "both"

    today = date.today()
    current_month = today.year * 12 + today.month
    first_month = current_month - months + 1
    start_year, start_month = divmod(first_month - 1, 12)
    start_date = date(start_year, start_month + 1, 1).isoformat()
    next_year, next_month = divmod(current_month, 12)
    end_date = date(next_year, next_month + 1, 1).isoformat()

    rows = query("""SELECT substr(t.date, 1, 7) month,
                           SUM(CASE WHEN a.type='bank' THEN t.amount ELSE 0 END) bank_added,
                           SUM(CASE WHEN a.type='cash' AND IFNULL(t.source,'')!='bank'
                                    THEN t.amount ELSE 0 END) cash_added
                    FROM transactions t JOIN accounts a ON a.id=t.account_id
                    WHERE t.date >= ? AND t.date < ?
                      AND (a.type='bank' OR a.type='cash')
                    GROUP BY month ORDER BY month""", (start_date, end_date))
    amounts = [
        row["bank_added"] if base == "bank" else
        row["cash_added"] if base == "cash" else
        row["bank_added"] + row["cash_added"]
        for row in rows
    ]
    active = [amount for amount in amounts if amount > 0]
    if not active:
        return 0.0

    # Count quiet months after the first recorded addition, but don't assume history
    # before the app's first recorded deposit.
    earliest = next(row["month"] for row, amount in zip(rows, amounts) if amount > 0)
    year, month = map(int, earliest.split("-"))
    tracked_months = current_month - (year * 12 + month) + 1
    return sum(active) / min(months, tracked_months)

def summary():
    """Bank and cash on hand are tracked separately. Spending comes out of the source you picked,
    and cash topped up from the bank lowers the bank. The plan uses average additions, not balances."""
    r = query("""SELECT
        COALESCE(SUM(CASE WHEN a.type='bank' THEN t.amount END), 0) bank_in,
        COALESCE(SUM(CASE WHEN a.type='cash' THEN t.amount END), 0) cash_in,
        COALESCE(SUM(CASE WHEN a.type='cash' AND t.source='bank' THEN t.amount END), 0) withdrawn,
        COALESCE(SUM(CASE WHEN a.type='spending' AND t.source='cash' THEN t.amount END), 0) spent_cash,
        COALESCE(SUM(CASE WHEN a.type='spending' AND t.source='bank' THEN t.amount END), 0) spent_bank,
        COALESCE(SUM(CASE WHEN a.type='spending' AND t.source IS NULL THEN t.amount END), 0) spent_unassigned
        FROM transactions t JOIN accounts a ON a.id=t.account_id""")[0]
    bank = r["bank_in"] - r["withdrawn"] - r["spent_bank"]
    cash = r["cash_in"] - r["spent_cash"]
    base = settings.get("calc_base")
    base = base if base in BASES else "both"
    monthly_added = average_monthly_added(base)
    today = date.today()
    month_start = today.replace(day=1).isoformat()
    next_year, next_month = divmod(today.year * 12 + today.month, 12)
    next_month_start = date(next_year, next_month + 1, 1).isoformat()
    spent_by_bucket = {
        row["bucket_id"]: row["spent"]
        for row in query("""SELECT t.bucket_id, SUM(t.amount) spent
                            FROM transactions t JOIN accounts a ON a.id=t.account_id
                            WHERE a.type='spending' AND t.bucket_id IS NOT NULL
                              AND t.date >= ? AND t.date < ?
                            GROUP BY t.bucket_id""", (month_start, next_month_start))
    }
    bucket_rows = buckets.all()
    allocation = split(monthly_added, bucket_rows)
    for part, bucket in zip(allocation, bucket_rows):
        part["spent"] = spent_by_bucket.get(bucket["id"], 0.0)
        part["remaining"] = max(part["amount"] - part["spent"], 0.0)
        part["over"] = max(part["spent"] - part["amount"], 0.0)
    return {
        "bank": bank, "cash": cash,
        "spent_bank": r["spent_bank"], "spent_cash": r["spent_cash"],
        "spent_unassigned": r["spent_unassigned"],
        "spent": r["spent_bank"] + r["spent_cash"] + r["spent_unassigned"],
        "total": bank + cash - r["spent_unassigned"],
        "base": base, "monthly_added": monthly_added,
        "allocation": allocation,
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