'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import {
  ArrowLeft,
  Award,
  ExternalLink,
  Home,
  RotateCcw,
} from 'lucide-react';
import {
  ApiError,
  certificates as certificatesApi,
  type CertificateSummary,
} from '@/lib/api';
import { certificateShareText } from '@/lib/share';
import CertificateSheet from '@/components/credentials/certificate-artwork';
import CertificatePreview from '@/components/credentials/certificate-preview';
import {
  CopyLinkButton,
  DownloadButton,
  LinkedInShareButton,
} from '@/components/credentials/credential-actions';

const STATUS_STYLES: Record<string, { label: string; cls: string }> = {
  active: { label: 'Valid', cls: 'border-success/30 bg-success/10 text-success' },
  revoked: { label: 'Revoked', cls: 'border-red-300 bg-red-50 text-red-600' },
  superseded: { label: 'Superseded', cls: 'border-border bg-muted text-muted-foreground' },
};

/**
 * Certificate viewer: preview, download (PDF/PNG), print, LinkedIn sharing,
 * and public verification — with explicit navigation back to the dashboard,
 * the certificate list, and achievements so browser-back is never the only way.
 */
export default function CertificateViewerPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;

  const [certs, setCerts] = useState<CertificateSummary[] | null>(null);
  const [error, setError] = useState<'auth' | 'network' | 'notfound' | null>(null);
  const [zoom, setZoom] = useState(0);
  const [downloading, setDownloading] = useState<'pdf' | 'png' | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    (async () => {
      try {
        const data = await certificatesApi.myCertificates();
        if (cancelled) return;
        const found = data.find(
          (c) =>
            c.public_id === id ||
            c.credential_id.toLowerCase() === id.toLowerCase()
        );
        if (found) {
          setCerts(data);
        } else {
          setError('notfound');
        }
      } catch (e) {
        if (cancelled) return;
        setError(e instanceof ApiError && e.status === 401 ? 'auth' : 'network');
      }
    })();
    return () => { cancelled = true; };
  }, [id]);

  const cert = useMemo(() => {
    if (!certs || !id) return null;
    return (
      certs.find(
        (c) =>
          c.public_id === id ||
          c.credential_id.toLowerCase() === id.toLowerCase()
      ) ?? null
    );
  }, [certs, id]);

  const shareUrl = cert?.verification_url ?? '';
  const shareText = cert
    ? certificateShareText({
        courseTitle: cert.course_title,
        learnerName: cert.student_name,
        verificationUrl: shareUrl,
      })
    : '';

  const handleDownload = async (format: 'pdf' | 'png') => {
    // Ignore repeat clicks while a generation is already in flight.
    if (!cert || downloading) return;
    setDownloading(format);
    setDownloadError(null);
    try {
      await certificatesApi.download(cert.public_id, format);
    } catch (e) {
      setDownloadError(
        e instanceof ApiError
          ? e.message || `Could not download the ${format.toUpperCase()}.`
          : `Could not download the ${format.toUpperCase()}. Please try again.`
      );
    } finally {
      setDownloading(null);
    }
  };

  if (error === 'auth') {
    return (
      <div className="mx-auto max-w-2xl px-4 py-16 text-center sm:px-6">
        <div className="card-hairline p-10">
          <h1 className="text-xl font-bold text-foreground">Sign in to view certificates</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Certificates belong to the learner who earned them.
          </p>
          <Link
            href="/sign-in"
            className="focus-ring inline-flex min-h-10 items-center rounded-lg bg-cta px-4 py-2 text-sm font-semibold text-white hover:bg-cta-hover"
          >
            Sign in
          </Link>
        </div>
      </div>
    );
  }

  if (error === 'notfound' || (certs && !cert)) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-16 text-center sm:px-6">
        <div className="card-hairline p-10">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-muted">
            <RotateCcw className="h-6 w-6 text-muted-foreground" aria-hidden="true" />
          </div>
          <h1 className="mt-4 text-xl font-bold text-foreground">Certificate not found</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            No certificate in your account matches{' '}
            <span className="font-mono">{id}</span>. It may have been issued to
            a different account, or the link is incorrect.
          </p>
          <div className="mt-6 flex flex-wrap justify-center gap-3">
            <Link
              href="/certificates"
              className="focus-ring inline-flex min-h-10 items-center rounded-lg bg-cta px-4 py-2 text-sm font-semibold text-white hover:bg-cta-hover"
            >
              My certificates
            </Link>
            <Link
              href="/dashboard"
              className="focus-ring inline-flex min-h-10 items-center rounded-lg border border-border px-4 py-2 text-sm font-medium text-foreground hover:bg-muted"
            >
              Back to Dashboard
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (error === 'network' || !cert) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
        <div className="card-hairline animate-pulse p-10">
          <div className="h-6 w-1/3 rounded bg-muted" />
          <div className="mt-6 aspect-[297/210] w-full rounded bg-muted" />
        </div>
      </div>
    );
  }

  const status = STATUS_STYLES[cert.status] ?? STATUS_STYLES.superseded;

  return (
    <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
      {/* ── Navigation: breadcrumb + explicit back actions ── */}
      <nav aria-label="Breadcrumb" className="mb-4">
        <ol className="flex flex-wrap items-center gap-1.5 text-xs text-muted-foreground">
          <li>
            <Link href="/dashboard" className="hover:text-primary">
              Dashboard
            </Link>
          </li>
          <li aria-hidden="true">/</li>
          <li>
            <Link href="/certificates" className="hover:text-primary">
              Certificates
            </Link>
          </li>
          <li aria-hidden="true">/</li>
          <li className="font-mono text-foreground" aria-current="page">
            {cert.credential_id}
          </li>
        </ol>
      </nav>

      {/* ── Header ── */}
      <div className="mb-5 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
              {cert.course_title}
            </h1>
            <span
              className={`rounded-pill border px-2.5 py-0.5 text-xs font-medium ${status.cls}`}
            >
              {status.label}
            </span>
          </div>
          <p className="mt-1.5 text-sm text-muted-foreground">
            Awarded to{' '}
            <span className="font-semibold text-foreground">{cert.student_name}</span>
            {cert.final_score !== null && (
              <> · Final assessment {cert.final_score}%</>
            )}
            <span className="ml-2 font-mono text-xs">{cert.credential_id}</span>
          </p>
        </div>

        <div className="flex shrink-0 flex-wrap gap-2">
          <Link
            href="/dashboard"
            className="focus-ring inline-flex min-h-10 items-center gap-2 rounded-lg border border-border bg-card px-3.5 py-2 text-sm font-medium text-foreground hover:bg-muted"
          >
            <Home className="h-4 w-4" aria-hidden="true" />
            Back to Dashboard
          </Link>
          <Link
            href="/achievements"
            className="focus-ring inline-flex min-h-10 items-center gap-2 rounded-lg border border-border bg-card px-3.5 py-2 text-sm font-medium text-foreground hover:bg-muted"
          >
            <Award className="h-4 w-4" aria-hidden="true" />
            My Achievements
          </Link>
        </div>
      </div>

      {cert.status !== 'active' && (
        <div
          role="status"
          className="mb-4 rounded-card border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
        >
          {cert.status === 'revoked'
            ? 'This certificate has been revoked by Code Yaar Academy and is no longer valid. It is shown for your records only.'
            : 'This certificate was replaced by a corrected re-issue. The record below is retained for your history.'}
        </div>
      )}

      {downloadError && (
        <p
          role="alert"
          className="mb-4 rounded-card border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-600"
        >
          {downloadError}
        </p>
      )}

      {/* ── Certificate preview ── */}
      <div className="certificate-print-root">
        <CertificatePreview zoom={zoom} onZoomChange={setZoom}>
          <CertificateSheet
            data={{
              student_name: cert.student_name,
              course_title: cert.course_title,
              credential_id: cert.credential_id,
              verification_code: cert.public_id,
              issued_at: cert.issued_at,
              final_score: cert.final_score,
              issuer: cert.issuer,
              verification_url: cert.verification_url,
              qr_data_url: cert.qr_data_url,
              status: cert.status,
            }}
          />
        </CertificatePreview>
      </div>

      {/* ── Actions ── */}
      <div className="mt-6 rounded-card border border-border bg-card p-4 sm:p-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <h2 className="text-sm font-semibold text-foreground">
              Download, print &amp; share
            </h2>
            <p className="mt-1 max-w-xl text-xs text-muted-foreground">
              PDF and PNG are rendered by Code Yaar&apos;s credential engine at
              A4 landscape — identical to this preview. LinkedIn&apos;s share
              window opens with your public verification link; your post text is
              copied for you, and you can attach the downloaded file manually.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <DownloadButton
              onClick={() => handleDownload('pdf')}
              busy={downloading === 'pdf'}
              label="Download PDF"
            />
            <DownloadButton
              onClick={() => handleDownload('png')}
              busy={downloading === 'png'}
              label="Download PNG"
              variant="outline"
            />
            <DownloadButton
              onClick={() => window.print()}
              label="Print"
              icon="print"
              variant="outline"
            />
            <LinkedInShareButton url={shareUrl} text={shareText} />
            <CopyLinkButton url={shareUrl} />
            <a
              href={shareUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="focus-ring inline-flex min-h-10 items-center gap-2 rounded-lg border border-border bg-card px-4 py-2 text-sm font-semibold text-foreground hover:bg-muted"
            >
              <ExternalLink className="h-4 w-4" aria-hidden="true" />
              Verification page
            </a>
          </div>
        </div>
      </div>

      {/* ── Footer navigation ── */}
      <div className="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-border pt-5">
        <Link
          href="/certificates"
          className="focus-ring inline-flex min-h-10 items-center gap-2 text-sm font-medium text-primary hover:underline"
        >
          <ArrowLeft className="h-4 w-4" aria-hidden="true" />
          Back to all certificates
        </Link>
        <div className="flex flex-wrap gap-4 text-sm">
          <Link href="/dashboard" className="font-medium text-foreground hover:text-primary">
            Dashboard
          </Link>
          <Link href="/achievements" className="font-medium text-foreground hover:text-primary">
            View My Achievements
          </Link>
          <Link href="/learn?view=courses" className="font-medium text-foreground hover:text-primary">
            Browse courses
          </Link>
        </div>
      </div>
    </div>
  );
}
