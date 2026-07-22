import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import Landing from '../pages/Landing';
import Login from '../pages/Login';
import Register from '../pages/Register';
import PatientDashboard from '../pages/PatientDashboard';
import CaregiverDashboard from '../pages/CaregiverDashboard';
import UploadPrescription from '../pages/UploadPrescription';
import ReviewPrescription from '../pages/ReviewPrescription';
import MedicationList from '../pages/MedicationList';
import NotFound from '../pages/NotFound';
import { useAuth } from '../hooks/useAuth';
import { ProtectedRoute, PublicRoute } from './ProtectedRoute';
import { ROLES, ROUTE_PATHS } from '../utils/constants';
import ReminderSettings from "../pages/ReminderSettings";
import VerifyMedicine from "../pages/VerifyMedicine";
import DoctorDashboard from "../pages/DoctorDashboard";
import PatientAnalytics from "../pages/PatientAnalytics";


function DashboardRedirect() {
  const { currentUser } = useAuth();
  let destination = ROUTE_PATHS.PATIENT_DASHBOARD;
  if (currentUser?.role === ROLES.CAREGIVER) {
    destination = ROUTE_PATHS.CAREGIVER_DASHBOARD;
  } else if (currentUser?.role === ROLES.DOCTOR) {
    destination = ROUTE_PATHS.DOCTOR_DASHBOARD;
  }

  return <Navigate to={destination} replace />;
}


export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path={ROUTE_PATHS.LANDING}
          element={
            <PublicRoute>
              <Landing />
            </PublicRoute>
          }
        />
        <Route
          path={ROUTE_PATHS.LOGIN}
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />
        <Route
          path={ROUTE_PATHS.REGISTER}
          element={
            <PublicRoute>
              <Register />
            </PublicRoute>
          }
        />
        <Route
          path={ROUTE_PATHS.DASHBOARD}
          element={
            <ProtectedRoute>
              <DashboardRedirect />
            </ProtectedRoute>
          }
        />
        <Route
          path={ROUTE_PATHS.PATIENT_DASHBOARD}
          element={
            <ProtectedRoute allowedRoles={[ROLES.PATIENT]}>
              <PatientDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path={ROUTE_PATHS.UPLOAD_PRESCRIPTION}
          element={
            <ProtectedRoute allowedRoles={[ROLES.PATIENT]}>
              <UploadPrescription />
            </ProtectedRoute>
          }
        />
        <Route
          path={ROUTE_PATHS.REVIEW_PRESCRIPTION}
          element={
            <ProtectedRoute allowedRoles={[ROLES.PATIENT]}>
              <ReviewPrescription />
            </ProtectedRoute>
          }
        />
        <Route
          path={ROUTE_PATHS.MEDICATION_LIST}
          element={
            <ProtectedRoute allowedRoles={[ROLES.PATIENT]}>
              <MedicationList />
            </ProtectedRoute>
          }
        />
        <Route
          path={ROUTE_PATHS.CAREGIVER_DASHBOARD}
          element={
            <ProtectedRoute allowedRoles={[ROLES.CAREGIVER]}>
              <CaregiverDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path={ROUTE_PATHS.REMINDERS}
          element={
            <ProtectedRoute allowedRoles={[ROLES.PATIENT]}>
              <ReminderSettings />
            </ProtectedRoute>
          }
        />
        <Route
          path={ROUTE_PATHS.VERIFY_MEDICINE}
          element={
          <ProtectedRoute allowedRoles={[ROLES.PATIENT]}>
            <VerifyMedicine />
          </ProtectedRoute>
          }
        />
        <Route
          path={ROUTE_PATHS.DOCTOR_DASHBOARD}
          element={
            <ProtectedRoute allowedRoles={[ROLES.DOCTOR]}>
              <DoctorDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path={ROUTE_PATHS.PATIENT_ANALYTICS}
          element={
            <ProtectedRoute allowedRoles={[ROLES.PATIENT, ROLES.CAREGIVER, ROLES.DOCTOR]}>
              <PatientAnalytics />
            </ProtectedRoute>
          }
        />

      
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}
