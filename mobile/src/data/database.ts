import type { SQLiteDatabase } from 'expo-sqlite';
import { REST_LABEL } from '../domain/budget';

const DEFAULT_BUCKETS = [
  ['Savings', 20],
  ['Guilt-free', 10],
  ['Investment', 10],
  ['Emergency fund', 10],
] as const;

export async function initializeDatabase(database: SQLiteDatabase): Promise<void> {
  await database.execAsync(`
    PRAGMA foreign_keys = ON;
    CREATE TABLE IF NOT EXISTS accounts (
      id INTEGER PRIMARY KEY,
      name TEXT NOT NULL UNIQUE,
      type TEXT NOT NULL CHECK(type IN ('bank', 'cash', 'spending')),
      is_savings INTEGER NOT NULL DEFAULT 0 CHECK(is_savings IN (0, 1))
    );
    CREATE TABLE IF NOT EXISTS buckets (
      id INTEGER PRIMARY KEY,
      label TEXT NOT NULL UNIQUE,
      percent REAL NOT NULL CHECK(percent BETWEEN 0 AND 100)
    );
    CREATE TABLE IF NOT EXISTS transactions (
      id INTEGER PRIMARY KEY,
      date TEXT NOT NULL,
      account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
      amount REAL NOT NULL,
      note TEXT DEFAULT '',
      source TEXT CHECK(source IN ('bank', 'cash')),
      bucket_id INTEGER REFERENCES buckets(id)
    );
    CREATE TABLE IF NOT EXISTS settings (
      key TEXT PRIMARY KEY,
      value TEXT NOT NULL
    );
  `);

  const accountColumns = await database.getAllAsync<{ name: string }>('PRAGMA table_info(accounts)');
  if (!accountColumns.some((column) => column.name === 'is_savings')) {
    await database.execAsync(
      'ALTER TABLE accounts ADD COLUMN is_savings INTEGER NOT NULL DEFAULT 0 CHECK(is_savings IN (0, 1))',
    );
  }

  const columns = await database.getAllAsync<{ name: string }>('PRAGMA table_info(transactions)');
  const columnNames = new Set(columns.map((column) => column.name));
  if (!columnNames.has('source')) {
    await database.execAsync(
      "ALTER TABLE transactions ADD COLUMN source TEXT CHECK(source IN ('bank', 'cash'))",
    );
  }
  if (!columnNames.has('bucket_id')) {
    await database.execAsync(
      'ALTER TABLE transactions ADD COLUMN bucket_id INTEGER REFERENCES buckets(id)',
    );
  }

  for (const [label, percent] of DEFAULT_BUCKETS) {
    await database.runAsync(
      'INSERT OR IGNORE INTO buckets(label, percent) VALUES (?, ?)',
      label,
      percent,
    );
  }
  const existingNeeds = await database.getFirstAsync<{ id: number }>(
    'SELECT id FROM buckets WHERE label = ?',
    REST_LABEL,
  );
  if (!existingNeeds) {
    const sum = await database.getFirstAsync<{ total: number }>(
      'SELECT COALESCE(SUM(percent), 0) AS total FROM buckets',
    );
    await database.runAsync(
      'INSERT INTO buckets(label, percent) VALUES (?, ?)',
      REST_LABEL,
      Math.max(0, 100 - (sum?.total ?? 0)),
    );
  }
  await database.runAsync(
    "INSERT OR IGNORE INTO settings(key, value) VALUES ('calc_base', 'both')",
  );
}
