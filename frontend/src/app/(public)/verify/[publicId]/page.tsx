'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { ApiError, certificates as certificatesApi, type PublicVerification } from '@/lib/api';

function formatDate(iso: string | undefined | null) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

export default function VerifyCertificatePage() {
  const params = useParams<{ publicId: string }>();
  const publicId = params.publicId;
  const [data, setData] = useState<PublicVerification | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [networkIssue, setNetworkIssue] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!publicId) return;
    let cancelled = false;
    (async () => {
      try {
        const res = await certificatesApi.verify(publicId);
        if (!cancelled) setData(res);
      } catch (e) {
        if (cancelled) return;
        if (e instanceof ApiError && e.status === 404) setNotFound(true);
        else setNetworkIssue(true);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [publicId]);

  return (
    <div className="mx-auto max-w-2xl px-4 py-16 sm:px-6">
      <div className="mb-6 text-center">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">
          Certificate Verification
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          This page reflects the Code-Yaar registry at the moment you loaded it.
        </p>
      </div>

      {loading ? (
        <div className="card-hairline animate-pulse p-10">
          <div className="mx-auto h-24 w-24 rounded-full bg-muted" />
          <div className="mx-auto mt-6 h-4 w-2/3 rounded bg-muted" />
          <div className="mx-auto mt-3 h-4 w-1/2 rounded bg-muted" />
        </div>
      ) : networkIssue ? (
        <div className="card-hairline p-10 text-center">
          <h2 className="text-lg font-semibold text-foreground">Verification service unreachable</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Could not contact the certificate registry. Please try again later.
          </p>
        </div>
      ) : notFound || !data ? (
        <div className="card-hairline border-red-300 p-10 text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-red-50 text-3xl">
            ✕
          </div>
          <h2 className="mt-4 text-lg font-semibold text-foreground">Certificate not found</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            No certificate exists with identifier{' '}
            <span className="font-mono">{publicId}</span>. It may have been entered
            incorrectly — or it was never issued by Code-Yaar.
          </p>
        </div>
      ) : !data.valid ? (
        <div className="card-hairline border-red-300 p-10 text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-red-50 text-3xl">
            {data.revoked ? '⊘' : '↻'}
          </div>
          <h2 className="mt-4 text-lg font-semibold text-foreground">
            {data.revoked ? 'Certificate revoked' : 'Certificate superseded'}
          </h2>
          <p className="mt-2 text-sm text-muted-foreground">
            {data.student_name} · {data.course_title}
          </p>
          <p className="mt-3 text-sm text-muted-foreground">
            {data.revoked
              ? 'This certificate was withdrawn by the issuing body and is no longer valid.'
              : 'This certificate was replaced by a corrected re-issuance. Use the latest credential.'}
          </p>
        </div>
      ) : (
        <div className="card-hairline p-10 text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-success/10 text-3xl text-success">
            ✓
          </div>
          <h2 className="mt-4 text-xl font-bold text-foreground">Certificate is valid</h2>
          <p className="mt-1 text-xs font-medium uppercase tracking-wide text-success">
            Verified by Code-Yaar Academy
          </p>

          <div className="mt-8 rounded-card border border-border bg-background p-6 text-left">
            <p className="text-sm text-muted-foreground">This certifies that</p>
            <p className="mt-1 text-xl font-bold text-foreground">{data.student_name}</p>
            <p className="mt-3 text-sm text-muted-foreground">has successfully completed</p>
            <p className="mt-1 text-lg font-semibold text-foreground">{data.course_title}</p>

            <dl className="mt-6 grid grid-cols-1 gap-3 border-t border-border pt-4 text-sm sm:grid-cols-2">
              <div>
                <dt className="text-muted-foreground">Credential ID</dt>
                <dd className="mt-0.5 font-mono text-foreground">{data.credential_id}</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Issue date</dt>
                <dd className="mt-0.5 text-foreground">{formatDate(data.issued_at)}</dd>
              </div>
            </dl>
          </div>

          <p className="mt-6 break-all font-mono text-xs text-muted-foreground">
            {publicId}
          </p>
        </div>
      )}

      <div className="mt-8 text-center">
        <Link href="/" className="text-sm font-medium text-primary hover:underline">
          ← Back to Code-Yaar
        </Link>
      </div>
    </div>
  );
}
