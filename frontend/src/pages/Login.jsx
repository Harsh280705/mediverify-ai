import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import PageShell from '../components/PageShell';
import PrimaryButton from '../components/PrimaryButton';
import SectionCard from '../components/SectionCard';
import TextField from '../components/TextField';
import { useAuth } from '../hooks/useAuth';
import { ROUTE_PATHS, getDashboardPath } from '../utils/constants';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      const user = await login(form.email, form.password);
      navigate(getDashboardPath(user?.role ?? 'patient'), { replace: true });
    } catch (loginError) {
      setError(loginError.message || 'Unable to sign in right now.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <PageShell eyebrow="Authentication" title="Login" description="Sign in with Firebase Authentication to access the role-based dashboard.">
      <div className="mx-auto max-w-xl">
        <SectionCard
          title="Welcome back"
          footer={<Link className="text-sm text-cyan-300 underline-offset-4 hover:underline" to={ROUTE_PATHS.REGISTER}>Need an account? Register here.</Link>}
        >
          <form className="space-y-4" onSubmit={handleSubmit}>
            <TextField label="Email" type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} autoComplete="email" required />
            <TextField label="Password" type="password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} autoComplete="current-password" required />
            {error ? <p className="text-sm text-rose-300">{error}</p> : null}
            <PrimaryButton type="submit" disabled={submitting} className="w-full">
              {submitting ? 'Signing in...' : 'Login'}
            </PrimaryButton>
          </form>
        </SectionCard>
      </div>
    </PageShell>
  );
}
