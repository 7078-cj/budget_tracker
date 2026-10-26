from datetime import date
from .db import Repository, query

class TransactionRepo(Repository):
    """`source` means: spending -> paid from 'cash' or 'bank'; cash account -> 'bank' if the
    money was withdrawn from the bank (so the bank goes down); bank account -> None."""
    table, columns = "transactions", ("date", "account_id", "amount", "note", "source")

    def all(self, order="t.date DESC, t.id DESC"):
        return query("SELECT t.*, a.name account, a.type type FROM transactions t "
                     f"JOIN accounts a ON a.id=t.account_id ORDER BY {order}")

    def add(self, **v):
        v.setdefault("source", None)
        date.fromisoformat(v["date"])  # raises ValueError on bad format (use YYYY-MM-DD)
        v["amount"] = float(v["amount"])
        if v["amount"] <= 0:
            raise ValueError("Amount must be greater than 0")
        rows = query("SELECT type FROM accounts WHERE id=?", (v["account_id"],))
        if not rows:
            raise ValueError("Pick an account")
        kind, src = rows[0]["type"], v["source"]
        if kind == "spending" and src not in ("cash", "bank"):
            raise ValueError("Choose whether this was paid from cash on hand or the bank")
        if kind == "cash" and src not in (None, "bank"):
            raise ValueError("Cash on hand can only be topped up from the bank or from elsewhere")
        if kind == "bank" and src is not None:
            raise ValueError("A bank deposit has no source")
        return super().add(**v)

transactions = TransactionRepo()