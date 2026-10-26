import { TransactionsScreen } from '../screens/TransactionsScreen';
import { useAppRefresh } from '../ui/AppRefreshContext';

export default function TransactionsRoute() {
  const { refreshKey, refresh } = useAppRefresh();
  return <TransactionsScreen key={refreshKey} onChanged={refresh} />;
}
