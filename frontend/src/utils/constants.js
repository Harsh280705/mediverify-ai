export const ROLES = Object.freeze({
  PATIENT: 'patient',
  CAREGIVER: 'caregiver',
});

export const ROUTE_PATHS = Object.freeze({
  LANDING: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  PATIENT_DASHBOARD: '/patient',
  CAREGIVER_DASHBOARD: '/caregiver',
  DASHBOARD: '/dashboard',
});

export const FIRESTORE_COLLECTIONS = Object.freeze({
  USERS: 'users',
  PATIENTS: 'patients',
  CAREGIVERS: 'caregivers',
  MEDICATIONS: 'medications',
  VERIFICATION_SESSIONS: 'verification_sessions',
  DOCUMENTS: 'documents',
  TIMELINE_EVENTS: 'timeline_events',
  NOTIFICATIONS: 'notifications',
  LOGS: 'logs',
});

export const QUICK_ACTIONS = Object.freeze([
  'Connect medication records',
  'Review adherence timeline',
  'Upload supporting documents',
  'Monitor verification status',
]);

export function getDashboardPath(role) {
  return role === ROLES.CAREGIVER ? ROUTE_PATHS.CAREGIVER_DASHBOARD : ROUTE_PATHS.PATIENT_DASHBOARD;
}
