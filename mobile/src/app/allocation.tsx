import { AllocationScreen } from '../screens/AllocationScreen';
import { useAppRefresh } from '../ui/AppRefreshContext';

export default function AllocationRoute() {
  const { refreshKey, refresh } = useAppRefresh();
  return <AllocationScreen key={refreshKey} onChanged={refresh} />;
}
