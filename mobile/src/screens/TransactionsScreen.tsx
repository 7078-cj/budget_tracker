import { useCallback, useEffect, useMemo, useState } from 'react';
import { Alert, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useSQLiteContext } from 'expo-sqlite';
import { ACCOUNT_TYPES, formatMoney, PAYMENT_SOURCES, todayIso } from '../domain/budget';
import type { Account, Bucket, PaymentSource, Transaction } from '../domain/types';
import {
  deleteTransaction,
  getAccounts,
  getBuckets,
  getTransactions,
  saveTransaction,
} from '../data/budgetRepository';
import {
  ActionButton,
  AppModal,
  AppIcon,
  ChoiceRow,
  ErrorMessage,
  Field,
  FloatingActionButton,
  Heading,
  IconButton,
  Muted,
  Page,
  type IconName,
} from '../ui/components';
import { colors, spacing } from '../ui/theme';

export function TransactionsScreen({ onChanged }: { onChanged: () => void }) {
  const database = useSQLiteContext();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [buckets, setBuckets] = useState<Bucket[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [editingId, setEditingId] = useState<number | undefined>();
  const [formVisible, setFormVisible] = useState(false);
  const [date, setDate] = useState(todayIso());
  const [accountId, setAccountId] = useState<number>(-1);
  const [amount, setAmount] = useState('');
  const [source, setSource] = useState<PaymentSource | 'unknown' | null>('bank');
  const [bucketId, setBucketId] = useState<number | null>(null);
  const [note, setNote] = useState('');
  const [error, setError] = useState<string | null>(null);

  const selectedAccount = useMemo(
    () => accounts.find((account) => account.id === accountId),
    [accounts, accountId],
  );

  const load = useCallback(async (isActive: () => boolean = () => true) => {
    const [accountRows, bucketRows, transactionRows] = await Promise.all([
      getAccounts(database),
      getBuckets(database),
      getTransactions(database),
    ]);
    if (!isActive()) return;
    setAccounts(accountRows);
    setBuckets(bucketRows);
    setTransactions(transactionRows);
    if (accountId < 0 && accountRows.length > 0) {
      setAccountId(accountRows[0].id);
      setSource(accountRows[0].type === 'spending' || accountRows[0].type === 'savings' ? 'bank' : null);
      setBucketId(defaultBucketId(accountRows[0].type, bucketRows));
    }
  }, [accountId, database]);

  useEffect(() => {
    let active = true;
    void Promise.resolve().then(() => load(() => active)).catch((cause: unknown) => {
      if (active) setError(cause instanceof Error ? cause.message : 'Could not load transactions.');
    });
    return () => {
      active = false;
    };
  }, [load]);

  function selectAccount(id: number) {
    const account = accounts.find((item) => item.id === id);
    setAccountId(id);
    setSource(account?.type === 'spending' || account?.type === 'savings' ? 'bank' : null);
    setBucketId(account ? defaultBucketId(account.type, buckets) : null);
  }

  function resetForm() {
    setFormVisible(false);
    setEditingId(undefined);
    setDate(todayIso());
    setAmount('');
    setNote('');
    const initialAccount = accounts[0];
    setAccountId(initialAccount?.id ?? -1);
    setSource(initialAccount?.type === 'spending' || initialAccount?.type === 'savings' ? 'bank' : null);
    setBucketId(initialAccount ? defaultBucketId(initialAccount.type, buckets) : null);
    setError(null);
  }

  function startCreate() {
    setEditingId(undefined);
    setDate(todayIso());
    setAmount('');
    setNote('');
    const initialAccount = accounts[0];
    setAccountId(initialAccount?.id ?? -1);
    setSource(initialAccount?.type === 'spending' || initialAccount?.type === 'savings' ? 'bank' : null);
    setBucketId(initialAccount ? defaultBucketId(initialAccount.type, buckets) : null);
    setError(null);
    setFormVisible(true);
  }

  function startEdit(transaction: Transaction) {
    setEditingId(transaction.id);
    setDate(transaction.date);
    setAccountId(transaction.account_id);
    setAmount(String(transaction.amount));
    setNote(transaction.note ?? '');
    setSource(transaction.source);
    setBucketId(transaction.bucket_id);
    setError(null);
    setFormVisible(true);
  }

  async function submit() {
    try {
      await saveTransaction(
        database,
        {
          date,
          accountId,
          amount: Number(amount),
          note,
          source: selectedAccount?.type === 'spending' || selectedAccount?.type === 'savings'
            ? source === 'bank' || source === 'cash' ? source : null
            : selectedAccount?.type === 'cash'
              ? source === 'bank' ? 'bank' : null
              : null,
          bucketId: selectedAccount?.type === 'spending' || selectedAccount?.type === 'savings'
            ? bucketId
            : null,
        },
        editingId,
      );
      resetForm();
      await load();
      onChanged();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Could not save transaction.');
    }
  }

  function confirmDelete(transaction: Transaction) {
    Alert.alert('Delete transaction?', `${transaction.account}: ${formatMoney(transaction.amount)}`, [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Delete',
        style: 'destructive',
        onPress: () => {
          void deleteTransaction(database, transaction.id)
            .then(async () => {
              await load();
              onChanged();
              if (editingId === transaction.id) resetForm();
            })
            .catch((cause: unknown) =>
              setError(cause instanceof Error ? cause.message : 'Could not delete transaction.'),
            );
        },
      },
    ]);
  }

  return (
    <Page>
      <ScrollView contentContainerStyle={styles.content}>
        {!formVisible && error ? <ErrorMessage>{error}</ErrorMessage> : null}
        <Heading>Transactions</Heading>
        {transactions.map((transaction) => (
          <View key={transaction.id} style={styles.transactionRow}>
            <View style={styles.transactionIcon}>
              <AppIcon name={transactionIcon(transaction)} size={20} />
            </View>
            <View style={styles.transactionDetails}>
              <Text style={styles.transactionName} numberOfLines={1}>{transaction.account}</Text>
              <Muted>
                {transaction.date} · {transaction.type === 'spending'
                  ? `${transaction.source === 'cash' ? 'Cash' : transaction.source === 'bank' ? 'Bank' : 'Source unknown'} · ${transaction.budget ?? 'Uncategorized'}`
                  : transaction.type === 'savings'
                    ? `Savings from ${transaction.source === 'cash' ? 'cash' : transaction.source === 'bank' ? 'bank' : 'unknown source'}`
                    : transaction.type === 'cash' && transaction.source === 'bank'
                      ? 'Cash withdrawal from bank'
                      : ACCOUNT_TYPES.find((type) => type.value === transaction.type)?.label}
              </Muted>
              {transaction.note ? (
                <Muted numberOfLines={1}>{transaction.note}</Muted>
              ) : null}
              <Text
                style={[
                  styles.amount,
                  transaction.type === 'spending' ? styles.spendingAmount : null,
                ]}
              >
                {transaction.type === 'spending' ? '−' : '+'}{formatMoney(transaction.amount)}
              </Text>
            </View>
            <View style={styles.actions}>
              <IconButton
                name="edit"
                label={`Edit transaction for ${transaction.account}`}
                onPress={() => startEdit(transaction)}
              />
              <IconButton
                name="delete"
                label={`Delete transaction for ${transaction.account}`}
                color={colors.bad}
                onPress={() => confirmDelete(transaction)}
              />
            </View>
          </View>
        ))}
      </ScrollView>
      <FloatingActionButton label="Add transaction" onPress={startCreate} />
      <AppModal
        visible={formVisible}
        title={editingId === undefined ? 'Add transaction' : 'Update transaction'}
        onClose={resetForm}
      >
        {error ? <ErrorMessage>{error}</ErrorMessage> : null}
        {accounts.length === 0 ? (
          <Muted>Create an account before adding transactions.</Muted>
        ) : (
          <>
            <Field label="Date" value={date} onChangeText={setDate} placeholder="YYYY-MM-DD" />
            <ChoiceRow
              label="Account"
              options={accounts.map((account) => ({
                value: account.id,
                label: `${account.name} · ${ACCOUNT_TYPES.find((type) => type.value === account.type)?.label}`,
              }))}
              value={accountId}
              onChange={selectAccount}
            />
            <Field
              label="Amount"
              value={amount}
              onChangeText={setAmount}
              placeholder="0.00"
              keyboardType="decimal-pad"
            />
            {selectedAccount?.type === 'savings' ? (
              <>
                <ChoiceRow
                  label="Savings contribution from"
                  options={[
                    { value: 'unknown', label: 'Choose source' },
                    ...PAYMENT_SOURCES,
                  ]}
                  value={source ?? 'unknown'}
                  onChange={(value) => setSource(value === 'unknown' ? null : value)}
                />
                <Muted>This amount will be deducted from the selected account balance.</Muted>
              </>
            ) : null}
            {selectedAccount?.type === 'spending' ? (
              <>
                <ChoiceRow
                  label="Paid from"
                  options={[
                    { value: 'unknown', label: 'Choose source' },
                    ...PAYMENT_SOURCES,
                  ]}
                  value={source ?? 'unknown'}
                  onChange={setSource}
                />
                <ChoiceRow
                  label="Budget category"
                  options={buckets.map((bucket) => ({
                    value: bucket.id,
                    label: bucket.label,
                  }))}
                  value={bucketId ?? -1}
                  onChange={setBucketId}
                />
              </>
            ) : null}
            {selectedAccount?.type === 'cash' ? (
              <ChoiceRow
                label="Cash source"
                options={[
                  { value: 'none', label: 'Added from elsewhere' },
                  { value: 'bank', label: 'Withdrawn from bank' },
                ]}
                value={source === 'bank' ? 'bank' : 'none'}
                onChange={(value) => setSource(value === 'bank' ? 'bank' : null)}
              />
            ) : null}
            <Field label="Note (optional)" value={note} onChangeText={setNote} />
            <ActionButton
              title={editingId === undefined ? 'Create transaction' : 'Save changes'}
              onPress={() => void submit()}
            />
          </>
        )}
      </AppModal>
    </Page>
  );
}

const styles = StyleSheet.create({
  content: {
    padding: spacing.lg,
    paddingBottom: 100,
  },
  transactionName: {
    color: colors.text,
    fontSize: 15,
    fontWeight: '700',
  },
  amount: {
    color: colors.text,
    fontSize: 14,
    fontWeight: '800',
    marginTop: spacing.xs,
  },
  transactionRow: {
    alignItems: 'center',
    backgroundColor: colors.card,
    borderBottomColor: colors.border,
    borderBottomWidth: StyleSheet.hairlineWidth,
    flexDirection: 'row',
    gap: spacing.sm,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.md,
  },
  transactionIcon: {
    alignItems: 'center',
    alignSelf: 'flex-start',
    backgroundColor: colors.primaryLight,
    borderRadius: 13,
    height: 42,
    justifyContent: 'center',
    width: 42,
  },
  transactionDetails: {
    flex: 1,
    gap: 3,
    minWidth: 0,
  },
  actions: {
    alignItems: 'center',
    gap: spacing.xs,
  },
  spendingAmount: {
    color: colors.bad,
  },
});

function defaultBucketId(accountType: Account['type'], buckets: Bucket[]): number | null {
  if (accountType === 'savings') {
    return buckets.find((bucket) => bucket.label === 'Savings')?.id ?? null;
  }
  return accountType === 'spending' ? buckets[0]?.id ?? null : null;
}

function transactionIcon(transaction: Transaction): IconName {
  if (transaction.type === 'savings') return 'savings';
  if (transaction.type === 'spending') return 'spending';
  if (transaction.type === 'cash') return 'cash';
  return 'bank';
}
