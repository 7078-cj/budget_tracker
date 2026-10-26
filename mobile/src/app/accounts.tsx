import { AccountsScreen } from '../screens/AccountsScreen';
import { useAppRefresh } from '../ui/AppRefreshContext';

export default function AccountsRoute() {
  const { refreshKey, refresh } = useAppRefresh();
  return <AccountsScreen key={refreshKey} onChanged={refresh} />;
}
