import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import PageShell from '../components/PageShell';
import PrimaryButton from '../components/PrimaryButton';
import SectionCard from '../components/SectionCard';
import StatusBadge from '../components/StatusBadge';
import { useAuth } from '../hooks/useAuth';
import { apiClient } from '../services/api';
import { ROUTE_PATHS } from '../utils/constants';

export default function MedicationList() {
  const navigate = useNavigate();
  const { currentUser } = useAuth();

  const [medications, setMedications] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchData() {
      if (!currentUser?.uid) return;

      try {
        setLoading(true);
        setError('');

        const [medsRes, schedRes] = await Promise.all([
          apiClient.get(`/api/medications?patientId=${currentUser.uid}`),
          apiClient.get(`/api/schedule?patientId=${currentUser.uid}`),
        ]);

        setMedications(medsRes.data);
        setSchedules(schedRes.data);
      } catch (err) {
        const msg = err.response?.data?.detail || err.message || 'Failed to fetch medication details.';
        setError(msg);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [currentUser]);

  // Group schedule items by scheduledDate
  const groupedSchedules = schedules.reduce((acc, item) => {
    const dateStr = item.scheduledDate;
    if (!acc[dateStr]) {
      acc[dateStr] = [];
    }
    acc[dateStr].push(item);
    return acc;
  }, {});

  const sortedDates = Object.keys(groupedSchedules).sort((a, b) => new Date(a) - new Date(b));

  const formatHeaderDate = (dateStr) => {
    const dateObj = new Date(dateStr);
    const options = { weekday: 'short', month: 'short', day: 'numeric' };
    
    // Check if it matches today or tomorrow in local time
    const todayStr = new Date().toISOString().split('T')[0];
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const tomorrowStr = tomorrow.toISOString().split('T')[0];

    if (dateStr === todayStr) {
      return `Today (${dateObj.toLocaleDateString(undefined, options)})`;
    } else if (dateStr === tomorrowStr) {
      return `Tomorrow (${dateObj.toLocaleDateString(undefined, options)})`;
    }
    return dateObj.toLocaleDateString(undefined, options);
  };

  return (
    <PageShell
      eyebrow="Adherence & Schedule"
      title="Medications & Schedules"
      description="View your active medication courses and generated daily dosage timeline."
    >
      <div className="mb-6 flex flex-wrap items-center gap-3">
        <PrimaryButton onClick={() => navigate(ROUTE_PATHS.UPLOAD_PRESCRIPTION)}>
          + Upload New Prescription
        </PrimaryButton>
        <Link
          to={ROUTE_PATHS.PATIENT_DASHBOARD}
          className="text-sm text-slate-300 underline-offset-4 hover:text-white hover:underline ml-2"
        >
          Go to Dashboard
        </Link>
      </div>

      {error && (
        <div className="mb-6 rounded-xl border border-rose-500/20 bg-rose-500/10 p-4 text-sm text-rose-300">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex h-64 items-center justify-center">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-cyan-400/20 border-t-cyan-400"></div>
        </div>
      ) : (
        <div className="grid gap-8 lg:grid-cols-3">
          {/* Daily Schedule List (Takes 2 columns on large screens) */}
          <div className="lg:col-span-2 space-y-6">
            <h2 className="text-xl font-semibold text-white tracking-wide">Dosage Timeline</h2>

            {sortedDates.length === 0 ? (
              <div className="rounded-2xl border border-white/5 bg-white/2 p-12 text-center text-slate-400">
                No schedule entries generated. Upload a prescription to start scheduling.
              </div>
            ) : (
              <div className="space-y-6">
                {sortedDates.map((dateStr) => (
                  <div key={dateStr} className="space-y-3">
                    <h3 className="text-sm font-semibold text-cyan-300 uppercase tracking-wider">
                      {formatHeaderDate(dateStr)}
                    </h3>
                    <div className="space-y-2">
                      {groupedSchedules[dateStr].map((item) => (
                        <div
                          key={item.id}
                          className="flex items-center justify-between rounded-xl border border-white/5 bg-slate-950/40 p-4 shadow-soft backdrop-blur"
                        >
                          <div className="flex items-center gap-4">
                            <span className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-cyan-500/10 text-xs font-semibold text-cyan-300">
                              {item.timing.substring(0, 3)}
                            </span>
                            <div>
                              <h4 className="text-sm font-medium text-white">
                                {item.medicineName}{' '}
                                {item.strength && (
                                  <span className="text-xs text-slate-400">({item.strength})</span>
                                )}
                              </h4>
                              <p className="text-xs text-slate-400">Time of dose: {item.timing}</p>
                            </div>
                          </div>
                          <StatusBadge label={item.status} tone={item.status === 'Pending' ? 'slate' : 'green'} />
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Active Medications courses list (Takes 1 column on large screens) */}
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-white tracking-wide">Active Courses</h2>

            {medications.length === 0 ? (
              <div className="rounded-2xl border border-white/5 bg-white/2 p-12 text-center text-slate-400">
                No active medication courses.
              </div>
            ) : (
              <div className="space-y-4">
                {medications.map((med) => (
                  <SectionCard key={med.id} title={med.medicineName}>
                    <div className="text-xs text-slate-300 space-y-2">
                      {med.strength && (
                        <p>
                          <strong className="text-slate-400">Strength:</strong> {med.strength}
                        </p>
                      )}
                      {med.frequency && (
                        <p>
                          <strong className="text-slate-400">Frequency:</strong> {med.frequency}
                        </p>
                      )}
                      {med.timings && med.timings.length > 0 && (
                        <p>
                          <strong className="text-slate-400">Timings:</strong> {med.timings.join(', ')}
                        </p>
                      )}
                      {med.duration && (
                        <p>
                          <strong className="text-slate-400">Duration:</strong> {med.duration}
                        </p>
                      )}
                      {med.instructions && (
                        <p>
                          <strong className="text-slate-400">Instructions:</strong> {med.instructions}
                        </p>
                      )}
                      <div className="pt-2 flex items-center justify-between border-t border-white/5">
                        <span className="text-slate-500">Course Status</span>
                        <StatusBadge label={med.status} tone="cyan" />
                      </div>
                    </div>
                  </SectionCard>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </PageShell>
  );
}
