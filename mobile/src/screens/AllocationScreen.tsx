import { useCallback, useEffect, useState } from 'react';
import Slider from '@react-native-community/slider';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { useSQLiteContext } from 'expo-sqlite';
import type { Bucket } from '../domain/types';
import { rebalancePercentages } from '../domain/budget';
import { getBuckets, savePercentages } from '../data/budgetRepository';
import {
  ActionButton,
  AppIcon,
  Card,
  ErrorMessage,
  Field,
  Heading,
  Muted,
  Page,
  Row,
  categoryIcon,
} from '../ui/components';
import { colors, spacing } from '../ui/theme';

export function AllocationScreen({ onChanged }: { onChanged: () => void }) {
  const database = useSQLiteContext();
  const [buckets, setBuckets] = useState<Bucket[]>([]);
  const [percentages, setPercentages] = useState<Record<number, string>>({});
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (isActive: () => boolean = () => true) => {
    const rows = await getBuckets(database);
    if (!isActive()) return;
    setBuckets(rows);
    setPercentages(Object.fromEntries(rows.map((bucket) => [bucket.id, String(bucket.percent)])));
  }, [database]);

  useEffect(() => {
    let active = true;
    void Promise.resolve().then(() => load(() => active)).catch((cause: unknown) => {
      if (active) setError(cause instanceof Error ? cause.message : 'Could not load allocation.');
    });
    return () => {
      active = false;
    };
  }, [load]);

  const total = buckets.reduce(
    (sum, bucket) => sum + (Number(percentages[bucket.id]) || 0),
    0,
  );

  async function save() {
    try {
      await savePercentages(
        database,
        buckets.map((bucket) => ({
          id: bucket.id,
          percent: Number(percentages[bucket.id]),
        })),
      );
      setError(null);
      await load();
      onChanged();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Could not save percentages.');
    }
  }

  return (
    <Page>
      <ScrollView contentContainerStyle={styles.content}>
        <Card>
          <Heading>Income allocation</Heading>
          <Muted>Set the percentages for your monthly budget. The total must be 100%.</Muted>
          {error ? <ErrorMessage>{error}</ErrorMessage> : null}
          {buckets.map((bucket) => {
            const percent = Number(percentages[bucket.id]) || 0;
            return (
              <View key={bucket.id} style={styles.bucket}>
                <Row>
                  <AppIcon name={categoryIcon(bucket.label)} />
                  <Text style={styles.bucketName}>{bucket.label}</Text>
                  <Text style={styles.percent}>{percent.toFixed(1)}%</Text>
                </Row>
                <Slider
                  accessibilityLabel={`${bucket.label} allocation`}
                  minimumValue={0}
                  maximumValue={100}
                  step={0.1}
                  value={percent}
                  minimumTrackTintColor={colors.primary}
                  maximumTrackTintColor={colors.border}
                  thumbTintColor={colors.primary}
                  onValueChange={(value) =>
                    setPercentages((current) =>
                      rebalancePercentages(buckets, current, bucket.id, value),
                    )
                  }
                  style={styles.slider}
                />
                <Field
                  label={`${bucket.label} percentage`}
                  value={percentages[bucket.id] ?? ''}
                  onChangeText={(value) =>
                    setPercentages((current) => ({ ...current, [bucket.id]: value }))
                  }
                  keyboardType="decimal-pad"
                  placeholder="0"
                />
              </View>
            );
          })}
          <Muted style={styles.total}>Total: {total.toFixed(1)}%</Muted>
          <ActionButton
            title="Save allocation"
            onPress={() => void save()}
            disabled={Math.abs(total - 100) > 0.0001}
          />
        </Card>
      </ScrollView>
    </Page>
  );
}

const styles = StyleSheet.create({
  content: {
    padding: spacing.lg,
    paddingBottom: 40,
  },
  total: {
    color: colors.text,
    fontWeight: '700',
    marginVertical: spacing.md,
  },
  bucket: {
    borderBottomColor: colors.border,
    borderBottomWidth: StyleSheet.hairlineWidth,
    marginTop: spacing.lg,
    paddingBottom: spacing.sm,
  },
  bucketName: {
    color: colors.text,
    flex: 1,
    fontSize: 15,
    fontWeight: '700',
  },
  percent: {
    color: colors.primary,
    fontSize: 16,
    fontWeight: '800',
    minWidth: 62,
    textAlign: 'right',
  },
  slider: {
    height: 42,
    marginHorizontal: -spacing.sm,
    marginTop: spacing.xs,
  },
});
