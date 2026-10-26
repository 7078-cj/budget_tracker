"""Base class for any 'form + table + edit + delete' tab."""
from tkinter import messagebox, ttk
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
        actions = ttk.Frame(self)
        actions.pack(anchor="e", pady=(8, 0))
        self.edit_button = ttk.Button(actions, text="Edit selected",
                                      command=self.edit_selected)
        self.edit_button.pack(side="left", padx=(0, 8))
        self.cancel_button = ttk.Button(actions, text="Cancel edit",
                                        command=self.cancel_edit, state="disabled")
        self.cancel_button.pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Delete selected", style="Danger.TButton",
                   command=self.delete).pack(side="left")
        self.editing_id = None
        events.subscribe(self.refresh)
        self.refresh()

    def to_record(self, values):  # form values -> repo kwargs
        return values

    def form_values_for(self, row):
        return {key: str(row.get(key, "")) for key, *_ in self.fields}

    def rows(self):               # repo data -> display rows
        return self.repo.all()

    def submit(self, values):
        record = self.to_record(values)
        if self.editing_id is None:
            self.repo.add(**record)
        else:
            self.repo.update(self.editing_id, **record)
            self.cancel_edit()

    def edit_selected(self):
        id_ = self.table.selected_id()
        if id_ is None:
            messagebox.showinfo("Select a row", "Select a row to edit.")
            return
        row = next((item for item in self.repo.all() if item["id"] == id_), None)
        if row is None:
            messagebox.showerror("Can't edit", "The selected item no longer exists.")
            self.refresh()
            return
        self.editing_id = id_
        for key, value in self.form_values_for(row).items():
            self.form.vars[key].set(value)
        self.form.button.configure(text="Update")
        self.edit_button.configure(text="Update selected")
        self.cancel_button.state(["!disabled"])

    def cancel_edit(self):
        self.editing_id = None
        self.form.button.configure(text="Add")
        self.edit_button.configure(text="Edit selected")
        self.cancel_button.state(["disabled"])

    def delete(self):
        id_ = self.table.selected_id()
        if id_:
            self.repo.delete(id_)
            if id_ == self.editing_id:
                self.cancel_edit()

    def refresh(self):
        self.table.load(self.rows())