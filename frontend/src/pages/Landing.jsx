import { Link } from 'react-router-dom';
import PageShell from '../components/PageShell';
import PrimaryButton from '../components/PrimaryButton';
import SectionCard from '../components/SectionCard';
import { ROUTE_PATHS } from '../utils/constants';

export default function Landing() {
  return (
    <PageShell
      eyebrow="MediVerify AI"
      title="Medication adherence verification, built on a clean foundation."
      description="Day 1 establishes the authenticated app shell, role-based access, and a modular backend so OCR, timeline intelligence, and verification logic can land later without rewiring the stack."
    >
      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <SectionCard
          title="A foundation for patients and caregivers"
          footer={
            <div className="flex flex-wrap gap-3">
              <Link to={ROUTE_PATHS.LOGIN}>
                <PrimaryButton>Login</PrimaryButton>
              </Link>
              <Link to={ROUTE_PATHS.REGISTER}>
                <PrimaryButton className="bg-white text-slate-950 hover:bg-slate-100">Register</PrimaryButton>
              </Link>
            </div>
          }
        >
          <p>
            MediVerify AI is structured to support secure identity, role-aware experiences, and Firestore-backed user profiles from the
            start. The current build keeps all business logic outside of route handlers and leaves room for future OCR, AI, and reminder
            modules.
          </p>
        </SectionCard>

        <SectionCard title="What is ready now">
          <ul className="space-y-3">
            <li>React Router shell with protected routing</li>
            <li>Firebase client initialization and auth context</li>
            <li>FastAPI health endpoint and Firebase Admin singleton</li>
            <li>Re-usable component and service structure</li>
          </ul>
        </SectionCard>
      </div>
    </PageShell>
  );
}
