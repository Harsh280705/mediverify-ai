import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import PageShell from "../components/PageShell";
import PrimaryButton from "../components/PrimaryButton";
import SectionCard from "../components/SectionCard";
import StatusBadge from "../components/StatusBadge";
import TextField from "../components/TextField";
import { useAuth } from "../hooks/useAuth";
import { getLinkedPatients, linkPatient } from "../services/analyticsService";
import { ROLES, QUICK_ACTIONS } from "../utils/constants";

export default function CaregiverDashboard() {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();

  const [patients, setPatients] = useState([]);
  const [patientEmail, setPatientEmail] = useState("");
  const [loading, setLoading] = useState(true);
  const [linking, setLinking] = useState(false);
  const [linkError, setLinkError] = useState("");
  const [linkSuccess, setLinkSuccess] = useState("");

  const loadPatients = async () => {
    try {
      setLoading(true);
      const data = await getLinkedPatients();
      setPatients(data);
    } catch (err) {
      console.error("Failed to load caregiver patients", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPatients();
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
        loadPatients();
      }
    } catch (err) {
      setLinkError(err.response?.data?.detail || "Failed to link patient.");
    } finally {
      setLinking(false);
    }
  };

  return (
    <PageShell
      eyebrow="Caregiver Portal"
      title={`Welcome${currentUser?.name ? `, ${currentUser.name}` : ""}`}
      description="Connect with family members, manage care plans, and monitor real-time medication verification adherence logs."
    >
      <div className="mb-6 flex flex-wrap items-center gap-3">
        <StatusBadge label={ROLES.CAREGIVER.toUpperCase()} tone="emerald" />
        <PrimaryButton onClick={logout}>Logout</PrimaryButton>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Link Patient Column */}
        <div className="lg:col-span-1 space-y-6">
          <SectionCard title="Link Patient Account">
            <form onSubmit={handleLinkPatient} className="space-y-4">
              <p className="text-xs text-slate-400">
                Provide the email of the patient to link their medication schedule to your account.
              </p>
              <TextField
                label="Patient Email"
                type="email"
                value={patientEmail}
                onChange={(e) => setPatientEmail(e.target.value)}
                placeholder="family@example.com"
                required
              />
              {linkError && <p className="text-xs text-rose-300 font-semibold">{linkError}</p>}
              {linkSuccess && <p className="text-xs text-emerald-300 font-semibold">{linkSuccess}</p>}
              <PrimaryButton type="submit" disabled={linking} className="w-full">
                {linking ? "Linking..." : "Link Patient"}
              </PrimaryButton>
            </form>
          </SectionCard>

          <SectionCard title="Linked Family Panel">
            {loading ? (
              <div className="flex flex-col items-center justify-center py-4 text-slate-400 space-y-2 animate-pulse">
                <span className="text-xl">⏳</span>
                <p className="text-xs font-medium text-slate-350">Loading linked members...</p>
              </div>
            ) : patients.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-6 text-center text-slate-400 space-y-2">
                <span className="text-3xl">👥</span>
                <p className="text-xs font-semibold text-white">No Linked Members</p>
                <p className="text-[10px] text-slate-450 max-w-[160px]">Add family member's email above to link.</p>
              </div>
            ) : (
              <div className="divide-y divide-white/10">
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

        {/* Feature Actions Columns */}
        <div className="lg:col-span-2 space-y-6">
          <SectionCard title="Quick Resources">
            <div className="grid gap-4 sm:grid-cols-2">
              {QUICK_ACTIONS.map((action) => (
                <div
                  key={action}
                  className="rounded-xl border border-white/10 bg-white/5 p-4 text-sm text-slate-200"
                >
                  {action}
                </div>
              ))}
            </div>
          </SectionCard>

          <SectionCard title="Upcoming Collaborations">
            <ul className="space-y-3 text-sm text-slate-300">
              <li className="flex items-start gap-2">
                <span className="text-emerald-400 font-bold">•</span>
                <p><strong>SMS Alerts:</strong> Instant text messaging when linked patients miss critical evening doses.</p>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-emerald-400 font-bold">•</span>
                <p><strong>Audit Trails:</strong> Verification logs recording exact confidence levels and verification methods.</p>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-emerald-400 font-bold">•</span>
                <p><strong>Shared Document Vaults:</strong> Central storage for caregiver-patient prescription and dosage updates.</p>
              </li>
            </ul>
          </SectionCard>
        </div>
      </div>
    </PageShell>
  );
}
