import tkinter as tk
from tkinter import ttk, messagebox
from core import events
from core.buckets import buckets
from .theme import BAD, CARD, MUTED, PALETTE, PRIMARY_DK
from .widgets import Card, lbl

BAR_W = 360

class AllocationTab(ttk.Frame):
    """Set what % of every peso of income goes to each bucket."""
    def __init__(self, master):
        super().__init__(master)
        self.vars = {}
        events.subscribe(self.refresh)
        self.refresh()

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        card = Card(self, pad=24)
        card.pack(anchor="nw")
        b = card.body
        lbl(b, "Income allocation", 14, True).grid(row=0, column=0, columnspan=3, sticky="w")
        lbl(b, "Set each percentage. Your allocations must add up to 100%.", 10, fg=MUTED)\
            .grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 14))
        self.vars = {}
        for i, x in enumerate(buckets.all(), start=2):
            lbl(b, x["label"]).grid(row=i, column=0, sticky="w", pady=6)
            v = self.vars[x["id"]] = tk.StringVar(value=f"{x['percent']:g}")
            v.trace_add("write", lambda *_: self._update())
            ttk.Entry(b, textvariable=v, width=7, justify="right").grid(row=i, column=1, padx=8)
            lbl(b, "%", fg=MUTED).grid(row=i, column=2, sticky="w")
        n = len(self.vars) + 2
        self.bar = tk.Canvas(b, width=BAR_W, height=14, bg=CARD, highlightthickness=0)
        self.bar.grid(row=n, column=0, columnspan=3, sticky="w", pady=(14, 4))
        self.total = lbl(b, "", 10, True)
        self.total.grid(row=n + 1, column=0, columnspan=3, sticky="w")
        ttk.Button(b, text="Save", style="Primary.TButton", command=self.save)\
            .grid(row=n + 2, column=0, columnspan=3, sticky="w", pady=(14, 0))
        self._update()

    def _percents(self):
        return {i: float(v.get() or 0) for i, v in self.vars.items()}

    def _update(self):
        self.bar.delete("all")
        try:
            vals = list(self._percents().values())
        except ValueError:
            self.total.config(text="Enter numbers only", fg=BAD)
            return
        t = sum(vals)
        x = 0
        for i, p in enumerate(vals):
            w = BAR_W * max(p, 0) / 100
            self.bar.create_rectangle(x, 0, min(x + w, BAR_W), 14, fill=PALETTE[i % len(PALETTE)], width=0)
            x += w
        if t < 99.9999:
            text, color = f"Allocated {t:g}%  ·  {100 - t:g}% remaining", BAD
        elif t > 100.0001:
            text, color = f"Allocated {t:g}%  ·  {t - 100:g}% over", BAD
        else:
            text, color = "Total allocation 100%", PRIMARY_DK
        self.total.config(text=text, fg=color)

    def save(self):
        try:
            buckets.save_percents(self._percents())
        except ValueError as e:
            messagebox.showerror("Can't save", str(e))