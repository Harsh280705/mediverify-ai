import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import PageShell from "../components/PageShell";
import PrimaryButton from "../components/PrimaryButton";
import SectionCard from "../components/SectionCard";
import StatusBadge from "../components/StatusBadge";
import TextField from "../components/TextField";
import { useAuth } from "../hooks/useAuth";
import { getDoctorAlerts, getLinkedPatients, linkPatient, runAdherenceAudit } from "../services/analyticsService";
import { ROLES } from "../utils/constants";

export default function DoctorDashboard() {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();

  const [alerts, setAlerts] = useState([]);
  const [patients, setPatients] = useState([]);
  const [patientEmail, setPatientEmail] = useState("");
  const [loading, setLoading] = useState(true);
  const [linking, setLinking] = useState(false);
  const [linkError, setLinkError] = useState("");
  const [linkSuccess, setLinkSuccess] = useState("");

  const loadData = async () => {
    try {
      setLoading(true);
      const [alertsData, patientsData] = await Promise.all([
        getDoctorAlerts(),
        getLinkedPatients()
      ]);
      setAlerts(alertsData);
      setPatients(patientsData);
    } catch (err) {
      console.error("Failed to load doctor dashboard data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleLinkPatient = async (e) => {
    e.preventDefault();
    if (!patientEmail.trim()) return;
    setLinking(true);
    setLinkError("");
    setLinkSuccess("");
    try {
      const res = await linkPatient(patientEmail.trim());
      if (res.success) {
        setLinkSuccess(`Successfully linked patient: ${res.patient.name}`);
        setPatientEmail("");
        loadData();
      }
    } catch (err) {
      setLinkError(err.response?.data?.detail || "Failed to link patient.");
    } finally {
      setLinking(false);
    }
  };

  const handleRunAudit = async () => {
    try {
      await runAdherenceAudit();
      loadData();
      alert("Adherence audit completed! Dashboard refreshed.");
    } catch (err) {
      console.error(err);
      alert("Failed to run adherence audit.");
    }
  };

  return (
    <PageShell
      eyebrow="Doctor Panel"
      title={`Welcome, Dr. ${currentUser?.name || "Doctor"}`}
      description="Monitor patient adherence logs, view high-risk medication alerts, and review detailed compliance analytics."
    >
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3">
          <StatusBadge label={ROLES.DOCTOR.toUpperCase()} tone="rose" />
          <PrimaryButton onClick={handleRunAudit}>🔄 Run Adherence Audit</PrimaryButton>
          <PrimaryButton onClick={logout}>Logout</PrimaryButton>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Assign Patient Box */}
        <div className="lg:col-span-1">
          <SectionCard title="Assign Patient">
            <form onSubmit={handleLinkPatient} className="space-y-4">
              <p className="text-xs text-slate-400">
                Enter the registered email of the patient to assign them to your panel.
              </p>
              <TextField
                label="Patient Email"
                type="email"
                value={patientEmail}
                onChange={(e) => setPatientEmail(e.target.value)}
                placeholder="patient@example.com"
                required
              />
              {linkError && <p className="text-xs text-rose-300 font-semibold">{linkError}</p>}
              {linkSuccess && <p className="text-xs text-emerald-300 font-semibold">{linkSuccess}</p>}
              <PrimaryButton type="submit" disabled={linking} className="w-full">
                {linking ? "Assigning..." : "Assign Patient"}
              </PrimaryButton>
            </form>
          </SectionCard>

          <div className="mt-6">
            <SectionCard title="My Patient Panel">
              {loading ? (
                <div className="flex flex-col items-center justify-center py-4 text-slate-400 space-y-2 animate-pulse">
                  <span className="text-xl">⏳</span>
                  <p className="text-xs font-medium text-slate-350">Loading patients...</p>
                </div>
              ) : patients.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-6 text-center text-slate-400 space-y-2">
                  <span className="text-3xl">👥</span>
                  <p className="text-xs font-semibold text-white">No Patients Assigned</p>
                  <p className="text-[10px] text-slate-450 max-w-[160px]">Assign a patient above to monitor.</p>
                </div>
              ) : (
                <div className="divide-y divide-white/15">
                  {patients.map((p) => (
                    <div
                      key={p.uid}
                      onClick={() => navigate(`/patient/analytics/${p.uid}`)}
                      className="group flex items-center justify-between py-3 cursor-pointer hover:bg-white/5 px-2 rounded-lg transition"
                    >
                      <div>
                        <p className="text-sm font-semibold text-white group-hover:text-cyan-300 transition">
                          {p.name}
                        </p>
                        <p className="text-xs text-slate-400">{p.email}</p>
                      </div>
                      <span className="text-xs text-slate-400 group-hover:text-white transition">View 📊</span>
                    </div>
                  ))}
                </div>
              )}
            </SectionCard>
          </div>
        </div>

        {/* High-Risk Alerts List */}
        <div className="lg:col-span-2">
          <SectionCard title="⚠️ Active High-Risk Adherence Alerts (Missed Doses ≥ 2)">
            {loading ? (
              <div className="flex flex-col items-center justify-center py-12 text-slate-400 space-y-3 animate-pulse">
                <span className="text-3xl">⏳</span>
                <p className="text-sm font-medium text-slate-300">Fetching adherence alerts...</p>
              </div>
            ) : alerts.length === 0 ? (
              <div className="flex h-48 flex-col items-center justify-center rounded-xl border border-dashed border-white/10 bg-white/5 text-slate-500">
                <span className="text-2xl">🎉</span>
                <p className="mt-2 text-sm text-slate-400">All patients are compliant. No active alerts.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full border-collapse text-left text-sm text-slate-200">
                  <thead>
                    <tr className="border-b border-white/10 text-xs font-semibold uppercase text-slate-400">
                      <th className="py-3 px-4">Patient</th>
                      <th className="py-3 px-4">Missed Doses</th>
                      <th className="py-3 px-4">Last Taken</th>
                      <th className="py-3 px-4">Adherence Rate</th>
                      <th className="py-3 px-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {alerts.map((alert) => (
                      <tr key={alert.patientId} className="hover:bg-white/5 transition">
                        <td className="py-3 px-4 font-medium text-white">{alert.patientName}</td>
                        <td className="py-3 px-4 text-rose-300 font-bold">{alert.missedCount} Doses</td>
                        <td className="py-3 px-4 text-slate-400">
                          {alert.lastTaken ? new Date(alert.lastTaken).toLocaleString() : "Never"}
                        </td>
                        <td className="py-3 px-4">
                          <span
                            className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                              alert.adherencePercentage >= 80
                                ? "bg-emerald-500/10 text-emerald-300 border border-emerald-500/20"
                                : alert.adherencePercentage >= 50
                                ? "bg-amber-500/10 text-amber-300 border border-amber-500/20"
                                : "bg-rose-500/10 text-rose-300 border border-rose-500/20"
                            }`}
                          >
                            {alert.adherencePercentage}%
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right">
                          <button
                            onClick={() => navigate(`/patient/analytics/${alert.patientId}`)}
                            className="text-xs font-semibold text-cyan-300 hover:text-white underline"
                          >
                            Analyze
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </SectionCard>
        </div>
      </div>
    </PageShell>
  );
}
