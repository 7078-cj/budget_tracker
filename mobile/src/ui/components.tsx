import type { PropsWithChildren, ReactNode } from 'react';
import {
  KeyboardAvoidingView,
  Modal,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import type { ColorValue, StyleProp, TextStyle } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { SymbolView } from 'expo-symbols';
import type { SymbolViewProps } from 'expo-symbols';
import { colors, spacing } from './theme';

export const ICONS = {
  dashboard: {
    ios: 'chart.pie.fill',
    android: 'pie_chart',
    web: 'pie_chart',
  },
  transactions: {
    ios: 'arrow.left.arrow.right',
    android: 'swap_horiz',
    web: 'swap_horiz',
  },
  accounts: {
    ios: 'building.2.fill',
    android: 'account_balance',
    web: 'account_balance',
  },
  allocation: {
    ios: 'slider.horizontal.3',
    android: 'tune',
    web: 'tune',
  },
  savings: {
    ios: 'banknote.fill',
    android: 'savings',
    web: 'savings',
  },
  guiltFree: {
    ios: 'cart.fill',
    android: 'shopping_cart',
    web: 'shopping_cart',
  },
  investment: {
    ios: 'chart.line.uptrend.xyaxis',
    android: 'monitoring',
    web: 'monitoring',
  },
  emergency: {
    ios: 'cross.case.fill',
    android: 'medical_services',
    web: 'medical_services',
  },
  needs: {
    ios: 'house.fill',
    android: 'home',
    web: 'home',
  },
  bank: {
    ios: 'building.columns.fill',
    android: 'account_balance',
    web: 'account_balance',
  },
  cash: {
    ios: 'wallet.pass.fill',
    android: 'account_balance_wallet',
    web: 'account_balance_wallet',
  },
  spending: {
    ios: 'creditcard.fill',
    android: 'credit_card',
    web: 'credit_card',
  },
  edit: {
    ios: 'pencil',
    android: 'edit',
    web: 'edit',
  },
  delete: {
    ios: 'trash',
    android: 'delete',
    web: 'delete',
  },
  close: {
    ios: 'xmark',
    android: 'close',
    web: 'close',
  },
  add: {
    ios: 'plus',
    android: 'add',
    web: 'add',
  },
} as const satisfies Record<string, SymbolViewProps['name']>;

export type IconName = keyof typeof ICONS;

export function categoryIcon(label: string): IconName {
  if (label === 'Savings') return 'savings';
  if (label === 'Guilt-free') return 'guiltFree';
  if (label === 'Investment') return 'investment';
  if (label === 'Emergency fund') return 'emergency';
  return 'needs';
}

export function AppIcon({
  name,
  color = colors.primary,
  size = 22,
}: {
  name: IconName;
  color?: ColorValue;
  size?: number;
}) {
  return (
    <SymbolView
      name={ICONS[name]}
      tintColor={color}
      size={size}
      weight="semibold"
      accessibilityElementsHidden
      importantForAccessibility="no"
    />
  );
}

export function IconButton({
  name,
  label,
  onPress,
  color = colors.primary,
}: {
  name: IconName;
  label: string;
  onPress: () => void;
  color?: ColorValue;
}) {
  return (
    <Pressable
      onPress={onPress}
      accessibilityRole="button"
      accessibilityLabel={label}
      hitSlop={8}
      style={styles.iconButton}
    >
      <AppIcon name={name} color={color} size={19} />
    </Pressable>
  );
}

export function FloatingActionButton({
  label,
  onPress,
}: {
  label: string;
  onPress: () => void;
}) {
  return (
    <Pressable
      onPress={onPress}
      accessibilityRole="button"
      accessibilityLabel={label}
      style={styles.floatingButton}
    >
      <AppIcon name="add" color={colors.white} size={28} />
    </Pressable>
  );
}

export function AppModal({
  visible,
  title,
  onClose,
  children,
}: PropsWithChildren<{
  visible: boolean;
  title: string;
  onClose: () => void;
}>) {
  return (
    <Modal
      visible={visible}
      transparent
      animationType="slide"
      onRequestClose={onClose}
      statusBarTranslucent
    >
      <KeyboardAvoidingView
        style={styles.modalRoot}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <Pressable
          accessibilityRole="button"
          accessibilityLabel="Close dialog"
          onPress={onClose}
          style={styles.modalBackdrop}
        />
        <View style={styles.modalSheet}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>{title}</Text>
            <IconButton name="close" label="Close dialog" onPress={onClose} />
          </View>
          <ScrollView
            keyboardShouldPersistTaps="handled"
            contentContainerStyle={styles.modalContent}
          >
            {children}
          </ScrollView>
        </View>
      </KeyboardAvoidingView>
    </Modal>
  );
}

export function Page({ children }: PropsWithChildren) {
  return (
    <SafeAreaView edges={['top']} style={styles.page}>
      {children}
    </SafeAreaView>
  );
}

export function Card({ children }: PropsWithChildren) {
  return <View style={styles.card}>{children}</View>;
}

export function Heading({ children }: PropsWithChildren) {
  return <Text style={styles.heading}>{children}</Text>;
}

export function Muted({
  children,
  style,
  numberOfLines,
}: PropsWithChildren<{ style?: StyleProp<TextStyle>; numberOfLines?: number }>) {
  return (
    <Text numberOfLines={numberOfLines} style={[styles.muted, style]}>
      {children}
    </Text>
  );
}

export function Field({
  label,
  value,
  onChangeText,
  placeholder,
  keyboardType,
}: {
  label: string;
  value: string;
  onChangeText: (value: string) => void;
  placeholder?: string;
  keyboardType?: 'default' | 'numeric' | 'decimal-pad';
}) {
  return (
    <View style={styles.field}>
      <Text style={styles.fieldLabel}>{label}</Text>
      <TextInput
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor={colors.muted}
        keyboardType={keyboardType}
        style={styles.input}
        autoCapitalize="sentences"
      />
    </View>
  );
}

export function ChoiceRow<T extends string | number>({
  label,
  options,
  value,
  onChange,
}: {
  label: string;
  options: { value: T; label: string }[];
  value: T;
  onChange: (value: T) => void;
}) {
  return (
    <View style={styles.field}>
      <Text style={styles.fieldLabel}>{label}</Text>
      <View style={styles.choiceWrap}>
        {options.map((option) => {
          const selected = option.value === value;
          return (
            <Pressable
              key={String(option.value)}
              onPress={() => onChange(option.value)}
              style={[styles.choice, selected && styles.choiceSelected]}
              accessibilityRole="button"
              accessibilityState={{ selected }}
            >
              <Text style={[styles.choiceText, selected && styles.choiceTextSelected]}>
                {option.label}
              </Text>
            </Pressable>
          );
        })}
      </View>
    </View>
  );
}

export function ActionButton({
  title,
  onPress,
  variant = 'primary',
  disabled = false,
}: {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'danger';
  disabled?: boolean;
}) {
  return (
    <Pressable
      onPress={onPress}
      disabled={disabled}
      style={[
        styles.button,
        variant === 'primary' ? styles.primaryButton : null,
        variant === 'secondary' ? styles.secondaryButton : null,
        variant === 'danger' ? styles.dangerButton : null,
        disabled && styles.disabledButton,
      ]}
    >
      <Text
        style={[
          styles.buttonText,
          variant === 'secondary' ? styles.secondaryButtonText : null,
          variant === 'danger' ? styles.dangerButtonText : null,
        ]}
      >
        {title}
      </Text>
    </Pressable>
  );
}

export function ErrorMessage({ children }: PropsWithChildren) {
  return <Text style={styles.error}>{children}</Text>;
}

export function Row({ children }: { children: ReactNode }) {
  return <View style={styles.row}>{children}</View>;
}

const styles = StyleSheet.create({
  page: {
    flex: 1,
    backgroundColor: colors.background,
  },
  card: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 16,
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  heading: {
    color: colors.text,
    fontSize: 18,
    fontWeight: '700',
    marginBottom: spacing.sm,
  },
  muted: {
    color: colors.muted,
    fontSize: 13,
  },
  field: {
    marginBottom: spacing.md,
  },
  fieldLabel: {
    color: colors.muted,
    fontSize: 12,
    fontWeight: '600',
    marginBottom: spacing.xs,
  },
  input: {
    minHeight: 44,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 10,
    backgroundColor: colors.card,
    color: colors.text,
    paddingHorizontal: spacing.md,
    fontSize: 15,
  },
  choiceWrap: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  choice: {
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 999,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    backgroundColor: colors.card,
  },
  choiceSelected: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  choiceText: {
    color: colors.muted,
    fontSize: 13,
    fontWeight: '600',
  },
  choiceTextSelected: {
    color: colors.white,
  },
  button: {
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 44,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
  },
  primaryButton: {
    backgroundColor: colors.primary,
  },
  secondaryButton: {
    backgroundColor: colors.primaryLight,
  },
  dangerButton: {
    backgroundColor: '#FDECEE',
  },
  disabledButton: {
    opacity: 0.5,
  },
  buttonText: {
    color: colors.white,
    fontWeight: '700',
  },
  secondaryButtonText: {
    color: colors.primary,
  },
  dangerButtonText: {
    color: colors.bad,
  },
  error: {
    color: colors.bad,
    fontSize: 13,
    marginBottom: spacing.md,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: spacing.sm,
  },
  iconButton: {
    alignItems: 'center',
    justifyContent: 'center',
    width: 38,
    height: 38,
    borderRadius: 12,
    backgroundColor: colors.surface,
  },
  floatingButton: {
    alignItems: 'center',
    backgroundColor: colors.primary,
    borderRadius: 30,
    bottom: spacing.lg,
    elevation: 6,
    height: 58,
    justifyContent: 'center',
    position: 'absolute',
    right: spacing.lg,
    shadowColor: colors.text,
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.22,
    shadowRadius: 5,
    width: 58,
  },
  modalRoot: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  modalBackdrop: {
    ...StyleSheet.absoluteFill,
    backgroundColor: '#10182B99',
  },
  modalSheet: {
    backgroundColor: colors.background,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    maxHeight: '90%',
    paddingBottom: Platform.OS === 'ios' ? spacing.xl : spacing.lg,
  },
  modalHeader: {
    alignItems: 'center',
    borderBottomColor: colors.border,
    borderBottomWidth: StyleSheet.hairlineWidth,
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  modalTitle: {
    color: colors.text,
    flex: 1,
    fontSize: 18,
    fontWeight: '800',
  },
  modalContent: {
    padding: spacing.lg,
    paddingBottom: spacing.xl,
  },
});
