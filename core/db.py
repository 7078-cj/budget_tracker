"""SQLite connection, schema, and the one generic Repository every table reuses."""
import os
import sqlite3
from pathlib import Path
from . import events

DB_PATH = Path(os.environ.get("BUDGET_DB", Path.home() / ".budget_tracker" / "budget.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts(
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  type TEXT NOT NULL CHECK(type IN ('bank','cash','spending')));
CREATE TABLE IF NOT EXISTS transactions(
  id INTEGER PRIMARY KEY,
  date TEXT NOT NULL,
  account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
  amount REAL NOT NULL,
  note TEXT DEFAULT '');
CREATE TABLE IF NOT EXISTS buckets(
  id INTEGER PRIMARY KEY,
  label TEXT NOT NULL UNIQUE,
  percent REAL NOT NULL CHECK(percent BETWEEN 0 AND 100));
"""
DEFAULT_BUCKETS = [("Savings", 20), ("Guilt-free", 10), ("Investment", 10), ("Emergency fund", 10)]

LEGACY_TYPES = ("CASE type WHEN 'income' THEN 'bank' WHEN 'profit' THEN 'bank' "
                "WHEN 'liability' THEN 'spending' ELSE type END")

def _migrate_accounts(conn):
    """Old databases had income/profit/liability accounts: fold them into bank/cash/spending."""
    sql = conn.execute("SELECT sql FROM sqlite_master WHERE name='accounts'").fetchone()["sql"]
    if "'income'" not in sql:
        return
    conn.execute("PRAGMA foreign_keys=OFF")  # or dropping the old table would cascade-delete transactions
    conn.executescript(f"""
        BEGIN;
        CREATE TABLE accounts_new(id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE,
          type TEXT NOT NULL CHECK(type IN ('bank','cash','spending')));
        INSERT INTO accounts_new SELECT id, name, {LEGACY_TYPES} FROM accounts;
        DROP TABLE accounts;
        ALTER TABLE accounts_new RENAME TO accounts;
        COMMIT;""")
    conn.execute("PRAGMA foreign_keys=ON")

_conn = None

def get_conn():
    global _conn
    if _conn is None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(DB_PATH)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA foreign_keys=ON")
        _conn.executescript(SCHEMA)
        _migrate_accounts(_conn)
        _conn.executemany("INSERT OR IGNORE INTO buckets(label, percent) VALUES(?,?)", DEFAULT_BUCKETS)
        _conn.commit()
    return _conn

def query(sql, args=()):
    return [dict(r) for r in get_conn().execute(sql, args).fetchall()]

def execute(sql, rows=None, args=()):
    """Run a write, commit, and notify subscribers once. `rows` => executemany."""
    conn = get_conn()
    cur = conn.executemany(sql, rows) if rows is not None else conn.execute(sql, args)
    conn.commit()
    events.emit()
    return cur.lastrowid

class Repository:
    table = ""
    columns = ()

    def all(self, order="id"):
        return query(f"SELECT * FROM {self.table} ORDER BY {order}")

    def add(self, **v):
        marks = ",".join("?" * len(self.columns))
        return execute(f"INSERT INTO {self.table}({','.join(self.columns)}) VALUES({marks})",
                       args=[v[c] for c in self.columns])

    def update(self, id_, **v):
        sets = ",".join(f"{c}=?" for c in v)
        execute(f"UPDATE {self.table} SET {sets} WHERE id=?", args=[*v.values(), id_])

    def delete(self, id_):
        execute(f"DELETE FROM {self.table} WHERE id=?", args=[id_])