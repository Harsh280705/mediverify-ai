import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

import PageShell from "../components/PageShell";
import PrimaryButton from "../components/PrimaryButton";
import SectionCard from "../components/SectionCard";
import StatusBadge from "../components/StatusBadge";

import { useAuth } from "../hooks/useAuth";
import { getDashboard } from "../services/dashboard";

import {
  QUICK_ACTIONS,
  ROUTE_PATHS,
  ROLES,
  buildVerifyRoute,
} from "../utils/constants";

export default function PatientDashboard() {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();

  const [todaySchedule, setTodaySchedule] = useState([]);
  const [loadingSchedule, setLoadingSchedule] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      if (!currentUser?.uid) return;

      try {
        const data = await getDashboard(currentUser.uid);

        // Local date (avoids UTC mismatch)
        const now = new Date();

        const today =
          now.getFullYear() +
          "-" +
          String(now.getMonth() + 1).padStart(2, "0") +
          "-" +
          String(now.getDate()).padStart(2, "0");

        const todayData = data.schedules.filter(
          (schedule) => schedule.scheduledDate === today
        );

        setTodaySchedule(todayData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingSchedule(false);
      }
    }

    loadDashboard();
  }, [currentUser]);

  return (
    <PageShell
      eyebrow="Patient Dashboard"
      title={`Welcome${currentUser?.name ? `, ${currentUser.name}` : ""}`}
      description="View today's medicines and verify each dose before marking it as taken."
    >
      <div className="mb-6 flex flex-wrap items-center gap-3">
        <StatusBadge label={ROLES.PATIENT} tone="cyan" />

        <PrimaryButton
          onClick={() => navigate(ROUTE_PATHS.UPLOAD_PRESCRIPTION)}
        >
          Upload Prescription
        </PrimaryButton>

        <PrimaryButton
          onClick={() => navigate(ROUTE_PATHS.MEDICATION_LIST)}
        >
          Medication List
        </PrimaryButton>

        <PrimaryButton
          onClick={() => navigate(ROUTE_PATHS.REMINDERS)}
        >
          🔔 Reminder Settings
        </PrimaryButton>

        <PrimaryButton
          onClick={() => navigate(ROUTE_PATHS.PATIENT_ANALYTICS.replace(":patientId", currentUser.uid))}
        >
          📊 Adherence Analytics
        </PrimaryButton>

        <PrimaryButton onClick={logout}>
          Logout
        </PrimaryButton>


        <Link
          to={ROUTE_PATHS.CAREGIVER_DASHBOARD}
          className="text-sm text-slate-300 underline-offset-4 hover:text-white hover:underline"
        >
          View caregiver route
        </Link>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">

        <SectionCard title="Quick Actions">
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

        <SectionCard title="Today's Medicines">

          {loadingSchedule ? (

            <p>Loading today's medicines...</p>

          ) : todaySchedule.length === 0 ? (

            <p>No medicines scheduled for today.</p>

          ) : (

            todaySchedule.map((item) => (

              <div
                key={item.id}
                className="flex items-center justify-between border-b border-white/10 py-3"
              >

                <div>
                  <p className="font-medium text-white">
                    {item.medicineName}
                  </p>

                  <p className="text-sm text-slate-400">
                    {item.timing}
                  </p>

                  <p className="text-xs text-slate-500">
                    {item.scheduledDate}
                  </p>
                </div>

                <div className="flex items-center gap-3">

                  <StatusBadge
                    label={item.status}
                    tone={
                      item.status === "Taken"
                        ? "green"
                        : "cyan"
                    }
                  />

                  {item.status !== "Taken" && (
                    <PrimaryButton
                      onClick={() =>
                        navigate(
                          buildVerifyRoute(item.id),
                          {
                            state: {
                              schedule: item,
                            },
                          }
                        )
                      }
                    >
                      Verify
                    </PrimaryButton>
                  )}

                </div>

              </div>

            ))

          )}

        </SectionCard>

      </div>
    </PageShell>
  );
}