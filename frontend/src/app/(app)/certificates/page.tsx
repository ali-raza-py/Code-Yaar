'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  ApiError,
  certificates as certificatesApi,
  type CertificateSummary,
} from '@/lib/api';
import { NetworkError } from '@/components/learning/workspace/error-states';

const STATUS_STYLES: Record<CertificateSummary['status'], { label: string; cls: string }> = {
  active: { label: 'Valid', cls: 'border-success/30 bg-success/10 text-success' },
  revoked: { label: 'Revoked', cls: 'border-red-300 bg-red-50 text-red-600' },
  superseded: { label: 'Superseded', cls: 'border-border bg-muted text-muted-foreground' },
};

function formatDate(iso: string | null) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

export default function CertificatesPage() {
  const [certs, setCerts] = useState<CertificateSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await certificatesApi.myCertificates();
        if (!cancelled) {
          setCerts(data);
          setError(null);
        }
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof ApiError && e.status === 401 ? 'auth' : 'network');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  const handleDownload = async (publicId: string) => {
    setDownloadingId(publicId);
    setDownloadError(null);
    try {
      await certificatesApi.download(publicId);
    } catch {
      setDownloadError('Download failed. Please try again.');
    } finally {
      setDownloadingId(null);
    }
  };

  if (error === 'network') return <NetworkError />;

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8">
        <div className="mb-3 inline-flex items-center gap-2 rounded-pill border border-primary/25 bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 01-.982-3.172M9.497 14.25a7.454 7.454 0 00.981-3.172M5.25 4.236c-.982.143-1.954.317-2.916.52A6.003 6.003 0 007.73 9.728" />
          </svg>
          ACHIEVEMENTS
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">
          My Certificates
        </h1>
        <p className="mt-2 text-muted-foreground">
          Verifiable certificates earned by completing every lesson and passing
          the final assessment. Each one can be shared and publicly verified.
        </p>
      </div>

      {downloadError && (
        <p className="mb-4 rounded-card border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-600">
          {downloadError}
        </p>
      )}

      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="h-40 rounded-card border border-border bg-card animate-pulse" />
          ))}
        </div>
      ) : error === 'auth' ? (
        <div className="card-hairline p-12 text-center">
          <h2 className="text-lg font-semibold text-foreground">Sign in to view certificates</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Certificates are issued by the server once your completion is verified.
          </p>
          <Link href="/sign-in" className="btn-primary mt-6">Sign in</Link>
        </div>
      ) : certs.length === 0 ? (
        <div className="card-hairline p-12 text-center">
          <h2 className="text-lg font-semibold text-foreground">No certificates yet</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Finish all lessons of a course and pass its final assessment to earn
            your first verifiable certificate.
          </p>
          <Link href="/learn?view=courses" className="btn-primary mt-6">Browse courses</Link>
        </div>
      ) : (
        <div className="space-y-4">
          {certs.map((cert) => {
            const status = STATUS_STYLES[cert.status] ?? STATUS_STYLES.superseded;
            return (
              <div key={cert.public_id} className="rounded-card border border-border bg-card p-6">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <h2 className="text-lg font-bold text-foreground">{cert.course_title}</h2>
                      <span className={`rounded-pill border px-2.5 py-0.5 text-xs font-medium ${status.cls}`}>
                        {status.label}
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-muted-foreground">
                      Awarded to <span className="font-semibold text-foreground">{cert.student_name}</span>
                      {cert.final_score !== null && (
                        <> · Final assessment {cert.final_score}%</>
                      )}
                    </p>
                  </div>
                  <p className="text-xs text-muted-foreground">Issued {formatDate(cert.issued_at)}</p>
                </div>

                <div className="mt-4 flex flex-wrap items-center gap-3 border-t border-border pt-4 text-xs text-muted-foreground">
                  <span className="font-mono">{cert.credential_id}</span>
                  <div className="ml-auto flex gap-2">
                    {cert.is_valid && (
                      <button
                        type="button"
                        onClick={() => handleDownload(cert.public_id)}
                        disabled={downloadingId === cert.public_id}
                        className="btn-primary px-3 py-1.5 text-xs disabled:opacity-60"
                      >
                        {downloadingId === cert.public_id ? 'Preparing…' : 'Download PDF'}
                      </button>
                    )}
                    <Link
                      href={`/verify/${cert.public_id}`}
                      className="rounded-card border border-border bg-background px-3 py-1.5 text-xs font-medium text-foreground transition-colors hover:bg-muted"
                    >
                      Public verification page
                    </Link>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
