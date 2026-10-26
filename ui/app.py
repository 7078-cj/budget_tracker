import tkinter as tk
from tkinter import ttk
from core import settings
from . import theme
from .accounts_tab import AccountsTab
from .allocation_tab import AllocationTab
from .dashboard_tab import DashboardTab
from .transactions_tab import TransactionsTab
from .widgets import lbl

TABS = [("Dashboard", DashboardTab), ("Accounts", AccountsTab),
        ("Transactions", TransactionsTab), ("Allocation %", AllocationTab)]

def run():
    root = tk.Tk()
    root.title("Budget Tracker")
    root.geometry("1180x780")
    root.minsize(980, 680)
    mode = settings.get("theme")
    mode = mode if mode in theme.PALETTES else "light"
    theme.apply(root, mode)

    shell = tk.Frame(root, bg=theme.BG)
    shell.pack(fill="both", expand=True)
    sidebar = tk.Frame(shell, bg=theme.CARD, width=220,
                       highlightthickness=1, highlightbackground=theme.BORDER)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)
    content = tk.Frame(shell, bg=theme.BG)
    content.pack(side="left", fill="both", expand=True)

    brand = tk.Frame(sidebar, bg=theme.CARD)
    brand.pack(fill="x", padx=20, pady=(26, 32))
    brand_title = lbl(brand, "Budget Tracker", 16, True, theme.PRIMARY, theme.CARD)
    brand_title.pack(anchor="w")
    brand_subtitle = lbl(brand, "Personal finances", 9, fg=theme.MUTED)
    brand_subtitle.pack(anchor="w", pady=(3, 0))

    nav = tk.Frame(sidebar, bg=theme.CARD)
    nav.pack(fill="x", padx=12)
    header = tk.Frame(content, bg=theme.BG)
    header.pack(fill="x", padx=28, pady=(22, 12))
    page_title = lbl(header, "Dashboard", 18, True, theme.TEXT, theme.BG)
    page_title.pack(side="left")

    stage = ttk.Frame(content)
    stage.pack(fill="both", expand=True, padx=28, pady=(0, 24))
    stage.rowconfigure(0, weight=1)
    stage.columnconfigure(0, weight=1)

    pages, buttons = {}, {}

    def show(name):
        pages[name].tkraise()
        for n, b in buttons.items():
            b.config(bg=theme.PRIMARY if n == name else theme.CARD,
                     fg="white" if n == name else theme.MUTED)
        page_title.config(text=name)

    def toggle_theme():
        nonlocal mode
        mode = "light" if mode == "night" else "night"
        settings.put("theme", mode)
        theme.apply(root, mode)
        shell.config(bg=theme.BG)
        sidebar.config(bg=theme.CARD, highlightbackground=theme.BORDER)
        content.config(bg=theme.BG)
        brand.config(bg=theme.CARD)
        brand_title.config(bg=theme.CARD, fg=theme.PRIMARY)
        brand_subtitle.config(bg=theme.CARD, fg=theme.MUTED)
        header.config(bg=theme.BG)
        page_title.config(bg=theme.BG, fg=theme.TEXT)
        nav.config(bg=theme.CARD)
        theme_button.config(bg=theme.CARD, fg=theme.MUTED,
                            text=f"Night mode: {'On' if mode == 'night' else 'Off'}")
        for name, button in buttons.items():
            button.config(bg=theme.CARD, fg=theme.MUTED)
        for page in pages.values():
            page.refresh()
        show(page_title.cget("text"))

    for name, cls in TABS:
        pages[name] = cls(stage)
        pages[name].grid(row=0, column=0, sticky="nsew")
        b = tk.Label(nav, text=name, anchor="w", font=(theme.FONT, 10, "bold"),
                     padx=14, pady=11, cursor="hand2", bg=theme.CARD, fg=theme.MUTED)
        b.pack(fill="x", pady=2)
        b.bind("<Button-1>", lambda e, n=name: show(n))
        buttons[name] = b

    theme_button = tk.Label(sidebar, text=f"Night mode: {'On' if mode == 'night' else 'Off'}",
                            anchor="w", font=(theme.FONT, 10, "bold"),
                            padx=14, pady=11, cursor="hand2",
                            bg=theme.CARD, fg=theme.MUTED)
    theme_button.pack(side="bottom", fill="x", padx=12, pady=18)
    theme_button.bind("<Button-1>", lambda _event: toggle_theme())

    show(TABS[0][0])
    root.mainloop()