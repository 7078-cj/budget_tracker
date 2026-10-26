from datetime import date
from .db import Repository, query

class TransactionRepo(Repository):
    """`source` means: spending -> paid from 'cash' or 'bank'; cash account -> 'bank' if the
    money was withdrawn from the bank (so the bank goes down); bank account -> None."""
    table, columns = "transactions", ("date", "account_id", "amount", "note", "source", "bucket_id")

    def all(self, order="t.date DESC, t.id DESC"):
        return query("SELECT t.*, a.name account, a.type type, b.label budget "
                     "FROM transactions t JOIN accounts a ON a.id=t.account_id "
                     "LEFT JOIN buckets b ON b.id=t.bucket_id "
                     f"ORDER BY {order}")

    def add(self, **v):
        self._validate(v)
        return super().add(**v)

    def update(self, id_, **v):
        self._validate(v)
        super().update(id_, **v)

    @staticmethod
    def _validate(v):
        v.setdefault("source", None)
        v.setdefault("bucket_id", None)
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
        bucket_id = v.get("bucket_id")
        if kind == "spending":
            if bucket_id is None:
                raise ValueError("Choose a budget category for this spending transaction")
            if not query("SELECT id FROM buckets WHERE id=?", (bucket_id,)):
                raise ValueError("Choose a valid budget category")
        elif bucket_id is not None:
            raise ValueError("Only spending transactions can have a budget category")
        if kind == "cash" and src not in (None, "bank"):
            raise ValueError("Cash on hand can only be topped up from the bank or from elsewhere")
        if kind == "bank" and src is not None:
            raise ValueError("A bank deposit has no source")
        v["bucket_id"] = bucket_id

transactions = TransactionRepo()