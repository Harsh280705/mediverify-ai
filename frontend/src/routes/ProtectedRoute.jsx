import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { getDashboardPath, ROUTE_PATHS } from '../utils/constants';

function LoadingScreen() {
  return (
    <div className="grid min-h-screen place-items-center px-4 text-slate-200">
      <div className="rounded-2xl border border-white/10 bg-white/5 px-6 py-4 text-sm shadow-soft">Loading MediVerify AI...</div>
    </div>
  );
}

export function ProtectedRoute({ children, allowedRoles }) {
  const { currentUser, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <LoadingScreen />;
  }

  if (!currentUser) {
    return <Navigate to={ROUTE_PATHS.LANDING} replace state={{ from: location }} />;
  }

  if (allowedRoles?.length && !allowedRoles.includes(currentUser.role)) {
    return <Navigate to={getDashboardPath(currentUser.role)} replace />;
  }

  return children;
}

export function PublicRoute({ children }) {
  const { currentUser, loading } = useAuth();

  if (loading) {
    return <LoadingScreen />;
  }

  if (currentUser) {
    return <Navigate to={getDashboardPath(currentUser.role)} replace />;
  }

  return children;
}
