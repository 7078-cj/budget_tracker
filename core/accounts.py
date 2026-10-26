from .db import Repository, query

TYPE_LABELS = {"bank": "Bank", "cash": "Cash on hand", "spending": "Spending"}
TYPES = tuple(TYPE_LABELS)

class AccountRepo(Repository):
    table, columns = "accounts", ("name", "type")

    def add(self, **v):
        if not v["name"]:
            raise ValueError("Account name is required")
        if v["type"] not in TYPES:
            raise ValueError(f"Type must be one of: {', '.join(TYPES)}")
        return super().add(**v)

    def with_balances(self):
        return query("""SELECT a.*, COALESCE(SUM(t.amount),0) balance FROM accounts a
                        LEFT JOIN transactions t ON t.account_id=a.id
                        GROUP BY a.id ORDER BY a.type, a.name""")

accounts = AccountRepo()