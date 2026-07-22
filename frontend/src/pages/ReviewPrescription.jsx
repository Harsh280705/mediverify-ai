import { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import PageShell from '../components/PageShell';
import PrimaryButton from '../components/PrimaryButton';
import SectionCard from '../components/SectionCard';
import TextField from '../components/TextField';
import { useAuth } from '../hooks/useAuth';
import { apiClient } from '../services/api';
import { ROUTE_PATHS } from '../utils/constants';

const TIMING_OPTIONS = ['Morning', 'Afternoon', 'Evening', 'Night'];

export default function ReviewPrescription() {
  const location = useLocation();
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  
  const { extractedData, fileName } = location.state || {};

  const [patientName, setPatientName] = useState('');
  const [medications, setMedications] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (extractedData) {
      setPatientName(extractedData.patientName || currentUser?.name || '');
      setMedications(extractedData.medications || []);
    }
  }, [extractedData, currentUser]);

  if (!extractedData) {
    return (
      <PageShell
        eyebrow="Prescription Pipeline"
        title="Review Prescription"
        description="No prescription details found to review."
      >
        <div className="mx-auto max-w-md rounded-2xl border border-white/10 bg-white/5 p-8 text-center space-y-4">
          <p className="text-slate-300 text-sm">
            Please upload a prescription document first.
          </p>
          <Link
            to={ROUTE_PATHS.UPLOAD_PRESCRIPTION}
            className="inline-flex items-center justify-center rounded-xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
          >
            Go to Upload
          </Link>
        </div>
      </PageShell>
    );
  }

  const handleMedicationChange = (index, field, value) => {
    const updated = [...medications];
    updated[index] = { ...updated[index], [field]: value };
    setMedications(updated);
  };

  const handleTimingToggle = (medIndex, timing) => {
    const updated = [...medications];
    const timings = updated[medIndex].timings || [];
    if (timings.includes(timing)) {
      updated[medIndex].timings = timings.filter((t) => t !== timing);
    } else {
      updated[medIndex].timings = [...timings, timing];
    }
    setMedications(updated);
  };

  const handleAddMedication = () => {
    setMedications([
      ...medications,
      {
        medicineName: '',
        strength: '',
        frequency: 'Once daily',
        timings: ['Morning'],
        duration: '7 days',
        instructions: 'After food',
      },
    ]);
  };

  const handleDeleteMedication = (index) => {
    const updated = medications.filter((_, idx) => idx !== index);
    setMedications(updated);
  };

  const handleConfirm = async (e) => {
    e.preventDefault();
    if (!currentUser?.uid) {
      setError('You must be logged in as a patient to confirm prescription schedules.');
      return;
    }

    if (medications.length === 0) {
      setError('Please add at least one medication before confirming.');
      return;
    }

    // Validate medication names
    for (let i = 0; i < medications.length; i++) {
      if (!medications[i].medicineName.trim()) {
        setError(`Medication #${i + 1} is missing a name.`);
        return;
      }
    }

    setSubmitting(true);
    setError('');

    const payload = {
      patientId: currentUser.uid,
      patientName: patientName || currentUser.name || 'Anonymous Patient',
      medications: medications.map((med) => ({
        medicineName: med.medicineName.trim(),
        strength: med.strength.trim(),
        frequency: med.frequency.trim(),
        timings: med.timings,
        duration: med.duration.trim(),
        instructions: med.instructions.trim(),
      })),
    };

    try {
      await apiClient.post('/api/medications/confirm', payload);
      setSuccess(true);
      setTimeout(() => {
        navigate(ROUTE_PATHS.MEDICATION_LIST);
      }, 1500);
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Firestore write failed.';
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <PageShell
      eyebrow="Prescription Pipeline"
      title="Review Extracted Medications"
      description={`Source file: ${fileName || 'Uploaded Scan'}. Please audit and correct the extracted medication list before confirming.`}
    >
      <form onSubmit={handleConfirm} className="space-y-6">
        <SectionCard title="Patient Details">
          <div className="max-w-md">
            <TextField
              label="Patient Name"
              value={patientName}
              onChange={(e) => setPatientName(e.target.value)}
              placeholder="e.g. John Doe"
              required
            />
          </div>
        </SectionCard>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">Medications ({medications.length})</h2>
            <button
              type="button"
              onClick={handleAddMedication}
              className="inline-flex items-center justify-center rounded-xl border border-cyan-400/30 bg-cyan-950/20 px-4 py-2.5 text-sm font-semibold text-cyan-300 transition hover:bg-cyan-950/40 hover:text-white"
            >
              + Add Medicine
            </button>
          </div>

          {medications.length === 0 ? (
            <div className="rounded-2xl border border-white/5 bg-white/2 p-12 text-center text-slate-400">
              No medications listed. Click "+ Add Medicine" to define a medication course.
            </div>
          ) : (
            <div className="grid gap-6 md:grid-cols-2">
              {medications.map((med, idx) => (
                <div
                  key={idx}
                  className="relative rounded-2xl border border-white/10 bg-slate-950/40 p-5 shadow-soft backdrop-blur-md space-y-4"
                >
                  <button
                    type="button"
                    onClick={() => handleDeleteMedication(idx)}
                    className="absolute right-4 top-4 rounded-lg p-1.5 text-slate-400 hover:bg-rose-950/30 hover:text-rose-300 transition"
                    title="Delete medication"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={1.5}
                      stroke="currentColor"
                      className="h-5 w-5"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"
                      />
                    </svg>
                  </button>

                  <div className="pr-8 space-y-4">
                    <TextField
                      label="Medicine Name"
                      value={med.medicineName}
                      onChange={(e) => handleMedicationChange(idx, 'medicineName', e.target.value)}
                      placeholder="e.g. Amoxicillin"
                      required
                    />

                    <div className="grid grid-cols-2 gap-4">
                      <TextField
                        label="Strength"
                        value={med.strength}
                        onChange={(e) => handleMedicationChange(idx, 'strength', e.target.value)}
                        placeholder="e.g. 500mg"
                      />
                      <TextField
                        label="Duration"
                        value={med.duration}
                        onChange={(e) => handleMedicationChange(idx, 'duration', e.target.value)}
                        placeholder="e.g. 7 days"
                      />
                    </div>

                    <TextField
                      label="Frequency"
                      value={med.frequency}
                      onChange={(e) => handleMedicationChange(idx, 'frequency', e.target.value)}
                      placeholder="e.g. Twice daily"
                    />

                    <div className="space-y-2">
                      <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                        Timings
                      </span>
                      <div className="flex flex-wrap gap-2">
                        {TIMING_OPTIONS.map((time) => {
                          const isChecked = med.timings?.includes(time);
                          return (
                            <button
                              key={time}
                              type="button"
                              onClick={() => handleTimingToggle(idx, time)}
                              className={`rounded-lg px-3 py-1.5 text-xs font-medium border transition ${
                                isChecked
                                  ? 'bg-cyan-500/20 border-cyan-400 text-cyan-200'
                                  : 'bg-white/5 border-white/10 text-slate-300 hover:border-white/20'
                              }`}
                            >
                              {time}
                            </button>
                          );
                        })}
                      </div>
                    </div>

                    <TextField
                      label="Instructions"
                      value={med.instructions}
                      onChange={(e) => handleMedicationChange(idx, 'instructions', e.target.value)}
                      placeholder="e.g. After food"
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {error && (
          <div className="rounded-xl border border-rose-500/20 bg-rose-500/10 p-4 text-sm text-rose-300">
            {error}
          </div>
        )}

        {success && (
          <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-4 text-sm text-emerald-300">
            Schedules generated successfully! Redirecting to Medication List...
          </div>
        )}

        <div className="flex items-center justify-end gap-3">
          <Link
            to={ROUTE_PATHS.UPLOAD_PRESCRIPTION}
            className="rounded-xl px-5 py-3 text-sm font-semibold text-slate-400 hover:text-white transition"
          >
            Cancel
          </Link>
          <PrimaryButton
            type="submit"
            disabled={submitting || success}
          >
            {submitting ? 'Scheduling...' : 'Confirm & Save Schedule'}
          </PrimaryButton>
        </div>
      </form>
    </PageShell>
  );
}
