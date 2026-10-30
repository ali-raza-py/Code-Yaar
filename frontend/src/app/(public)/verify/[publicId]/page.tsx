'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { ApiError, badges as badgesApi, certificates as certificatesApi } from '@/lib/api';

type Resolution =
  | { kind: 'pending' }
  | { kind: 'certificate'; id: string }
  | { kind: 'badge'; id: string }
  | { kind: 'missing' }
  | { kind: 'unavailable' };

/**
 * Legacy `/verify/<id>` links resolve here: look the identifier up in both
 * registries and forward to the canonical, metadata-rich route
 * (`/verify/certificate/<id>` or `/verify/badge/<id>`). If the identifier
 * belongs to neither registry we say so instead of pretending it is valid.
 */
export default function LegacyVerificationResolver() {
  const params = useParams<{ publicId: string }>();
  const router = useRouter();
  const publicId = params.publicId;
  const [resolution, setResolution] = useState<Resolution>({ kind: 'pending' });

  useEffect(() => {
    if (!publicId) return;
    let cancelled = false;
    (async () => {
      try {
        const cert = await certificatesApi.verify(publicId);
        if (cancelled) return;
        if (cert.found && cert.credential_id) {
          setResolution({ kind: 'certificate', id: cert.credential_id });
          router.replace(`/verify/certificate/${encodeURIComponent(cert.credential_id)}`);
          return;
        }
      } catch (e) {
        if (e instanceof ApiError && e.status !== 404) {
          if (!cancelled) setResolution({ kind: 'unavailable' });
          return;
        }
      }

      try {
        const badge = await badgesApi.verify(publicId);
        if (cancelled) return;
        if (badge.found && badge.credential_id) {
          setResolution({ kind: 'badge', id: badge.credential_id });
          router.replace(`/verify/badge/${encodeURIComponent(badge.credential_id)}`);
          return;
        }
        if (!cancelled) setResolution({ kind: 'missing' });
      } catch (e) {
        if (cancelled) return;
        if (e instanceof ApiError && e.status === 404) setResolution({ kind: 'missing' });
        else setResolution({ kind: 'unavailable' });
      }
    })();
    return () => { cancelled = true; };
  }, [publicId, router]);

  return (
    <div className="mx-auto max-w-2xl px-4 py-16 text-center sm:px-6">
      <div className="card-hairline p-10">
        {resolution.kind === 'pending' && (
          <>
            <div className="mx-auto h-10 w-10 animate-spin rounded-full border-2 border-muted border-t-primary" />
            <p className="mt-4 text-sm text-muted-foreground">
              Checking the Code Yaar credential registry…
            </p>
          </>
        )}

        {resolution.kind === 'certificate' || resolution.kind === 'badge' ? (
          <p className="text-sm text-muted-foreground">
            Credential found — opening the verification page…
          </p>
        ) : null}

        {resolution.kind === 'missing' && (
          <>
            <h1 className="text-xl font-bold text-foreground">Credential not found</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              No certificate or badge matches{' '}
              <span className="font-mono">{publicId}</span>. It may have been
              mistyped, or it was never issued by Code Yaar Academy.
            </p>
          </>
        )}

        {resolution.kind === 'unavailable' && (
          <>
            <h1 className="text-xl font-bold text-foreground">
              Verification service unavailable
            </h1>
            <p className="mt-2 text-sm text-muted-foreground">
              We could not reach the Code Yaar registry. Please try again shortly.
            </p>
          </>
        )}

        <div className="mt-6 flex flex-wrap justify-center gap-3">
          <Link
            href="/"
            className="focus-ring inline-flex min-h-10 items-center rounded-lg bg-cta px-4 py-2 text-sm font-semibold text-white hover:bg-cta-hover"
          >
            Code Yaar home
          </Link>
          <Link
            href="/learn?view=courses"
            className="focus-ring inline-flex min-h-10 items-center rounded-lg border border-border px-4 py-2 text-sm font-medium text-foreground hover:bg-muted"
          >
            Explore courses
          </Link>
        </div>
      </div>
    </div>
  );
}
