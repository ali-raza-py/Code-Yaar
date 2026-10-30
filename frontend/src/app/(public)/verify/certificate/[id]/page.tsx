import type { Metadata } from 'next';
import VerifyView from '@/components/credentials/verify-view';
import {
  certificateOgImageUrl,
  verifyCertificateServer,
} from '@/lib/server-verify';

type Params = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { id } = await params;
  const result = await verifyCertificateServer(id);

  if (result.state !== 'ok') {
    return {
      title: 'Certificate not found',
      description:
        'This identifier does not exist in the Code Yaar credential registry.',
      robots: { index: false },
    };
  }

  const cert = result.data;
  const holder = cert.student_name || 'a Code Yaar learner';
  const course = cert.course_title || 'a Code Yaar course';
  const description = cert.valid
    ? `${holder} has completed ${course} at Code Yaar Academy. Credential ${cert.credential_id} — verified against the Code Yaar registry.`
    : `Credential ${cert.credential_id} exists in the Code Yaar registry but is currently ${cert.status}.`;

  const url = cert.verification_url || `/verify/certificate/${id}`;

  return {
    title: cert.valid
      ? `Certificate verified — ${course}`
      : `Certificate ${cert.status || 'unverified'}`,
    description,
    alternates: { canonical: url },
    openGraph: {
      title: cert.valid
        ? `${holder} — Certificate in ${course}`
        : `Code Yaar credential ${cert.credential_id}`,
      description,
      url,
      siteName: 'Code Yaar',
      type: 'website',
      ...(cert.valid ? { images: [{ url: certificateOgImageUrl(cert.credential_id || id), width: 2648, height: 1874, alt: `Code Yaar certificate for ${course}` }] } : {}),
    },
    twitter: {
      card: 'summary_large_image',
      title: `Code Yaar certificate — ${course}`,
      description,
    },
  };
}

export default async function CertificateVerificationPage({ params }: Params) {
  const { id } = await params;
  const result = await verifyCertificateServer(id);

  return (
    <VerifyView
      kind="certificate"
      state={result.state === 'ok' ? 'ok' : result.state === 'missing' ? 'missing' : 'unavailable'}
      requestedId={id}
      certificate={result.state === 'ok' ? result.data : undefined}
    />
  );
}
