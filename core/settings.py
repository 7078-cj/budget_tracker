"""Tiny key/value store for app preferences (saved in the same SQLite file)."""
from .db import execute, query

DEFAULTS = {"calc_base": "both", "theme": "light"}  # dashboard plan and appearance preferences

def get(key):
    rows = query("SELECT value FROM settings WHERE key=?", (key,))
    return rows[0]["value"] if rows else DEFAULTS[key]

def put(key, value):
    execute("INSERT INTO settings(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value", args=(key, value))