from datetime import date
from core.accounts import accounts, TYPE_LABELS
from core.buckets import buckets
from core.transactions import transactions
from .crud_tab import CrudTab
from .widgets import money

# Per account type: (label for the extra dropdown, {choice shown: value stored})
SOURCE_OPTIONS = {
    "spending": ("Paid from", {
        "Choose payment source": None,
        "Cash on hand": "cash",
        "Bank": "bank",
    }),
    "cash": ("Take from bank?", {"No": None, "Yes, deduct from bank": "bank"}),
    "bank": ("Paid from", {"Not needed": None}),
}

def source_text(t):
    if t["type"] == "spending":
        return {"cash": "Cash on hand", "bank": "Bank"}.get(t["source"], "")
    if t["type"] == "cash" and t["source"] == "bank":
        return "Withdrawn from bank"
    return ""

class TransactionsTab(CrudTab):
    repo = transactions
    fields = [("date", "Date", None, ""), ("account", "Account", [], ""),
              ("source", "Paid from", [], ""), ("budget", "Budget category", [], ""),
              ("amount", "Amount", None, ""),
              ("note", "Note", None, "")]
    columns = [("date", "Date", 95), ("account", "Account", 150), ("type", "Type", 100),
               ("from", "From", 120), ("budget", "Budget category", 140),
               ("amount", "Amount", 110), ("note", "Note", 190)]

    def __init__(self, master):
        super().__init__(master)
        self.form.vars["account"].trace_add("write", lambda *_: self._sync_source())
        self.form.vars["account"].trace_add("write", lambda *_: self._sync_budget(reset=True))

    def refresh(self):
        self.accts = {f"{a['name']} ({TYPE_LABELS[a['type']]})": a for a in accounts.all()}
        self.bucket_by_label = {b["label"]: b["id"] for b in buckets.all()}
        self.form.set_choices("account", list(self.accts))
        if not self.form.vars["date"].get():
            self.form.vars["date"].set(date.today().isoformat())
        self._sync_source()
        self._sync_budget()
        super().refresh()

    def _sync_source(self):
        """The extra dropdown changes meaning with the account type."""
        acct = self.accts.get(self.form.vars["account"].get())
        label, self.options = SOURCE_OPTIONS[acct["type"] if acct else "bank"]
        self.form.set_label("source", label)
        self.form.set_choices("source", list(self.options))

    def _sync_budget(self, reset=False):
        if not hasattr(self, "bucket_by_label"):
            return
        acct = self.accts.get(self.form.vars["account"].get())
        is_spending = acct is not None and acct["type"] == "spending"
        choices = ["Choose category", *self.bucket_by_label] if is_spending else ["Not applicable"]
        self.form.set_label("budget", "Budget category" if is_spending else "Budget category (spending only)")
        self.form.set_choices("budget", choices)
        if reset or not is_spending:
            self.form.vars["budget"].set(choices[0])
        self.form.widgets["budget"].configure(state="readonly" if is_spending else "disabled")

    def to_record(self, v):
        acct = self.accts.get(v["account"])
        if not acct:
            raise ValueError("Create an account first")
        bucket_id = None
        if acct["type"] == "spending":
            bucket_id = self.bucket_by_label.get(v["budget"])
            if bucket_id is None:
                raise ValueError("Choose a budget category for this spending transaction")
        return {"date": v["date"], "account_id": acct["id"], "amount": v["amount"],
                "note": v["note"], "source": self.options.get(v["source"]),
                "bucket_id": bucket_id}

    def form_values_for(self, row):
        source = source_text(row)
        if not source:
            source = "Yes, deduct from bank" if row["type"] == "cash" and row["source"] == "bank" else (
                "No" if row["type"] == "cash" else
                "Choose payment source" if row["type"] == "spending" else "Not needed")
        return {
            "date": row["date"],
            "account": f"{row['account']} ({TYPE_LABELS[row['type']]})",
            "source": source,
            "budget": row["budget"] or "Choose category" if row["type"] == "spending" else "Not applicable",
            "amount": str(row["amount"]),
            "note": row["note"] or "",
        }

    def rows(self):
        return [{**t, "type": TYPE_LABELS[t["type"]], "from": source_text(t),
                 "budget": t["budget"] or "—", "amount": money(t["amount"])}
                for t in transactions.all()]