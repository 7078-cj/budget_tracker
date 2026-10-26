import type {
  AccountType,
  Allocation,
  Bucket,
  CalculationBase,
  PaymentSource,
} from './types';

export const REST_LABEL = 'Needs & bills';
export const BASES: { value: CalculationBase; label: string }[] = [
  { value: 'both', label: 'Both' },
  { value: 'bank', label: 'Bank' },
  { value: 'cash', label: 'Cash added' },
];
export const ACCOUNT_TYPES: { value: AccountType; label: string }[] = [
  { value: 'bank', label: 'Bank' },
  { value: 'cash', label: 'Cash on hand' },
  { value: 'spending', label: 'Spending' },
  { value: 'savings', label: 'Savings' },
];
export const PAYMENT_SOURCES: { value: PaymentSource; label: string }[] = [
  { value: 'bank', label: 'Bank' },
  { value: 'cash', label: 'Cash on hand' },
];

export interface MonthlyCashAdded {
  month: string;
  bankAdded: number;
  cashAdded: number;
}

export interface BalanceTotals {
  bankIn: number;
  cashIn: number;
  withdrawn: number;
  spentCash: number;
  spentBank: number;
  spentUnknown: number;
  savings: number;
  savingsFromBank: number;
  savingsFromCash: number;
}

export function calculateBalances(totals: BalanceTotals) {
  const bank = totals.bankIn - totals.withdrawn - totals.spentBank - totals.savingsFromBank;
  const cash = totals.cashIn - totals.spentCash - totals.savingsFromCash;
  return {
    bank,
    cash,
    spentBank: totals.spentBank,
    spentCash: totals.spentCash,
    spentUnknown: totals.spentUnknown,
    savings: totals.savings,
    total: bank + cash + totals.savings - totals.spentUnknown,
  };
}

export function averageMonthlyAdded(
  rows: MonthlyCashAdded[],
  base: CalculationBase,
  today = new Date(),
): number {
  const amounts = rows.map((row) =>
    base === 'bank'
      ? row.bankAdded
      : base === 'cash'
        ? row.cashAdded
        : row.bankAdded + row.cashAdded,
  );
  const firstActiveIndex = amounts.findIndex((amount) => amount > 0);
  const firstActiveMonth = rows[firstActiveIndex]?.month;
  if (!firstActiveMonth) return 0;

  const [firstYear, firstMonth] = firstActiveMonth.split('-').map(Number);
  const elapsedMonths =
    (today.getFullYear() - firstYear) * 12 + today.getMonth() - firstMonth + 2;
  const trackedMonths = Math.min(6, elapsedMonths);
  if (trackedMonths <= 0) return 0;
  return amounts.reduce((sum, amount) => sum + Math.max(amount, 0), 0) / trackedMonths;
}

export function calculateAllocations(
  buckets: Bucket[],
  monthlyAdded: number,
  spending: { bucket_id: number; spent: number }[],
): Allocation[] {
  const spentByBucket = new Map(spending.map((row) => [row.bucket_id, row.spent]));
  return buckets.map((bucket) => {
    const amount = monthlyAdded * bucket.percent / 100;
    const spent = spentByBucket.get(bucket.id) ?? 0;
    return {
      ...bucket,
      amount,
      spent,
      remaining: Math.max(amount - spent, 0),
      over: Math.max(spent - amount, 0),
    };
  });
}

export function validatePercentages(percentages: number[]): void {
  if (percentages.some((value) => !Number.isFinite(value) || value < 0 || value > 100)) {
    throw new Error('Percentages must be between 0 and 100.');
  }
  const total = percentages.reduce((sum, value) => sum + value, 0);
  if (Math.abs(total - 100) > 0.0001) {
    throw new Error(`Percentages must add up to 100% (currently ${total.toFixed(1)}%).`);
  }
}

export function rebalancePercentages(
  buckets: Bucket[],
  current: Record<number, string>,
  changedId: number,
  rawValue: number,
): Record<number, string> {
  const value = Math.min(100, Math.max(0, Math.round(rawValue * 10) / 10));
  const needs = buckets.find((bucket) => bucket.label === REST_LABEL);
  const otherBuckets = buckets.filter((bucket) => bucket.id !== needs?.id);
  if (!buckets.some((bucket) => bucket.id === changedId)) return current;

  const result: Record<number, string> = { ...current };
  if (needs?.id === changedId) {
    const existing = otherBuckets.map((bucket) => Math.max(0, Number(current[bucket.id]) || 0));
    const targetTenths = Math.round((100 - value) * 10);
    const total = existing.reduce((sum, percent) => sum + percent, 0);
    const weights = existing.map((percent) =>
      total > 0 ? percent / total : 1 / Math.max(1, existing.length),
    );
    const shares = weights.map((weight) => Math.floor(weight * targetTenths));
    let remainder = targetTenths - shares.reduce((sum, share) => sum + share, 0);
    const order = weights
      .map((weight, index) => ({ index, fraction: weight * targetTenths - shares[index] }))
      .sort((left, right) => right.fraction - left.fraction);
    for (let index = 0; index < order.length && remainder > 0; index += 1) {
      shares[order[index].index] += 1;
      remainder -= 1;
    }
    otherBuckets.forEach((bucket, index) => {
      result[bucket.id] = String((shares[index] ?? 0) / 10);
    });
    result[changedId] = String(value);
    return result;
  }

  const fixedTotal = otherBuckets
    .filter((bucket) => bucket.id !== changedId && bucket.id !== needs?.id)
    .reduce((sum, bucket) => sum + (Number(current[bucket.id]) || 0), 0);
  const adjustedValue = Math.min(value, Math.max(0, 100 - fixedTotal));
  result[changedId] = String(adjustedValue);
  if (needs) {
    result[needs.id] = String(Math.round((100 - fixedTotal - adjustedValue) * 10) / 10);
  }
  return result;
}

export function validateAccount(name: string, type: AccountType): string {
  const normalized = name.trim();
  if (!normalized) throw new Error('Account name is required.');
  if (!ACCOUNT_TYPES.some((option) => option.value === type)) {
    throw new Error('Select a valid account type.');
  }
  return normalized;
}

export function validateTransaction(input: {
  date: string;
  amount: number;
  accountType: AccountType;
  source: PaymentSource | null;
  bucketId: number | null;
}): void {
  const dateParts = /^(\d{4})-(\d{2})-(\d{2})$/.exec(input.date);
  const parsedDate = dateParts
    ? new Date(Number(dateParts[1]), Number(dateParts[2]) - 1, Number(dateParts[3]))
    : null;
  if (
    !parsedDate ||
    parsedDate.getFullYear() !== Number(dateParts?.[1]) ||
    parsedDate.getMonth() + 1 !== Number(dateParts?.[2]) ||
    parsedDate.getDate() !== Number(dateParts?.[3])
  ) {
    throw new Error('Enter a valid date in YYYY-MM-DD format.');
  }
  if (!Number.isFinite(input.amount) || input.amount <= 0) {
    throw new Error('Amount must be greater than zero.');
  }
  if (input.accountType === 'spending' && !input.source) {
    throw new Error('Choose whether this was paid from the bank or cash.');
  }
  if (input.accountType === 'spending' && input.bucketId === null) {
    throw new Error('Choose a budget category.');
  }
  if (input.accountType !== 'spending' && input.accountType !== 'savings' && input.bucketId !== null) {
    throw new Error('Only spending transactions can have a budget category.');
  }
  if (input.accountType === 'bank' && input.source !== null) {
    throw new Error('Bank deposits do not have a payment source.');
  }
  if (input.accountType === 'savings' && (!input.source || input.bucketId === null)) {
    throw new Error('Choose whether the savings contribution came from bank or cash.');
  }
  if (input.accountType === 'cash' && input.source !== null && input.source !== 'bank') {
    throw new Error('Cash additions can only be marked as a bank withdrawal.');
  }
}

export function formatMoney(amount: number): string {
  return new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: 'PHP',
    minimumFractionDigits: 2,
  }).format(amount);
}

export function todayIso(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(
    now.getDate(),
  ).padStart(2, '0')}`;
}
