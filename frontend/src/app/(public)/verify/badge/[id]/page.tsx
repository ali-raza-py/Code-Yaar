import type { Metadata } from 'next';
import VerifyView from '@/components/credentials/verify-view';
import { badgeOgImageUrl, verifyBadgeServer } from '@/lib/server-verify';

type Params = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { id } = await params;
  const result = await verifyBadgeServer(id);

  if (result.state !== 'ok') {
    return {
      title: 'Badge not found',
      description:
        'This identifier does not exist in the Code Yaar credential registry.',
      robots: { index: false },
    };
  }

  const badge = result.data;
  const holder = badge.recipient_name || 'a Code Yaar learner';
  const title = badge.title || 'Code Yaar achievement';
  const description = badge.valid
    ? `${holder} earned the "${title}" badge (${badge.level_label || 'achievement'}) from Code Yaar Academy. Credential ${badge.credential_id} — verified against the Code Yaar registry.`
    : `Credential ${badge.credential_id} exists in the Code Yaar registry but is currently ${badge.status}.`;

  const url = badge.verification_url || `/verify/badge/${id}`;

  return {
    title: badge.valid ? `Badge verified — ${title}` : `Badge ${badge.status || 'unverified'}`,
    description,
    alternates: { canonical: url },
    openGraph: {
      title: badge.valid ? `${holder} — ${title} badge` : `Code Yaar credential ${badge.credential_id}`,
      description,
      url,
      siteName: 'Code Yaar',
      type: 'website',
      ...(badge.valid
        ? {
            images: [
              {
                url: badgeOgImageUrl(badge.credential_id || id),
                width: 1200,
                height: 1200,
                alt: `${title} — LinkedIn-ready achievement graphic from Code Yaar Academy`,
              },
            ],
          }
        : {}),
    },
    twitter: {
      card: 'summary_large_image',
      title: `Code Yaar badge — ${title}`,
      description,
    },
  };
}

export default async function BadgeVerificationPage({ params }: Params) {
  const { id } = await params;
  const result = await verifyBadgeServer(id);

  return (
    <VerifyView
      kind="badge"
      state={result.state === 'ok' ? 'ok' : result.state === 'missing' ? 'missing' : 'unavailable'}
      requestedId={id}
      badge={result.state === 'ok' ? result.data : undefined}
    />
  );
}
