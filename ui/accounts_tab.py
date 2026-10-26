from core.accounts import accounts, TYPE_LABELS
from .crud_tab import CrudTab
from .widgets import money

BY_LABEL = {label: key for key, label in TYPE_LABELS.items()}

class AccountsTab(CrudTab):
    repo = accounts
    fields = [("name", "Name", None, ""), ("type", "Type", list(BY_LABEL), "Bank")]
    columns = [("name", "Name", 220), ("type", "Type", 130), ("balance", "Total recorded", 140)]

    def to_record(self, v):
        return {"name": v["name"], "type": BY_LABEL[v["type"]]}

    def form_values_for(self, row):
        return {"name": row["name"], "type": TYPE_LABELS[row["type"]]}

    def rows(self):
        return [{**a, "type": TYPE_LABELS[a["type"]], "balance": money(a["balance"])}
                for a in accounts.with_balances()]