import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import Landing from '../pages/Landing';
import Login from '../pages/Login';
import Register from '../pages/Register';
import PatientDashboard from '../pages/PatientDashboard';
import CaregiverDashboard from '../pages/CaregiverDashboard';
import NotFound from '../pages/NotFound';
import { useAuth } from '../hooks/useAuth';
import { ProtectedRoute, PublicRoute } from './ProtectedRoute';
import { ROLES, ROUTE_PATHS } from '../utils/constants';

function DashboardRedirect() {
  const { currentUser } = useAuth();
  const destination = currentUser?.role === ROLES.CAREGIVER ? ROUTE_PATHS.CAREGIVER_DASHBOARD : ROUTE_PATHS.PATIENT_DASHBOARD;

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
          path={ROUTE_PATHS.CAREGIVER_DASHBOARD}
          element={
            <ProtectedRoute allowedRoles={[ROLES.CAREGIVER]}>
              <CaregiverDashboard />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}
