import tkinter as tk
from tkinter import ttk, messagebox
import math
from core import events
from core.buckets import buckets
from core.allocation import REST_LABEL
from . import theme
from .widgets import Card, GlassSlider, lbl

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
        self._updating_sliders = False
        self.needs_id = None
        self.vars = {}
        self.value_labels = {}
        self.scales = {}
        self.entry_vars = {}
        self.entries = {}
        card = Card(self, pad=24)
        card.pack(anchor="nw")
        b = card.body
        lbl(b, "Income allocation", 14, True).grid(row=0, column=0, columnspan=3, sticky="w")
        lbl(b, "Use the sliders or type a percentage. Needs & bills adjusts to keep the total at 100%.",
            10, fg=theme.MUTED).grid(row=1, column=0, columnspan=4, sticky="w", pady=(0, 14))
        for i, x in enumerate(buckets.all(), start=2):
            bucket_id = x["id"]
            if x["label"] == REST_LABEL:
                self.needs_id = bucket_id
            v = self.vars[bucket_id] = tk.DoubleVar(value=x["percent"])
            lbl(b, x["label"], 10, True).grid(row=i, column=0, sticky="w", pady=7, padx=(0, 12))
            scale = self.scales[bucket_id] = GlassSlider(
                b, x["percent"], lambda value, key=bucket_id: self._slider_changed(key, value))
            scale.grid(row=i, column=1, sticky="ew", padx=8)
            value_label = self.value_labels[bucket_id] = lbl(
                b, f"{x['percent']:g}%", 10, True, theme.PRIMARY_DK, theme.PRIMARY_LT)
            value_label.grid(row=i, column=2, sticky="e", padx=(8, 0))
            value_label.config(padx=9, pady=4)
            entry_var = self.entry_vars[bucket_id] = tk.StringVar(value=f"{x['percent']:g}")
            entry = self.entries[bucket_id] = ttk.Entry(
                b, textvariable=entry_var, width=7, justify="right")
            entry.grid(row=i, column=3, sticky="e", padx=(8, 0))
            entry_var.trace_add("write", lambda *_args, key=bucket_id: self._entry_changed(key))
            entry.bind("<Return>", lambda _event, key=bucket_id: self._commit_entry(key, show_error=True))
            entry.bind("<FocusOut>", lambda _event, key=bucket_id: self._commit_entry(key))
        b.columnconfigure(1, weight=1)
        n = len(self.vars) + 2
        self.bar = tk.Canvas(b, width=BAR_W, height=14, bg=theme.CARD, highlightthickness=0)
        self.bar.grid(row=n, column=0, columnspan=4, sticky="w", pady=(14, 4))
        self.total = lbl(b, "", 10, True)
        self.total.grid(row=n + 1, column=0, columnspan=4, sticky="w")
        self.save_button = ttk.Button(b, text="Save", style="Primary.TButton", command=self.save)
        self.save_button.grid(row=n + 2, column=0, columnspan=4, sticky="w", pady=(14, 0))
        self._update()

    def _percents(self):
        return {i: v.get() for i, v in self.vars.items()}

    def _slider_changed(self, bucket_id, raw_value):
        if self._updating_sliders:
            return

        percents = self._percents()
        value = round(float(raw_value), 1)
        other_ids = [i for i in self.vars if i != self.needs_id]

        if bucket_id == self.needs_id:
            target = 100 - value
            other_total = sum(percents[i] for i in other_ids)
            if other_total:
                adjusted = [round(percents[i] * target / other_total, 1) for i in other_ids]
            elif other_ids:
                adjusted = [round(target / len(other_ids), 1) for _ in other_ids]
            else:
                adjusted = []
            if adjusted:
                adjusted[-1] = target - sum(adjusted[:-1])
            percents[self.needs_id] = value
            percents.update(zip(other_ids, adjusted))
        else:
            fixed_total = sum(percents[i] for i in other_ids if i != bucket_id)
            value = min(value, max(0, 100 - fixed_total))
            percents[bucket_id] = value
            percents[self.needs_id] = 100 - sum(
                percents[i] for i in other_ids)

        self._updating_sliders = True
        try:
            for key, percent in percents.items():
                self.vars[key].set(percent)
                self.scales[key].set(percent)
                self.value_labels[key].config(text=f"{percent:g}%")
                self.entry_vars[key].set(f"{percent:g}")
        finally:
            self._updating_sliders = False
        self._update()

    def _entry_changed(self, bucket_id):
        if self._updating_sliders:
            return
        self._update()

    def _commit_entry(self, bucket_id, show_error=False):
        if self._updating_sliders:
            return
        text = self.entry_vars[bucket_id].get().strip()
        try:
            value = float(text)
            if not math.isfinite(value) or not 0 <= value <= 100:
                raise ValueError
        except ValueError:
            if show_error:
                messagebox.showerror("Invalid percentage", "Enter a number from 0 to 100.")
                return "break"
            return
        self._slider_changed(bucket_id, value)
        return "break" if show_error else None

    def _update(self):
        self.bar.delete("all")
        try:
            vals = list(self._percents().values())
        except ValueError:
            self.total.config(text="Enter numbers only", fg=theme.BAD)
            return
        t = sum(vals)
        x = 0
        for i, p in enumerate(vals):
            w = BAR_W * max(p, 0) / 100
            self.bar.create_rectangle(x, 0, min(x + w, BAR_W), 14,
                                      fill=theme.PALETTE[i % len(theme.PALETTE)], width=0)
            x += w
        if t < 99.9999:
            text, color = f"Allocated {t:g}%  ·  {100 - t:g}% remaining", theme.BAD
        elif t > 100.0001:
            text, color = f"Allocated {t:g}%  ·  {t - 100:g}% over", theme.BAD
        else:
            text, color = "Total allocation 100%", theme.PRIMARY_DK
        self.total.config(text=text, fg=color)
        pending = False
        invalid = False
        for key, entry_var in self.entry_vars.items():
            try:
                value = float(entry_var.get().strip())
                if not math.isfinite(value) or not 0 <= value <= 100:
                    invalid = True
                    break
                pending = pending or abs(value - self.vars[key].get()) > 0.0001
            except ValueError:
                invalid = True
                break
        if invalid:
            self.total.config(text="Enter a percentage from 0 to 100", fg=theme.BAD)
            self.save_button.state(["disabled"])
        elif pending:
            self.total.config(text="Press Enter or leave the field to apply your change",
                              fg=theme.MUTED)
            self.save_button.state(["disabled"])
        else:
            self.save_button.state(["!disabled"])

    def save(self):
        try:
            buckets.save_percents(self._percents())
        except ValueError as e:
            messagebox.showerror("Can't save", str(e))