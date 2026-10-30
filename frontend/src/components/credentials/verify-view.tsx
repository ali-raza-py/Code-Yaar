import Link from 'next/link';
import {
  BadgeCheck,
  Home,
  RefreshCw,
  ShieldAlert,
  XCircle,
} from 'lucide-react';
import {
  CopyLinkButton,
  LinkedInShareButton,
} from '@/components/credentials/credential-actions';
import { certificateShareText, badgeShareText } from '@/lib/share';
import {
  badgeMedallionImageUrl,
  type BadgeVerifyResult,
  type CertificateVerifyResult,
} from '@/lib/server-verify';

type State = 'ok' | 'missing' | 'unavailable';

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '—';
  return d.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

function Detail({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="min-w-0">
      <dt className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        {label}
      </dt>
      <dd className="mt-1 break-words text-sm font-semibold text-foreground">
        {children}
      </dd>
    </div>
  );
}

/**
 * Public credential verification presentation.
 *
 * Every value shown here comes from the Django registry row for this exact
 * identifier — an unknown, revoked, or superseded credential renders its real
 * status instead of a generic success screen.
 */
export default function VerifyView({
  kind,
  state,
  requestedId,
  certificate,
  badge,
}: {
  kind: 'certificate' | 'badge';
  state: State;
  requestedId: string;
  certificate?: CertificateVerifyResult;
  badge?: BadgeVerifyResult;
}) {
  const isCert = kind === 'certificate';
  const data = isCert ? certificate : badge;
  const valid = Boolean(data?.valid);
  const revoked = Boolean(data?.revoked);
  const superseded = Boolean(isCert && certificate?.superseded);

  const verificationUrl = data?.verification_url ?? '';
  const title = isCert
    ? certificate?.course_title || 'Certificate'
    : badge?.title || 'Badge';
  const recipient = isCert
    ? certificate?.student_name || ''
    : badge?.recipient_name || '';

  const shareText =
    isCert && certificate
      ? certificateShareText({
          courseTitle: certificate.course_title || 'a Code Yaar course',
          learnerName: certificate.student_name,
          verificationUrl: verificationUrl,
        })
      : badge
        ? badgeShareText({
            badgeTitle: badge.title || 'Code Yaar achievement',
            verificationUrl: verificationUrl,
          })
        : '';

  const status = state === 'missing'
    ? {
        tone: 'danger',
        icon: XCircle,
        heading: isCert ? 'Certificate not found' : 'Badge not found',
        sub: 'This identifier does not exist in the Code Yaar registry. It may have been mistyped — or it was never issued.',
      }
    : state === 'unavailable'
      ? {
          tone: 'muted',
          icon: RefreshCw,
          heading: 'Verification service unavailable',
          sub: 'We could not reach the Code Yaar registry right now. Please try again in a moment.',
        }
      : !valid
        ? {
            tone: 'danger',
            icon: ShieldAlert,
            heading: revoked
              ? isCert
                ? 'Certificate revoked'
                : 'Badge revoked'
              : superseded
                ? 'Certificate superseded'
                : isCert
                  ? 'Certificate invalid'
                  : 'Badge inactive',
            sub: revoked
              ? 'This credential was withdrawn by the issuing body and is no longer valid.'
              : superseded
                ? 'This certificate was replaced by a corrected re-issue. Use the latest credential.'
                : 'This credential was replaced or deactivated. Use the latest issued version.',
          }
        : {
            tone: 'success',
            icon: BadgeCheck,
            heading: isCert ? 'Certificate is valid' : 'Badge is valid',
            sub: `Verified against the live Code Yaar registry · ${new Date().toLocaleDateString()}`,
          };

  const StatusIcon = status.icon;

  return (
    <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6 lg:py-14">
      <nav aria-label="Breadcrumb" className="mb-6">
        <ol className="flex flex-wrap items-center gap-1.5 text-xs text-muted-foreground">
          <li>
            <Link href="/" className="hover:text-primary">
              Home
            </Link>
          </li>
          <li aria-hidden="true">/</li>
          <li>Credential verification</li>
          <li aria-hidden="true">/</li>
          <li className="font-mono text-foreground" aria-current="page">
            {requestedId}
          </li>
        </ol>
      </nav>

      <div className="overflow-hidden rounded-card border border-border bg-card shadow-[var(--shadow-1)]">
        {/* Brand band */}
        <div className="relative overflow-hidden bg-[#111827] px-6 py-6 text-center sm:px-8">
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-0"
            style={{
              background:
                'radial-gradient(circle at 15% 0%, rgba(117,40,232,0.45), transparent 45%), radial-gradient(circle at 85% 100%, rgba(196,163,90,0.22), transparent 45%)',
            }}
          />
          <p
            className="relative text-xs font-bold tracking-[0.34em] text-[#C4B5FD]"
            style={{ letterSpacing: '0.34em' }}
          >
            CODE YAAR ACADEMY
          </p>
          <p className="relative mt-2 text-2xl font-extrabold text-white">
            {isCert ? 'Certificate Verification' : 'Badge Verification'}
          </p>
          <p
            className="relative mt-1.5 text-[11px] font-semibold text-[#C4A35A]"
            style={{ letterSpacing: '0.3em' }}
          >
            THINK. BUILD. EVOLVE.
          </p>
        </div>

        {/* Status */}
        <div className="px-6 pb-2 pt-8 text-center sm:px-8">
          <div
            className={`mx-auto flex h-16 w-16 items-center justify-center rounded-full ${
              status.tone === 'success'
                ? 'bg-success/10 text-success'
                : status.tone === 'danger'
                  ? 'bg-red-50 text-red-600'
                  : 'bg-muted text-muted-foreground'
            }`}
          >
            <StatusIcon className="h-8 w-8" aria-hidden="true" />
          </div>
          <h1 className="mt-4 text-2xl font-bold tracking-tight text-foreground">
            {status.heading}
          </h1>
          <p className="mx-auto mt-2 max-w-lg text-sm text-muted-foreground">
            {status.sub}
          </p>
        </div>

        {/* Record */}
        {state === 'ok' && data && (
          <div className="px-6 pb-8 pt-6 sm:px-8">
            {!isCert && badge?.credential_id && (
              <div className="mb-6 flex justify-center">
                {/* Official medallion artwork, served by Django from the real
                    record — the same file the download actions deliver. */}
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={badgeMedallionImageUrl(badge.credential_id)}
                  alt={`${title} badge issued by Code Yaar Academy`}
                  width={200}
                  height={200}
                  className="h-40 w-40 rounded-full object-cover shadow-[var(--shadow-1)] sm:h-48 sm:w-48"
                />
              </div>
            )}
            <div className="rounded-card border border-border bg-background p-6 text-center">
              <p className="text-sm text-muted-foreground">This certifies that</p>
              <p className="mt-2 break-words text-2xl font-bold text-foreground">
                {recipient || '—'}
              </p>
              <div className="mx-auto my-4 h-px w-40 bg-primary/40" />
              <p className="text-sm text-muted-foreground">
                {isCert ? 'has successfully completed' : 'has earned the achievement'}
              </p>
              <p className="mt-2 break-words text-lg font-semibold text-primary">
                {title}
              </p>
            </div>

            <dl className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Detail label="Credential ID">
                <span className="font-mono">
                  {isCert ? certificate?.credential_id : badge?.credential_id}
                </span>
              </Detail>
              <Detail label="Issue date">
                {formatDate(
                  isCert ? certificate?.issued_at : (badge?.issued_at ?? null)
                )}
              </Detail>
              <Detail label="Issuing organization">
                {(isCert ? certificate?.issuer : badge?.issuer) || 'Code Yaar Academy'}
              </Detail>
              {isCert ? (
                <Detail label="Final assessment">
                  {certificate?.final_score != null
                    ? `${certificate.final_score}%`
                    : 'Not graded'}
                </Detail>
              ) : (
                <Detail label="Level">
                  {badge?.level_label || '—'}
                </Detail>
              )}
              <Detail label="Status">
                <span
                  className={`inline-flex items-center rounded-pill border px-2.5 py-0.5 text-xs font-semibold ${
                    valid
                      ? 'border-success/30 bg-success/10 text-success'
                      : 'border-red-200 bg-red-50 text-red-600'
                  }`}
                >
                  {valid ? 'Active' : revoked ? 'Revoked' : 'Inactive'}
                </span>
              </Detail>
              {!isCert && badge?.category_label && (
                <Detail label="Category">{badge.category_label}</Detail>
              )}
            </dl>

            <p className="mt-5 break-all rounded-card border border-border bg-muted/40 px-4 py-3 text-center font-mono text-xs text-muted-foreground">
              {verificationUrl}
            </p>

            {valid && (
              <div className="mt-5 flex flex-wrap justify-center gap-3">
                <LinkedInShareButton
                  url={verificationUrl}
                  text={shareText}
                  variant="outline"
                />
                <CopyLinkButton url={verificationUrl} />
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="border-t border-border bg-background px-6 py-5 text-center sm:px-8">
          <p className="text-xs text-muted-foreground">
            This page reflects the Code Yaar credential registry at the moment it
            was loaded. Issued by Code Yaar Academy.
          </p>
          <div className="mt-3 flex flex-wrap justify-center gap-4 text-sm">
            <Link
              href="/"
              className="inline-flex items-center gap-1.5 font-medium text-foreground hover:text-primary"
            >
              <Home className="h-3.5 w-3.5" aria-hidden="true" />
              Code Yaar home
            </Link>
            <Link
              href="/learn?view=courses"
              className="font-medium text-foreground hover:text-primary"
            >
              Explore courses
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
