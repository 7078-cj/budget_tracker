from .db import Repository, query

TYPE_LABELS = {"bank": "Bank", "cash": "Cash on hand", "spending": "Spending"}
TYPES = tuple(TYPE_LABELS)

class AccountRepo(Repository):
    table, columns = "accounts", ("name", "type")

    def add(self, **v):
        self._validate(v)
        return super().add(**v)

    def update(self, id_, **v):
        self._validate(v)
        current = query("SELECT type FROM accounts WHERE id=?", (id_,))
        if not current:
            raise ValueError("Account no longer exists")
        if v["type"] != current[0]["type"] and query(
                "SELECT id FROM transactions WHERE account_id=? LIMIT 1", (id_,)):
            raise ValueError("Can't change an account type after it has transactions")
        super().update(id_, **v)

    @staticmethod
    def _validate(v):
        v["name"] = v["name"].strip()
        if not v["name"]:
            raise ValueError("Account name is required")
        if v["type"] not in TYPES:
            raise ValueError(f"Type must be one of: {', '.join(TYPES)}")

    def with_balances(self):
        return query("""SELECT a.*, COALESCE(SUM(t.amount),0) balance FROM accounts a
                        LEFT JOIN transactions t ON t.account_id=a.id
                        GROUP BY a.id ORDER BY a.type, a.name""")

accounts = AccountRepo()