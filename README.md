<img width="1116" height="919" alt="image" src="https://github.com/user-attachments/assets/c332d51a-fa0e-408a-acfc-9974e4d0b780" />
<img width="1088" height="907" alt="image" src="https://github.com/user-attachments/assets/0fe42816-ee21-467a-8aee-09374a582136" />
<img width="1101" height="908" alt="image" src="https://github.com/user-attachments/assets/faca3ecf-0118-484a-b03c-075886c5f466" />
<img width="1089" height="901" alt="image" src="https://github.com/user-attachments/assets/e4139371-00e6-4b39-a181-c8c504e3f9c9" />

# Budget Tracker

A small desktop app that tracks your money and tells you how to split it. Add what you have in the bank and in cash, log your spending, and the dashboard shows how much you can spend guilt-free, how much to invest, how much to put in your emergency fund, and how much to keep for bills.

Built with Python, Tkinter and SQLite. There is nothing to install except Python itself.

## Features

- **Three account types:** Bank, Cash on hand, Spending.
- **Money on hand:** calculated for you as `bank + cash on hand - spending`.
- **Your percentages:** use sliders or enter percentages for Savings, Guilt-free, Investment, Emergency fund and Needs & bills. Adjustments keep the total at 100%.
- **Night mode:** switch between light and dark appearance with the sidebar toggle. Your choice is saved locally.
- **Sidebar navigation:** jump between Dashboard, Accounts, Transactions and Allocation % from the left sidebar.
- **Edit records:** select an account or transaction and choose **Edit selected** to load it into the form, update it, or cancel the edit.
- **Dashboard:** current money on hand, separate bank and cash balances, spending totals by payment source (including older spending where the source is unknown), a monthly plan that splits average cash added across savings, guilt-free spending, investment, emergency fund and bills, a cash-flow chart, and recent transactions. The plan averages up to the last six calendar months, excludes spending and bank-to-cash transfers, and counts quiet months after the first recorded addition. The dashboard reflows for narrower windows, scrolls vertically when needed, and refreshes when you change anything.
- **Budget tracking:** choose a budget category for each spending transaction. The dashboard subtracts categorized expenses from that category's monthly allowance and shows how much remains.
- **Emergency fund goal:** shows 3 to 6 months of your average monthly spending as a target.
- **Local data:** everything is stored in one SQLite file on your computer.

## Quick start

Requires Python 3.9 or newer.

```bash
python main.py
```

On Linux you may need Tkinter first: `sudo apt install python3-tk`.

## How to use it

1. **Accounts tab:** create your accounts, for example `BPI` (Bank), `Wallet` (Cash on hand) and `Food` (Spending).
2. **Transactions tab:** record your current money once as a positive amount on a Bank or Cash on hand account. This is your starting balance. After that, add money whenever you receive some, and log expenses on a Spending account. For each new expense, choose its budget category (such as Guilt-free, Savings, Investment, Emergency fund or Needs & bills).
3. **Allocation % tab:** use the sliders or type percentages directly. Changing Needs & bills rebalances the other categories proportionally; changing another category updates the Needs & bills share. Press Enter or leave the field to apply a typed value.
4. **Dashboard tab:** see your monthly plan. Amounts are your percentages applied to average cash added, not your current balance; spending remains reflected in the separate money-on-hand total.
5. Use the left sidebar to switch tabs or toggle night mode. The appearance preference is remembered the next time you open the app.

Amounts are always entered as positive numbers. The account type decides whether money goes in or out. Dates use `YYYY-MM-DD`.

## Project structure

```
main.py                  # entry point
core/                    # data and logic, no UI imports
  events.py              # tiny pub/sub: data layer emits, views refresh
  db.py                  # SQLite connection, schema, upgrade, generic Repository
  accounts.py            # account types (bank, cash, spending)
  transactions.py
  buckets.py             # the percentage buckets
  allocation.py          # pure functions: validate and split
  stats.py               # numbers the dashboard needs
ui/                      # Tkinter views
  theme.py               # colors, fonts, ttk styling
  charts.py              # canvas charts (donut, bars)
  widgets.py             # Form, Table, Card, money()
  crud_tab.py            # base class for form + table + delete tabs
  accounts_tab.py  transactions_tab.py  allocation_tab.py  dashboard_tab.py
  app.py                 # window and navigation
```

Design rules: one generic `Repository` for every table (DRY), and `core/` never imports `ui/` so the logic can be tested without a window.

## Where your data lives

```
Windows:      C:\Users\<you>\.budget_tracker\budget.db
macOS/Linux:  ~/.budget_tracker/budget.db
```

- **Back up:** close the app and copy `budget.db`.
- **Use another file:** set the `BUDGET_DB` environment variable to a path before starting the app.
- **Start fresh:** close the app and delete `budget.db`.

Databases from older versions of this app upgrade automatically the first time you open them. Old `income` and `profit` accounts become Bank accounts, and old `liability` accounts become Spending accounts.

## Build a Windows .exe

You need to build on Windows to get a `.exe`. PyInstaller can't cross-compile, so a Mac builds a Mac app and Linux builds a Linux binary.

1. Open a terminal in the project folder (the one with `main.py`).

2. Install PyInstaller:

   ```bash
   pip install pyinstaller
   ```

3. Build a single-file app with no console window:

   ```bash
   pyinstaller --noconsole --onefile --name BudgetTracker main.py
   ```

4. Your app is at `dist\BudgetTracker.exe`. Copy it anywhere and double-click it. Python is not needed on the other computer, and your data still goes to `.budget_tracker\budget.db` in that user's folder.

### Optional

- **Custom icon:** add `--icon assets\icon.ico` (the file must be a real `.ico`).
- **Faster startup:** `--onefile` unpacks itself on every launch. For quicker starts, drop `--onefile`. You get a `dist\BudgetTracker\` folder to zip and share.
- **Clean up:** `build\`, `dist\` and `BudgetTracker.spec` are build leftovers. Delete them to rebuild from scratch.

### Troubleshooting

- **Antivirus flags the .exe:** single-file PyInstaller builds are sometimes flagged as a false positive. Try the folder build (no `--onefile`), or sign the app if you plan to distribute it.
- **`pyinstaller` is not recognized:** run it as `python -m PyInstaller ...` instead.
- **Window opens and closes right away:** rebuild without `--noconsole` and run the `.exe` from a terminal to see the error message.
- **Missing module errors:** keep the `core\` and `ui\` folders next to `main.py` when building. PyInstaller finds them from the imports.

## Notes and limits

- Spending reduces money on hand from the pool as a whole. Cash-funded spending only reduces cash; bank-funded spending only reduces the bank. Older spending with no known payment source is shown separately and reduces total money on hand without being assigned to either balance. Categorized spending reduces the matching category's remaining amount for the current calendar month; older expenses without a category don't affect category remaining amounts.
- The monthly plan uses recorded bank deposits and cash added from outside the bank. Cash withdrawals from the bank are transfers, not new money. Since the app does not distinguish opening balances from income, a starting balance recorded as a transaction can affect that month's average.
- The 3 to 6 month emergency goal is a common rule of thumb based on the spending you have logged. Adjust to your own situation.
