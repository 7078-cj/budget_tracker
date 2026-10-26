"""Base class for any 'form + table + delete' tab. Subclasses supply the specifics."""
from tkinter import ttk
from core import events
from .widgets import Card, Form, Table

class CrudTab(ttk.Frame):
    repo, fields, columns = None, [], []

    def __init__(self, master):
        super().__init__(master)
        top = Card(self)
        top.pack(fill="x", pady=(0, 8))
        self.form = Form(top.body, self.fields, self.submit)
        self.form.pack(fill="x")
        mid = Card(self, pad=8)
        mid.pack(fill="both", expand=True)
        self.table = Table(mid.body, self.columns)
        self.table.pack(fill="both", expand=True)
        ttk.Button(self, text="Delete selected", style="Danger.TButton",
                   command=self.delete).pack(anchor="e", pady=(8, 0))
        events.subscribe(self.refresh)
        self.refresh()

    def to_record(self, values):  # form values -> repo kwargs
        return values

    def rows(self):               # repo data -> display rows
        return self.repo.all()

    def submit(self, values):
        self.repo.add(**self.to_record(values))

    def delete(self):
        id_ = self.table.selected_id()
        if id_:
            self.repo.delete(id_)

    def refresh(self):
        self.table.load(self.rows())