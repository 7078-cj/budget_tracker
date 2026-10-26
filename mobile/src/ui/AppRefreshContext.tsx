import { createContext, useContext, useMemo, useState } from 'react';
import type { PropsWithChildren } from 'react';

interface AppRefreshContextValue {
  refreshKey: number;
  refresh: () => void;
}

const AppRefreshContext = createContext<AppRefreshContextValue | null>(null);

export function AppRefreshProvider({ children }: PropsWithChildren) {
  const [refreshKey, setRefreshKey] = useState(0);
  const value = useMemo(
    () => ({
      refreshKey,
      refresh: () => setRefreshKey((current) => current + 1),
    }),
    [refreshKey],
  );
  return <AppRefreshContext.Provider value={value}>{children}</AppRefreshContext.Provider>;
}

export function useAppRefresh(): AppRefreshContextValue {
  const context = useContext(AppRefreshContext);
  if (!context) throw new Error('useAppRefresh must be used inside AppRefreshProvider.');
  return context;
}
