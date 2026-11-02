'use client';

// Standalone route kept alive for bookmarks and inbound links; it renders the
// same shared certificates body as the My Progress > Certificates tab.
import { CertificatesTabBody } from '@/components/progress/certificates-tab';

export default function CertificatesPage() {
  return <CertificatesTabBody />;
}
