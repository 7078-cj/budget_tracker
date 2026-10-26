import { Tabs } from 'expo-router';
import { SQLiteProvider } from 'expo-sqlite';
import { StatusBar } from 'expo-status-bar';
import { initializeDatabase } from '../data/database';
import { AppRefreshProvider } from '../ui/AppRefreshContext';
import { AppIcon } from '../ui/components';
import { colors } from '../ui/theme';

export default function RootLayout() {
  return (
    <SQLiteProvider databaseName="budget-tracker.db" onInit={initializeDatabase}>
      <AppRefreshProvider>
        <StatusBar style="dark" />
        <Tabs
          screenOptions={{
            headerTitle: 'Budget Tracker',
            headerStyle: { backgroundColor: colors.card },
            headerTintColor: colors.text,
            tabBarActiveTintColor: colors.primary,
            tabBarInactiveTintColor: colors.muted,
            tabBarLabelPosition: 'below-icon',
            tabBarIconStyle: { marginTop: 4 },
            tabBarStyle: {
              backgroundColor: colors.card,
              borderTopColor: colors.border,
              height: 62,
              paddingBottom: 5,
              paddingTop: 2,
            },
          }}
        >
          <Tabs.Screen
            name="index"
            options={{
              title: 'Dashboard',
              tabBarIcon: ({ color, size }) => <AppIcon name="dashboard" color={color} size={size} />,
            }}
          />
          <Tabs.Screen
            name="transactions"
            options={{
              title: 'Transactions',
              tabBarIcon: ({ color, size }) => <AppIcon name="transactions" color={color} size={size} />,
            }}
          />
          <Tabs.Screen
            name="accounts"
            options={{
              title: 'Accounts',
              tabBarIcon: ({ color, size }) => <AppIcon name="accounts" color={color} size={size} />,
            }}
          />
          <Tabs.Screen
            name="allocation"
            options={{
              title: 'Allocation',
              tabBarIcon: ({ color, size }) => <AppIcon name="allocation" color={color} size={size} />,
            }}
          />
        </Tabs>
      </AppRefreshProvider>
    </SQLiteProvider>
  );
}
