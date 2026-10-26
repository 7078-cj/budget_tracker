import tkinter as tk
from tkinter import ttk
from . import theme
from .accounts_tab import AccountsTab
from .allocation_tab import AllocationTab
from .dashboard_tab import DashboardTab
from .theme import BG, CARD, BORDER, FONT, MUTED, PRIMARY
from .transactions_tab import TransactionsTab
from .widgets import lbl

TABS = [("Dashboard", DashboardTab), ("Accounts", AccountsTab),
        ("Transactions", TransactionsTab), ("Allocation %", AllocationTab)]

def run():
    root = tk.Tk()
    root.title("Budget Tracker")
    root.geometry("1100x780")
    root.minsize(980, 880)
    theme.apply(root)

    header = tk.Frame(root, bg=BG)
    header.pack(fill="x", padx=24, pady=(18, 10))
    lbl(header, "Budget Tracker", 16, True, PRIMARY, BG).pack(side="left")
    pills = tk.Frame(header, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
    pills.pack(side="right")

    stage = ttk.Frame(root)
    stage.pack(fill="both", expand=True, padx=24, pady=(0, 20))
    stage.rowconfigure(0, weight=1)
    stage.columnconfigure(0, weight=1)

    pages, buttons = {}, {}

    def show(name):
        pages[name].tkraise()
        for n, b in buttons.items():
            b.config(bg=PRIMARY if n == name else CARD, fg="white" if n == name else MUTED)

    for name, cls in TABS:
        pages[name] = cls(stage)
        pages[name].grid(row=0, column=0, sticky="nsew")
        b = tk.Label(pills, text=name, font=(FONT, 10, "bold"), padx=16, pady=7, cursor="hand2")
        b.pack(side="left", padx=3, pady=3)
        b.bind("<Button-1>", lambda e, n=name: show(n))
        buttons[name] = b

    show(TABS[0][0])
    root.mainloop()