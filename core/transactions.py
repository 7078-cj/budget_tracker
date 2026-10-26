from datetime import date
from .db import Repository, query

class TransactionRepo(Repository):
    table, columns = "transactions", ("date", "account_id", "amount", "note")

    def all(self, order="t.date DESC, t.id DESC"):
        return query("SELECT t.*, a.name account, a.type type FROM transactions t "
                     f"JOIN accounts a ON a.id=t.account_id ORDER BY {order}")

    def add(self, **v):
        date.fromisoformat(v["date"])  # raises ValueError on bad format (use YYYY-MM-DD)
        v["amount"] = float(v["amount"])
        if v["amount"] <= 0:
            raise ValueError("Amount must be greater than 0")
        return super().add(**v)

transactions = TransactionRepo()
