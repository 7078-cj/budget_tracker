import { useCallback, useEffect, useState } from 'react';
import { Alert, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useSQLiteContext } from 'expo-sqlite';
import { ACCOUNT_TYPES } from '../domain/budget';
import type { Account, AccountType } from '../domain/types';
import { deleteAccount, getAccounts, saveAccount } from '../data/budgetRepository';
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
  Page,
  type IconName,
} from '../ui/components';
import { colors, spacing } from '../ui/theme';

export function AccountsScreen({ onChanged }: { onChanged: () => void }) {
  const database = useSQLiteContext();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [editingId, setEditingId] = useState<number | undefined>();
  const [formVisible, setFormVisible] = useState(false);
  const [name, setName] = useState('');
  const [type, setType] = useState<AccountType>('bank');
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (isActive: () => boolean = () => true) => {
    const rows = await getAccounts(database);
    if (isActive()) setAccounts(rows);
  }, [database]);

  useEffect(() => {
    let active = true;
    void Promise.resolve().then(() => load(() => active)).catch((cause: unknown) => {
      if (active) setError(cause instanceof Error ? cause.message : 'Could not load accounts.');
    });
    return () => {
      active = false;
    };
  }, [load]);

  function startEdit(account: Account) {
    setEditingId(account.id);
    setName(account.name);
    setType(account.type);
    setError(null);
    setFormVisible(true);
  }

  function startCreate() {
    setEditingId(undefined);
    setName('');
    setType('bank');
    setError(null);
    setFormVisible(true);
  }

  function closeForm() {
    setFormVisible(false);
    setEditingId(undefined);
    setName('');
    setType('bank');
    setError(null);
  }

  async function submit() {
    try {
      await saveAccount(database, { name, type }, editingId);
      closeForm();
      await load();
      onChanged();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Could not save account.');
    }
  }

  function confirmDelete(account: Account) {
    Alert.alert(
      'Delete account?',
      `Delete ${account.name} and its transactions?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: () => {
            void deleteAccount(database, account.id)
              .then(async () => {
                await load();
                if (editingId === account.id) closeForm();
                onChanged();
              })
              .catch((cause: unknown) =>
                setError(cause instanceof Error ? cause.message : 'Could not delete account.'),
              );
          },
        },
      ],
    );
  }

  return (
    <Page>
      <ScrollView contentContainerStyle={styles.content}>
        {!formVisible && error ? <ErrorMessage>{error}</ErrorMessage> : null}
        <Heading>Accounts</Heading>
        {accounts.map((account) => (
          <View key={account.id} style={styles.accountRow}>
            <View style={styles.accountIcon}>
              <AppIcon name={accountIcon(account.type)} />
            </View>
            <View style={styles.accountDetails}>
              <Text style={styles.accountName}>{account.name}</Text>
              <Text style={styles.type}>
                {ACCOUNT_TYPES.find((option) => option.value === account.type)?.label}
              </Text>
            </View>
            <IconButton name="edit" label={`Edit ${account.name}`} onPress={() => startEdit(account)} />
            <IconButton
              name="delete"
              label={`Delete ${account.name}`}
              color={colors.bad}
              onPress={() => confirmDelete(account)}
            />
          </View>
        ))}
      </ScrollView>
      <FloatingActionButton label="Add account" onPress={startCreate} />
      <AppModal
        visible={formVisible}
        title={editingId === undefined ? 'Add account' : 'Update account'}
        onClose={closeForm}
      >
        {error ? <ErrorMessage>{error}</ErrorMessage> : null}
        <Field label="Account name" value={name} onChangeText={setName} placeholder="e.g. Wallet" />
        <ChoiceRow label="Account type" options={ACCOUNT_TYPES} value={type} onChange={setType} />
        <ActionButton
          title={editingId === undefined ? 'Create account' : 'Save changes'}
          onPress={() => void submit()}
        />
      </AppModal>
    </Page>
  );
}

function accountIcon(type: Account['type']): IconName {
  return type === 'bank' ? 'bank' : type === 'cash' ? 'cash' : 'spending';
}

const styles = StyleSheet.create({
  content: {
    padding: spacing.lg,
    paddingBottom: 100,
  },
  accountName: {
    color: colors.text,
    fontSize: 15,
    fontWeight: '700',
  },
  accountRow: {
    alignItems: 'center',
    backgroundColor: colors.card,
    borderBottomColor: colors.border,
    borderBottomWidth: StyleSheet.hairlineWidth,
    flexDirection: 'row',
    gap: spacing.sm,
    minHeight: 72,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.sm,
  },
  accountIcon: {
    alignItems: 'center',
    backgroundColor: colors.primaryLight,
    borderRadius: 13,
    height: 42,
    justifyContent: 'center',
    width: 42,
  },
  accountDetails: {
    flex: 1,
    gap: 3,
  },
  type: {
    color: colors.muted,
    fontSize: 12,
  },
});
