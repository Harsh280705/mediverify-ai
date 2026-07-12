import { Link } from 'react-router-dom';
import PageShell from '../components/PageShell';
import PrimaryButton from '../components/PrimaryButton';
import { ROUTE_PATHS } from '../utils/constants';

export default function NotFound() {
  return (
    <PageShell eyebrow="404" title="Page not found" description="The requested route does not exist yet.">
      <Link to={ROUTE_PATHS.LANDING}>
        <PrimaryButton>Return home</PrimaryButton>
      </Link>
    </PageShell>
  );
}
