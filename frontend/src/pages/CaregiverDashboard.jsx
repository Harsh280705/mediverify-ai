import { Link } from 'react-router-dom';
import PageShell from '../components/PageShell';
import PrimaryButton from '../components/PrimaryButton';
import SectionCard from '../components/SectionCard';
import StatusBadge from '../components/StatusBadge';
import { useAuth } from '../hooks/useAuth';
import { QUICK_ACTIONS, ROUTE_PATHS, ROLES } from '../utils/constants';

export default function CaregiverDashboard() {
  const { currentUser, logout } = useAuth();

  return (
    <PageShell
      eyebrow="Caregiver Dashboard"
      title={`Welcome${currentUser?.name ? `, ${currentUser.name}` : ''}`}
      description="This dashboard is ready for future family and caregiver collaboration features while keeping the foundation lean."
    >
      <div className="mb-6 flex flex-wrap items-center gap-3">
        <StatusBadge label={ROLES.CAREGIVER} tone="emerald" />
        <PrimaryButton onClick={logout}>Logout</PrimaryButton>
        <Link to={ROUTE_PATHS.PATIENT_DASHBOARD} className="text-sm text-slate-300 underline-offset-4 hover:text-white hover:underline">
          View patient route
        </Link>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <SectionCard title="Quick Actions">
          <div className="grid gap-4 sm:grid-cols-2">
            {QUICK_ACTIONS.map((action) => (
              <div key={action} className="rounded-xl border border-white/10 bg-white/5 p-4 text-sm text-slate-200">
                {action}
              </div>
            ))}
          </div>
        </SectionCard>
        <SectionCard title="Upcoming Features">
          <ul className="space-y-3">
            <li>Care plan monitoring views</li>
            <li>Shared verification timelines</li>
            <li>Document review and audit trails</li>
            <li>Escalation and adherence insights</li>
          </ul>
        </SectionCard>
      </div>
    </PageShell>
  );
}
