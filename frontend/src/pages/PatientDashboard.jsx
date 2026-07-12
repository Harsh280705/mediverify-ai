import { Link } from 'react-router-dom';
import PageShell from '../components/PageShell';
import PrimaryButton from '../components/PrimaryButton';
import SectionCard from '../components/SectionCard';
import StatusBadge from '../components/StatusBadge';
import { useAuth } from '../hooks/useAuth';
import { QUICK_ACTIONS, ROUTE_PATHS, ROLES } from '../utils/constants';

export default function PatientDashboard() {
  const { currentUser, logout } = useAuth();

  return (
    <PageShell
      eyebrow="Patient Dashboard"
      title={`Welcome${currentUser?.name ? `, ${currentUser.name}` : ''}`}
      description="Your dashboard is role-aware and prepared for medication verification, timeline events, and upcoming reminders once those modules are added."
    >
      <div className="mb-6 flex flex-wrap items-center gap-3">
        <StatusBadge label={ROLES.PATIENT} tone="cyan" />
        <PrimaryButton onClick={logout}>Logout</PrimaryButton>
        <Link to={ROUTE_PATHS.CAREGIVER_DASHBOARD} className="text-sm text-slate-300 underline-offset-4 hover:text-white hover:underline">
          View caregiver route
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
            <li>Medication verification workflows</li>
            <li>Timeline event capture and review</li>
            <li>Document upload and storage integration</li>
            <li>Notification and reminder orchestration</li>
          </ul>
        </SectionCard>
      </div>
    </PageShell>
  );
}
