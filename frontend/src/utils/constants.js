export const ROLES = Object.freeze({
  PATIENT: "patient",
  CAREGIVER: "caregiver",
  DOCTOR: "doctor",
});

export const ROUTE_PATHS = Object.freeze({
  LANDING: "/",
  LOGIN: "/login",
  REGISTER: "/register",

  DASHBOARD: "/dashboard",

  PATIENT_DASHBOARD: "/patient",
  CAREGIVER_DASHBOARD: "/caregiver",
  DOCTOR_DASHBOARD: "/doctor",

  UPLOAD_PRESCRIPTION: "/patient/upload-prescription",
  REVIEW_PRESCRIPTION: "/patient/review-prescription",
  MEDICATION_LIST: "/patient/medications",
  PATIENT_ANALYTICS: "/patient/analytics/:patientId",

  REMINDERS: "/reminders",

  // Dynamic route for verification
  VERIFY_MEDICINE: "/verify/:scheduleId",
});


export const FIRESTORE_COLLECTIONS = Object.freeze({
  USERS: "users",
  PATIENTS: "patients",
  CAREGIVERS: "caregivers",
  MEDICATIONS: "medications",
  VERIFICATION_SESSIONS: "verification_sessions",
  DOCUMENTS: "documents",
  TIMELINE_EVENTS: "timeline_events",
  NOTIFICATIONS: "notifications",
  LOGS: "logs",
});

export const QUICK_ACTIONS = Object.freeze([
  "Connect medication records",
  "Review adherence timeline",
  "Upload supporting documents",
  "Monitor verification status",
]);

export function getDashboardPath(role) {
  if (role === ROLES.DOCTOR) {
    return ROUTE_PATHS.DOCTOR_DASHBOARD;
  }
  return role === ROLES.CAREGIVER
    ? ROUTE_PATHS.CAREGIVER_DASHBOARD
    : ROUTE_PATHS.PATIENT_DASHBOARD;
}


// Helper to build a verification URL
export function buildVerifyRoute(scheduleId) {
  return `/verify/${scheduleId}`;
}