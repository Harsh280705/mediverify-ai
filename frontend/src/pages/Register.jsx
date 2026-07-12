import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import PageShell from '../components/PageShell';
import PrimaryButton from '../components/PrimaryButton';
import SectionCard from '../components/SectionCard';
import TextField from '../components/TextField';
import SelectField from '../components/SelectField';
import { useAuth } from '../hooks/useAuth';
import { ROLES, ROUTE_PATHS, getDashboardPath } from '../utils/constants';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', email: '', password: '', role: ROLES.PATIENT });
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      const user = await register(form);
      navigate(getDashboardPath(user?.role ?? form.role), { replace: true });
    } catch (registerError) {
      setError(registerError.message || 'Unable to create the account right now.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <PageShell eyebrow="Authentication" title="Register" description="Create a Firebase user profile and persist role metadata to Firestore.">
      <div className="mx-auto max-w-xl">
        <SectionCard
          title="Create your account"
          footer={<Link className="text-sm text-cyan-300 underline-offset-4 hover:underline" to={ROUTE_PATHS.LOGIN}>Already registered? Go to login.</Link>}
        >
          <form className="space-y-4" onSubmit={handleSubmit}>
            <TextField label="Name" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} autoComplete="name" required />
            <TextField label="Email" type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} autoComplete="email" required />
            <TextField label="Password" type="password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} autoComplete="new-password" required />
            <SelectField
              label="Role"
              value={form.role}
              onChange={(event) => setForm({ ...form, role: event.target.value })}
              options={[
                { value: ROLES.PATIENT, label: 'Patient' },
                { value: ROLES.CAREGIVER, label: 'Caregiver' },
              ]}
              required
            />
            {error ? <p className="text-sm text-rose-300">{error}</p> : null}
            <PrimaryButton type="submit" disabled={submitting} className="w-full">
              {submitting ? 'Creating account...' : 'Register'}
            </PrimaryButton>
          </form>
        </SectionCard>
      </div>
    </PageShell>
  );
}
