import { DashboardScreen } from '../screens/DashboardScreen';
import { useAppRefresh } from '../ui/AppRefreshContext';

export default function DashboardRoute() {
  const { refreshKey, refresh } = useAppRefresh();
  return (
    <DashboardScreen
      key={refreshKey}
      refreshKey={refreshKey}
      onChanged={refresh}
    />
  );
}
