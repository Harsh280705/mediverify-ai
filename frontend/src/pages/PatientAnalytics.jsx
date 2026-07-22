import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import PageShell from "../components/PageShell";
import PrimaryButton from "../components/PrimaryButton";
import SectionCard from "../components/SectionCard";
import { getPatientAnalytics } from "../services/analyticsService";
import { useAuth } from "../hooks/useAuth";

export default function PatientAnalytics() {
  const { patientId } = useParams();
  const { currentUser } = useAuth();
  const navigate = useNavigate();

  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadAnalytics() {
      try {
        setLoading(true);
        const data = await getPatientAnalytics(patientId);
        setStats(data);
      } catch (err) {
        console.error(err);
        setError("Failed to load adherence analytics.");
      } finally {
        setLoading(false);
      }
    }
    loadAnalytics();
  }, [patientId]);

  if (loading) {
    return (
      <PageShell eyebrow="Analytics" title="Loading Compliance Stats..." description="Aggregating streak data and compliance rates.">
        <p className="text-slate-400">Please wait while we query Firestore schedules...</p>
      </PageShell>
    );
  }

  if (error) {
    return (
      <PageShell eyebrow="Analytics" title="Error" description={error}>
        <PrimaryButton onClick={() => navigate(-1)}>Go Back</PrimaryButton>
      </PageShell>
    );
  }

  return (
    <PageShell
      eyebrow="Adherence Dashboard"
      title="Medication Adherence Analytics"
      description={`Detailed insight into compliance statistics for the patient. Current streak and adherence percentages.`}
    >
      <div className="mb-6">
        <PrimaryButton onClick={() => navigate(-1)}>← Back</PrimaryButton>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {/* Current Streak Card */}
        <div className="relative overflow-hidden rounded-2xl border border-orange-500/20 bg-gradient-to-br from-orange-500/10 to-orange-500/0 p-6 shadow-soft">
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold uppercase tracking-wider text-orange-400">Current Streak</span>
            <span className="text-2xl">🔥</span>
          </div>
          <p className="mt-4 text-4xl font-extrabold text-white">{stats.streaks.current} Days</p>
          <p className="mt-1 text-xs text-slate-400">Consecutive days fully compliant</p>
        </div>

        {/* Longest Streak Card */}
        <div className="relative overflow-hidden rounded-2xl border border-cyan-500/20 bg-gradient-to-br from-cyan-500/10 to-cyan-500/0 p-6 shadow-soft">
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold uppercase tracking-wider text-cyan-400">Longest Streak</span>
            <span className="text-2xl">🏆</span>
          </div>
          <p className="mt-4 text-4xl font-extrabold text-white">{stats.streaks.longest} Days</p>
          <p className="mt-1 text-xs text-slate-400">All-time record streak</p>
        </div>

        {/* Weekly Adherence */}
        <div className="relative overflow-hidden rounded-2xl border border-emerald-500/20 bg-gradient-to-br from-emerald-500/10 to-emerald-500/0 p-6 shadow-soft">
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold uppercase tracking-wider text-emerald-400">Weekly Adherence</span>
            <span className="text-2xl">📅</span>
          </div>
          <p className="mt-4 text-4xl font-extrabold text-white">{stats.adherence.weekly}%</p>
          <div className="mt-2 h-2 w-full rounded-full bg-white/10">
            <div
              className="h-full rounded-full bg-emerald-500"
              style={{ width: `${stats.adherence.weekly}%` }}
            ></div>
          </div>
          <p className="mt-1 text-xs text-slate-400">Compliance over last 7 days</p>
        </div>

        {/* Monthly Adherence */}
        <div className="relative overflow-hidden rounded-2xl border border-indigo-500/20 bg-gradient-to-br from-indigo-500/10 to-indigo-500/0 p-6 shadow-soft">
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold uppercase tracking-wider text-indigo-400">Monthly Adherence</span>
            <span className="text-2xl">📊</span>
          </div>
          <p className="mt-4 text-4xl font-extrabold text-white">{stats.adherence.monthly}%</p>
          <div className="mt-2 h-2 w-full rounded-full bg-white/10">
            <div
              className="h-full rounded-full bg-indigo-500"
              style={{ width: `${stats.adherence.monthly}%` }}
            ></div>
          </div>
          <p className="mt-1 text-xs text-slate-400">Compliance over last 30 days</p>
        </div>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        {/* Today's Stats Checklist */}
        <SectionCard title="Today's Dose Metrics">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="rounded-xl border border-white/5 bg-white/5 p-4">
              <span className="text-xl">✅</span>
              <p className="text-sm font-medium text-slate-400 mt-1">Taken</p>
              <p className="text-2xl font-extrabold text-emerald-400 mt-2">{stats.today.taken}</p>
            </div>
            <div className="rounded-xl border border-white/5 bg-white/5 p-4">
              <span className="text-xl">⏳</span>
              <p className="text-sm font-medium text-slate-400 mt-1">Pending</p>
              <p className="text-2xl font-extrabold text-cyan-400 mt-2">{stats.today.pending}</p>
            </div>
            <div className="rounded-xl border border-white/5 bg-white/5 p-4">
              <span className="text-xl">❌</span>
              <p className="text-sm font-medium text-slate-400 mt-1">Missed</p>
              <p className="text-2xl font-extrabold text-rose-400 mt-2">{stats.today.missed}</p>
            </div>
          </div>

          <div className="mt-6 space-y-4">
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider">Overall Compliance</h4>
            <div className="flex items-center gap-4">
              <div className="flex-1 h-3 rounded-full bg-white/10">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-cyan-400"
                  style={{ width: `${stats.adherence.overall}%` }}
                ></div>
              </div>
              <span className="text-lg font-bold text-white">{stats.adherence.overall}%</span>
            </div>
            <p className="text-xs text-slate-400">Total compliance rate calculated for all historical scheduled medication doses.</p>
          </div>
        </SectionCard>

        {/* Informational Guidelines Card */}
        <SectionCard title="Adherence Recommendations">
          <ul className="space-y-4 text-sm text-slate-300">
            <li className="flex items-start gap-3">
              <span className="text-indigo-400 font-bold">•</span>
              <p>
                <strong>Consistent Schedule:</strong> Aligning dosing times with daily milestones (like morning coffee or breakfast) is proven to increase compliance by up to 40%.
              </p>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-indigo-400 font-bold">•</span>
              <p>
                <strong>Family Notifications:</strong> If the patient misses two consecutive scheduled doses, an alert is automatically forwarded to the assigned Caregiver/Doctor dashboard.
              </p>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-indigo-400 font-bold">•</span>
              <p>
                <strong>AI Verification:</strong> Encourage the patient to hold the medicine box/strip in front of the camera. The system reads and confirms it, reducing administration errors.
              </p>
            </li>
          </ul>
        </SectionCard>
      </div>
    </PageShell>
  );
}
