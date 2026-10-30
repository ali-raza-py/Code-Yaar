'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import {
  ApiError,
  certificates as certificatesApi,
  type CertificateEligibility,
  type CertificateSummary,
} from '@/lib/api';
import { useAuth } from '@/hooks/use-auth';

interface Props {
  courseSlug: string;
  enrolled: boolean;
}

/**
 * Server-driven certificate status for one course. Requirements and the
 * final score always come from Django — the client never decides eligibility.
 */
export default function CertificatePanel({ courseSlug, enrolled }: Props) {
  const { user } = useAuth();
  const [eligibility, setEligibility] = useState<CertificateEligibility | null>(null);
  const [certificate, setCertificate] = useState<CertificateSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [issuing, setIssuing] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!user || !enrolled) return;
    setLoading(true);
    try {
      const elig = await certificatesApi.eligibility(courseSlug);
      setEligibility(elig);
      if (elig.eligible) {
        // Show the existing certificate if one was already issued.
        const certs = await certificatesApi.myCertificates();
        setCertificate(certs.find((c) => c.course_slug === courseSlug) ?? null);
      } else {
        setCertificate(null);
      }
    } catch {
      setEligibility(null);
    } finally {
      setLoading(false);
    }
  }, [courseSlug, enrolled, user]);

  useEffect(() => {
    // Deferred call so state is never set synchronously inside the effect.
    (async () => { await refresh(); })();
  }, [refresh]);

  const handleIssue = async () => {
    setIssuing(true);
    setNotice(null);
    try {
      const cert = await certificatesApi.issue(courseSlug);
      setCertificate(cert);
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 412) {
        setNotice('The server re-checked your progress and requirements are not met yet.');
        await refresh();
      } else {
        setNotice('Could not issue the certificate. Please try again.');
      }
    } finally {
      setIssuing(false);
    }
  };

  if (!user) {
    return (
      <div className="rounded-xl border border-border bg-white p-5">
        <h3 className="mb-2 text-sm font-semibold text-foreground">Certificate</h3>
        <p className="text-sm text-muted-foreground">
          Sign in and complete this course to earn a verifiable certificate.
        </p>
      </div>
    );
  }

  if (!enrolled) {
    return (
      <div className="rounded-xl border border-border bg-white p-5">
        <h3 className="mb-2 text-sm font-semibold text-foreground">Certificate</h3>
        <p className="text-sm text-muted-foreground">
          Enroll in this course to track eligibility for its certificate.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-border bg-white p-5">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-foreground">Certificate</h3>
        {eligibility?.final_score != null && (
          <span className="text-xs text-muted-foreground">
            Assessment {eligibility.final_score}%
          </span>
        )}
      </div>

      {loading && !eligibility ? (
        <div className="space-y-2">
          <div className="h-4 w-3/4 rounded bg-muted animate-pulse" />
          <div className="h-4 w-2/3 rounded bg-muted animate-pulse" />
        </div>
      ) : !eligibility ? (
        <p className="text-sm text-muted-foreground">
          Certificate status could not be loaded. The server grades every
          requirement — nothing is self-declared.
        </p>
      ) : certificate ? (
        <div className="space-y-3">
          <div className="flex items-center gap-2 rounded-lg bg-success/10 px-3 py-2 text-sm font-medium text-success">
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
            </svg>
            Certificate issued
          </div>
          <p className="break-all font-mono text-xs text-muted-foreground">
            {certificate.credential_id}
          </p>
          <div className="flex flex-wrap gap-2">
            <Link
              href="/certificates"
              className="focus-ring inline-flex min-h-9 items-center rounded-lg bg-cta px-4 py-2 text-sm font-semibold text-white hover:bg-cta-hover"
            >
              View & download
            </Link>
            <Link
              href={`/verify/${certificate.public_id}`}
              className="focus-ring inline-flex min-h-9 items-center rounded-lg border border-border px-4 py-2 text-sm font-medium text-foreground hover:bg-muted/60"
            >
              Public link
            </Link>
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          <ul className="space-y-2">
            {eligibility.requirements.map((req) => (
              <li key={req.key} className="flex items-start gap-2 text-sm">
                <span
                  aria-hidden="true"
                  className={`mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full text-[10px] font-bold ${
                    req.met ? 'bg-success/15 text-success' : 'bg-muted text-muted-foreground'
                  }`}
                >
                  {req.met ? '✓' : '·'}
                </span>
                <span className={req.met ? 'text-foreground' : 'text-muted-foreground'}>
                  {req.label}
                  <span className="block text-xs text-muted-foreground">{req.detail}</span>
                </span>
              </li>
            ))}
          </ul>

          {eligibility.eligible ? (
            <button
              type="button"
              onClick={handleIssue}
              disabled={issuing}
              className="focus-ring inline-flex min-h-9 w-full items-center justify-center rounded-lg bg-cta px-4 py-2 text-sm font-semibold text-white hover:bg-cta-hover disabled:opacity-50"
            >
              {issuing ? 'Verifying…' : 'Claim my certificate'}
            </button>
          ) : (
            <p className="text-xs text-muted-foreground">
              Requirements are verified server-side against your real progress.
            </p>
          )}
          {notice && <p role="alert" className="text-xs text-danger">{notice}</p>}
        </div>
      )}
    </div>
  );
}
