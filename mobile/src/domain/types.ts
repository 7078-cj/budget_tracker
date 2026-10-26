export type AccountType = 'bank' | 'cash' | 'spending' | 'savings';
export type PaymentSource = 'bank' | 'cash';
export type CalculationBase = 'both' | 'bank' | 'cash';
export type AppTheme = 'light' | 'night';

export interface Account {
  id: number;
  name: string;
  type: AccountType;
}

export interface Bucket {
  id: number;
  label: string;
  percent: number;
}

export interface Transaction {
  id: number;
  date: string;
  account_id: number;
  account: string;
  type: AccountType;
  amount: number;
  note: string;
  source: PaymentSource | null;
  bucket_id: number | null;
  budget: string | null;
}

export interface Allocation extends Bucket {
  amount: number;
  spent: number;
  remaining: number;
  over: number;
}

export interface DashboardSummary {
  bank: number;
  cash: number;
  spentBank: number;
  spentCash: number;
  spentUnknown: number;
  savings: number;
  total: number;
  monthlyAdded: number;
  base: CalculationBase;
  allocations: Allocation[];
}

export interface AccountInput {
  name: string;
  type: AccountType;
}

export interface TransactionInput {
  date: string;
  accountId: number;
  amount: number;
  note: string;
  source: PaymentSource | null;
  bucketId: number | null;
}
