from datetime import date
from core.accounts import accounts, TYPE_LABELS
from core.transactions import transactions
from .crud_tab import CrudTab
from .widgets import money

class TransactionsTab(CrudTab):
    repo = transactions
    fields = [("date", "Date", None, ""), ("account", "Account", [], ""),
              ("amount", "Amount", None, ""), ("note", "Note", None, "")]
    columns = [("date", "Date", 100), ("account", "Account", 170), ("type", "Type", 110),
               ("amount", "Amount", 110), ("note", "Note", 250)]

    def refresh(self):
        self.accts = {f"{a['name']} ({TYPE_LABELS[a['type']]})": a["id"] for a in accounts.all()}
        self.form.set_choices("account", list(self.accts))
        if not self.form.vars["date"].get():
            self.form.vars["date"].set(date.today().isoformat())
        super().refresh()

    def to_record(self, v):
        if v["account"] not in self.accts:
            raise ValueError("Create an account first")
        return {"date": v["date"], "account_id": self.accts[v["account"]], "amount": v["amount"], "note": v["note"]}

    def rows(self):
        return [{**t, "type": TYPE_LABELS[t["type"]], "amount": money(t["amount"])}
                for t in transactions.all()]