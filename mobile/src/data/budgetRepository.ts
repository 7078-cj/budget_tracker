import type { SQLiteDatabase } from 'expo-sqlite';
import {
  averageMonthlyAdded,
  calculateAllocations,
  calculateBalances,
  validateAccount,
  validatePercentages,
  validateTransaction,
} from '../domain/budget';
import type {
  Account,
  AccountInput,
  AccountType,
  Allocation,
  Bucket,
  CalculationBase,
  DashboardSummary,
  Transaction,
  TransactionInput,
} from '../domain/types';

export async function getAccounts(database: SQLiteDatabase): Promise<Account[]> {
  return database.getAllAsync<Account>('SELECT id, name, type FROM accounts ORDER BY name');
}

export async function saveAccount(
  database: SQLiteDatabase,
  input: AccountInput,
  id?: number,
): Promise<void> {
  const name = validateAccount(input.name, input.type);
  if (id === undefined) {
    await database.runAsync('INSERT INTO accounts(name, type) VALUES (?, ?)', name, input.type);
    return;
  }
  const current = await database.getFirstAsync<{ type: AccountType }>(
    'SELECT type FROM accounts WHERE id = ?',
    id,
  );
  if (!current) throw new Error('Account no longer exists.');
  if (current.type !== input.type) {
    const used = await database.getFirstAsync<{ id: number }>(
      'SELECT id FROM transactions WHERE account_id = ? LIMIT 1',
      id,
    );
    if (used) throw new Error('Account type cannot change after transactions are recorded.');
  }
  await database.runAsync('UPDATE accounts SET name = ?, type = ? WHERE id = ?', name, input.type, id);
}

export async function deleteAccount(database: SQLiteDatabase, id: number): Promise<void> {
  await database.runAsync('DELETE FROM accounts WHERE id = ?', id);
}

export async function getBuckets(database: SQLiteDatabase): Promise<Bucket[]> {
  return database.getAllAsync<Bucket>('SELECT id, label, percent FROM buckets ORDER BY id');
}

export async function savePercentages(
  database: SQLiteDatabase,
  percentages: { id: number; percent: number }[],
): Promise<void> {
  validatePercentages(percentages.map(({ percent }) => percent));
  await database.withTransactionAsync(async () => {
    for (const { id, percent } of percentages) {
      await database.runAsync('UPDATE buckets SET percent = ? WHERE id = ?', percent, id);
    }
  });
}

export async function getTransactions(database: SQLiteDatabase): Promise<Transaction[]> {
  return database.getAllAsync<Transaction>(`
    SELECT t.id, t.date, t.account_id, a.name AS account, a.type,
           t.amount, t.note, t.source, t.bucket_id, b.label AS budget
    FROM transactions t
    JOIN accounts a ON a.id = t.account_id
    LEFT JOIN buckets b ON b.id = t.bucket_id
    ORDER BY t.date DESC, t.id DESC
  `);
}

export async function saveTransaction(
  database: SQLiteDatabase,
  input: TransactionInput,
  id?: number,
): Promise<void> {
  const account = await database.getFirstAsync<{ type: AccountType }>(
    'SELECT type FROM accounts WHERE id = ?',
    input.accountId,
  );
  if (!account) throw new Error('Select an account.');
  validateTransaction({
    date: input.date,
    amount: input.amount,
    accountType: account.type,
    source: input.source,
    bucketId: input.bucketId,
  });
  if (input.bucketId !== null) {
    const bucket = await database.getFirstAsync<{ id: number }>(
      'SELECT id FROM buckets WHERE id = ?',
      input.bucketId,
    );
    if (!bucket) throw new Error('Select a valid budget category.');
  }

  const values = [
    input.date,
    input.accountId,
    input.amount,
    input.note.trim(),
    input.source,
    input.bucketId,
  ] as const;
  if (id === undefined) {
    await database.runAsync(
      `INSERT INTO transactions(date, account_id, amount, note, source, bucket_id)
       VALUES (?, ?, ?, ?, ?, ?)`,
      ...values,
    );
  } else {
    await database.runAsync(
      `UPDATE transactions
       SET date = ?, account_id = ?, amount = ?, note = ?, source = ?, bucket_id = ?
       WHERE id = ?`,
      ...values,
      id,
    );
  }
}

export async function deleteTransaction(database: SQLiteDatabase, id: number): Promise<void> {
  await database.runAsync('DELETE FROM transactions WHERE id = ?', id);
}

export async function getCalculationBase(database: SQLiteDatabase): Promise<CalculationBase> {
  const setting = await database.getFirstAsync<{ value: string }>(
    "SELECT value FROM settings WHERE key = 'calc_base'",
  );
  return setting?.value === 'bank' || setting?.value === 'cash' ? setting.value : 'both';
}

export async function setCalculationBase(
  database: SQLiteDatabase,
  base: CalculationBase,
): Promise<void> {
  await database.runAsync(
    "INSERT INTO settings(key, value) VALUES ('calc_base', ?) " +
      'ON CONFLICT(key) DO UPDATE SET value = excluded.value',
    base,
  );
}

export async function getDashboardSummary(
  database: SQLiteDatabase,
  base: CalculationBase,
): Promise<DashboardSummary> {
  const totals = await database.getFirstAsync<{
    bankIn: number;
    cashIn: number;
    withdrawn: number;
    spentCash: number;
    spentBank: number;
    spentUnknown: number;
  }>(`
    SELECT
      COALESCE(SUM(CASE WHEN a.type = 'bank' THEN t.amount END), 0) AS bankIn,
      COALESCE(SUM(CASE WHEN a.type = 'cash' THEN t.amount END), 0) AS cashIn,
      COALESCE(SUM(CASE WHEN a.type = 'cash' AND t.source = 'bank' THEN t.amount END), 0) AS withdrawn,
      COALESCE(SUM(CASE WHEN a.type = 'spending' AND t.source = 'cash' THEN t.amount END), 0) AS spentCash,
      COALESCE(SUM(CASE WHEN a.type = 'spending' AND t.source = 'bank' THEN t.amount END), 0) AS spentBank,
      COALESCE(SUM(CASE WHEN a.type = 'spending' AND t.source IS NULL THEN t.amount END), 0) AS spentUnknown
    FROM transactions t JOIN accounts a ON a.id = t.account_id
  `);
  const balances = calculateBalances({
    bankIn: totals?.bankIn ?? 0,
    cashIn: totals?.cashIn ?? 0,
    withdrawn: totals?.withdrawn ?? 0,
    spentCash: totals?.spentCash ?? 0,
    spentBank: totals?.spentBank ?? 0,
    spentUnknown: totals?.spentUnknown ?? 0,
  });
  const today = new Date();
  const startMonthDate = new Date(today.getFullYear(), today.getMonth() - 5, 1);
  const endMonth = new Date(today.getFullYear(), today.getMonth() + 1, 1);
  const isoMonth = (date: Date) =>
    `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
  const monthlyRows = await database.getAllAsync<{
    month: string;
    bankAdded: number;
    cashAdded: number;
  }>(
    `SELECT substr(t.date, 1, 7) AS month,
            SUM(CASE WHEN a.type = 'bank' THEN t.amount ELSE 0 END) AS bankAdded,
            SUM(CASE WHEN a.type = 'cash' AND IFNULL(t.source, '') != 'bank'
                     THEN t.amount ELSE 0 END) AS cashAdded
     FROM transactions t JOIN accounts a ON a.id = t.account_id
     WHERE t.date >= ? AND t.date < ? AND a.type IN ('bank', 'cash')
     GROUP BY month ORDER BY month`,
    `${isoMonth(startMonthDate)}-01`,
    `${isoMonth(endMonth)}-01`,
  );
  const monthlyAdded = averageMonthlyAdded(monthlyRows, base, today);

  const buckets = await getBuckets(database);
  const monthStart = `${isoMonth(new Date(today.getFullYear(), today.getMonth(), 1))}-01`;
  const nextMonth = `${isoMonth(endMonth)}-01`;
  const spending = await database.getAllAsync<{ bucket_id: number; spent: number }>(
    `SELECT t.bucket_id, SUM(t.amount) AS spent
     FROM transactions t JOIN accounts a ON a.id = t.account_id
     WHERE a.type = 'spending' AND t.bucket_id IS NOT NULL
       AND t.date >= ? AND t.date < ?
     GROUP BY t.bucket_id`,
    monthStart,
    nextMonth,
  );
  const allocations: Allocation[] = calculateAllocations(buckets, monthlyAdded, spending);

  return {
    ...balances,
    monthlyAdded,
    base,
    allocations,
  };
}
