from datetime import date
from core.accounts import accounts, TYPE_LABELS
from core.transactions import transactions
from .crud_tab import CrudTab
from .widgets import money

# Per account type: (label for the extra dropdown, {choice shown: value stored})
SOURCE_OPTIONS = {
    "spending": ("Paid from", {"Cash on hand": "cash", "Bank": "bank"}),
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
              ("source", "Paid from", [], ""), ("amount", "Amount", None, ""),
              ("note", "Note", None, "")]
    columns = [("date", "Date", 95), ("account", "Account", 150), ("type", "Type", 100),
               ("from", "From", 140), ("amount", "Amount", 110), ("note", "Note", 190)]

    def __init__(self, master):
        super().__init__(master)
        self.form.vars["account"].trace_add("write", lambda *_: self._sync_source())

    def refresh(self):
        self.accts = {f"{a['name']} ({TYPE_LABELS[a['type']]})": a for a in accounts.all()}
        self.form.set_choices("account", list(self.accts))
        if not self.form.vars["date"].get():
            self.form.vars["date"].set(date.today().isoformat())
        self._sync_source()
        super().refresh()

    def _sync_source(self):
        """The extra dropdown changes meaning with the account type."""
        acct = self.accts.get(self.form.vars["account"].get())
        label, self.options = SOURCE_OPTIONS[acct["type"] if acct else "bank"]
        self.form.set_label("source", label)
        self.form.set_choices("source", list(self.options))

    def to_record(self, v):
        acct = self.accts.get(v["account"])
        if not acct:
            raise ValueError("Create an account first")
        return {"date": v["date"], "account_id": acct["id"], "amount": v["amount"],
                "note": v["note"], "source": self.options.get(v["source"])}

    def rows(self):
        return [{**t, "type": TYPE_LABELS[t["type"]], "from": source_text(t), "amount": money(t["amount"])}
                for t in transactions.all()]