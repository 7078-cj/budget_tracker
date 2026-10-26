import { useEffect, useState } from 'react';
import { ActivityIndicator, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useSQLiteContext } from 'expo-sqlite';
import { BASES, formatMoney } from '../domain/budget';
import type { CalculationBase, DashboardSummary } from '../domain/types';
import {
  getCalculationBase,
  getDashboardSummary,
  setCalculationBase,
} from '../data/budgetRepository';
import {
  ActionButton,
  AppIcon,
  Card,
  ChoiceRow,
  ErrorMessage,
  Heading,
  Muted,
  Page,
  Row,
  categoryIcon,
} from '../ui/components';
import { colors, spacing } from '../ui/theme';

export function DashboardScreen({
  refreshKey,
  onChanged,
}: {
  refreshKey: number;
  onChanged: () => void;
}) {
  const database = useSQLiteContext();
  const [base, setBase] = useState<CalculationBase>('both');
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    async function load() {
      try {
        const selected = await getCalculationBase(database);
        const value = await getDashboardSummary(database, selected);
        if (active) {
          setBase(selected);
          setSummary(value);
          setError(null);
        }
      } catch (cause) {
        if (active) setError(cause instanceof Error ? cause.message : 'Could not load dashboard.');
      } finally {
        if (active) setLoading(false);
      }
    }
    void load();
    return () => {
      active = false;
    };
  }, [database, refreshKey]);

  async function changeBase(value: CalculationBase) {
    try {
      await setCalculationBase(database, value);
      setBase(value);
      setSummary(await getDashboardSummary(database, value));
      onChanged();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Could not update calculation basis.');
    }
  }

  const monthlySpent = summary?.allocations.reduce(
    (spent, allocation) => spent + allocation.spent,
    0,
  ) ?? 0;
  const remainingToSpend = (summary?.monthlyAdded ?? 0) - monthlySpent;

  return (
    <Page>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.eyebrow}>YOUR MONEY</Text>
        {summary ? (
          <Card>
            <Muted>Still available to spend this month</Muted>
            <Text
              style={[
                styles.spendable,
                remainingToSpend < 0 ? styles.overBudget : null,
              ]}
            >
              {formatMoney(Math.abs(remainingToSpend))}
            </Text>
            {remainingToSpend < 0 ? (
              <Muted>Spent over this month’s budget</Muted>
            ) : (
              <Muted>From your {formatMoney(summary.monthlyAdded)} monthly budget</Muted>
            )}
          </Card>
        ) : null}
        {summary ? (
          <Card>
            <Heading>Left in each category</Heading>
            <View style={styles.categoryRemainingList}>
              {summary.allocations.map((allocation) => (
                <Row key={allocation.id}>
                  <AppIcon name={categoryIcon(allocation.label)} size={19} />
                  <Text style={styles.categoryRemainingName} numberOfLines={1}>
                    {allocation.label}
                  </Text>
                  <View style={styles.categoryRemainingAmount}>
                    <Text
                      style={[
                        styles.categoryRemainingValue,
                        allocation.over > 0 ? styles.overBudget : null,
                      ]}
                    >
                      {allocation.over > 0
                        ? `−${formatMoney(allocation.over)}`
                        : formatMoney(allocation.remaining)}
                    </Text>
                    {allocation.over > 0 ? (
                      <Muted>over budget</Muted>
                    ) : null}
                  </View>
                </Row>
              ))}
            </View>
          </Card>
        ) : null}
        <Card>
          {loading && !summary ? <ActivityIndicator color={colors.primary} /> : null}
          {error ? <ErrorMessage>{error}</ErrorMessage> : null}
          {summary ? (
            <>
              <Muted>Current money on hand</Muted>
              <Text style={styles.total}>{formatMoney(summary.total)}</Text>
              <Row>
                <View style={styles.balance}>
                  <Muted>In the bank</Muted>
                  <Text style={styles.balanceValue}>{formatMoney(summary.bank)}</Text>
                </View>
                <View style={styles.balance}>
                  <Muted>Cash on hand</Muted>
                  <Text style={styles.balanceValue}>{formatMoney(summary.cash)}</Text>
                </View>
              </Row>
              <View style={styles.savedBalance}>
                <Muted>Saved in savings accounts</Muted>
                <Text style={styles.savedAmount}>{formatMoney(summary.savings)}</Text>
              </View>
              <View style={styles.spending}>
                <Muted>Spent from bank: {formatMoney(summary.spentBank)}</Muted>
                <Muted>Spent from cash: {formatMoney(summary.spentCash)}</Muted>
                {summary.spentUnknown > 0 ? (
                  <Muted>Spending source unknown: {formatMoney(summary.spentUnknown)}</Muted>
                ) : null}
              </View>
            </>
          ) : null}
        </Card>

        {summary ? (
          <>
            <Card>
              <Heading>Monthly budget</Heading>
              <Muted>Based on average additions over up to six months</Muted>
              <ChoiceRow
                label="Calculate from"
                options={BASES}
                value={base}
                onChange={(value) => void changeBase(value)}
              />
              <Text style={styles.monthlyAmount}>{formatMoney(summary.monthlyAdded)} / month</Text>
            </Card>

            <Card>
              <Heading>Budget vs. spending</Heading>
              <Muted>Monthly allocation compared with spending by category</Muted>
              <View style={styles.chartLegend}>
                <View style={styles.legendItem}>
                  <View style={[styles.legendDot, styles.budgetColor]} />
                  <Muted>Budget</Muted>
                </View>
                <View style={styles.legendItem}>
                  <View style={[styles.legendDot, styles.spentColor]} />
                  <Muted>Spent</Muted>
                </View>
              </View>
              {summary.allocations.map((allocation) => {
                const chartMaximum = Math.max(
                  ...summary.allocations.map((item) => Math.max(item.amount, item.spent)),
                  1,
                );
                return (
                  <View key={allocation.id} style={styles.chartCategory}>
                    <Row>
                      <AppIcon name={categoryIcon(allocation.label)} size={18} />
                      <Text style={styles.chartLabel} numberOfLines={1}>{allocation.label}</Text>
                      <Muted>{formatMoney(allocation.spent)} / {formatMoney(allocation.amount)}</Muted>
                    </Row>
                    <View style={styles.chartTrack}>
                      <View
                        style={[
                          styles.chartBar,
                          styles.budgetBar,
                          { width: `${Math.max(2, allocation.amount / chartMaximum * 100)}%` },
                        ]}
                      />
                    </View>
                    <View style={styles.chartTrack}>
                      <View
                        style={[
                          styles.chartBar,
                          styles.spentBar,
                          { width: `${allocation.spent > 0
                            ? Math.max(2, allocation.spent / chartMaximum * 100)
                            : 0}%` },
                        ]}
                      />
                    </View>
                  </View>
                );
              })}
            </Card>

          </>
        ) : null}
        <ActionButton title="Refresh" variant="secondary" onPress={onChanged} />
      </ScrollView>
    </Page>
  );
}

const styles = StyleSheet.create({
  content: {
    padding: spacing.lg,
    paddingBottom: 40,
  },
  eyebrow: {
    color: colors.primary,
    fontSize: 11,
    fontWeight: '800',
    letterSpacing: 1,
    marginBottom: spacing.sm,
  },
  total: {
    color: colors.text,
    fontSize: 32,
    fontWeight: '800',
    marginVertical: spacing.sm,
  },
  spendable: {
    color: colors.good,
    fontSize: 34,
    fontWeight: '900',
    marginTop: spacing.xs,
  },
  overBudget: {
    color: colors.bad,
  },
  categoryRemainingList: {
    gap: spacing.md,
    marginTop: spacing.sm,
  },
  categoryRemainingName: {
    color: colors.text,
    flex: 1,
    fontSize: 14,
    fontWeight: '600',
  },
  categoryRemainingAmount: {
    alignItems: 'flex-end',
  },
  categoryRemainingValue: {
    color: colors.good,
    fontSize: 14,
    fontWeight: '800',
  },
  balance: {
    flex: 1,
    backgroundColor: colors.surface,
    borderRadius: 10,
    padding: spacing.md,
  },
  balanceValue: {
    color: colors.text,
    fontSize: 16,
    fontWeight: '700',
    marginTop: spacing.xs,
  },
  spending: {
    gap: spacing.xs,
    marginTop: spacing.md,
  },
  savedBalance: {
    backgroundColor: colors.primaryLight,
    borderRadius: 10,
    marginTop: spacing.md,
    padding: spacing.md,
  },
  savedAmount: {
    color: colors.primary,
    fontSize: 20,
    fontWeight: '800',
    marginTop: spacing.xs,
  },
  monthlyAmount: {
    color: colors.primary,
    fontSize: 24,
    fontWeight: '800',
    marginTop: spacing.sm,
  },
  chartLegend: {
    flexDirection: 'row',
    gap: spacing.lg,
    marginTop: spacing.md,
  },
  legendItem: {
    alignItems: 'center',
    flexDirection: 'row',
    gap: spacing.xs,
  },
  legendDot: {
    borderRadius: 4,
    height: 8,
    width: 8,
  },
  budgetColor: {
    backgroundColor: colors.primary,
  },
  spentColor: {
    backgroundColor: colors.good,
  },
  chartCategory: {
    gap: spacing.xs,
    marginTop: spacing.md,
  },
  chartLabel: {
    color: colors.text,
    flex: 1,
    fontSize: 13,
    fontWeight: '700',
  },
  chartTrack: {
    backgroundColor: colors.surface,
    borderRadius: 4,
    height: 8,
    overflow: 'hidden',
  },
  chartBar: {
    borderRadius: 4,
    height: '100%',
  },
  budgetBar: {
    backgroundColor: colors.primary,
  },
  spentBar: {
    backgroundColor: colors.good,
  },
});
