import CertificateQAHarness from './harness';

/**
 * Dev-only visual QA harness for the certificate sheet artwork.
 * Renders sample data (no persisted records are touched).
 * Not linked from any navigation; deleted after visual QA.
 */
export const dynamic = 'force-dynamic';
export default function Page() {
  return <CertificateQAHarness />;
}
