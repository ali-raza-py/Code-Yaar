'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Award, ExternalLink, Eye, Home, X } from 'lucide-react';
import {
  ApiError,
  badges as badgesApi,
  type EarnedBadge,
} from '@/lib/api';
import { badgeShareText, formatShortDate } from '@/lib/share';
import {
  CopyLinkButton,
  DownloadButton,
  LinkedInShareButton,
} from '@/components/credentials/credential-actions';
import { NetworkError } from '@/components/learning/workspace/error-states';

function levelTone(level: string): string {
  switch (level) {
    case 'Distinction':
      return 'border-amber-300 bg-amber-50 text-amber-700';
    case 'Advanced':
      return 'border-primary/30 bg-primary/10 text-primary';
    case 'Intermediate':
      return 'border-sky-300 bg-sky-50 text-sky-700';
    default:
      return 'border-border bg-muted text-muted-foreground';
  }
}

function BadgeArtwork({ badge, className }: { badge: EarnedBadge; className?: string }) {
  const [failed, setFailed] = useState(false);
  if (failed || !badge.is_valid) {
    return (
      <div
        className={`flex items-center justify-center rounded-full bg-gradient-to-br from-primary/15 to-primary/5 ${className ?? ''}`}
        aria-hidden="true"
      >
        <Award className="h-1/3 w-1/3 text-primary" />
      </div>
    );
  }
  return (
    // Official artwork served by Django from the real record — the same file
    // the Download actions deliver, so preview and download never diverge.
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={badgesApi.publicImageUrl(badge.public_id)}
      alt={`${badge.achievement.title} badge`}
      className={className}
      onError={() => setFailed(true)}
      loading="lazy"
    />
  );
}

export default function AchievementsPage() {
  const [items, setItems] = useState<EarnedBadge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<'auth' | 'network' | null>(null);
  const [active, setActive] = useState<EarnedBadge | null>(null);
  const [busy, setBusy] = useState<'png' | 'svg' | 'share-square' | 'share-wide' | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await badgesApi.myAchievements();
        if (!cancelled) {
          setItems(data.filter((b) => b.status !== 'revoked'));
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

  // Close the detail dialog on Escape.
  useEffect(() => {
    if (!active) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setActive(null);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [active]);

  const download = async (badge: EarnedBadge, format: 'png' | 'svg') => {
    setBusy(format);
    setActionError(null);
    try {
      await badgesApi.download(badge.credential_id, format);
    } catch {
      setActionError(`Could not download the ${format.toUpperCase()}. Please try again.`);
    } finally {
      setBusy(null);
    }
  };

  const downloadShare = async (badge: EarnedBadge, preset: 'square' | 'wide') => {
    setBusy(`share-${preset}`);
    setActionError(null);
    try {
      await badgesApi.downloadShareImage(badge.credential_id, preset);
    } catch {
      setActionError('Could not prepare the share image. Please try again.');
    } finally {
      setBusy(null);
    }
  };

  if (error === 'network') return <NetworkError />;

  const earnedCount = items.length;

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      {/* ── Breadcrumb ── */}
      <nav aria-label="Breadcrumb" className="mb-4">
        <ol className="flex flex-wrap items-center gap-1.5 text-xs text-muted-foreground">
          <li>
            <Link href="/dashboard" className="hover:text-primary">
              Dashboard
            </Link>
          </li>
          <li aria-hidden="true">/</li>
          <li className="text-foreground" aria-current="page">
            Achievements
          </li>
        </ol>
      </nav>

      {/* ── Header ── */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="mb-3 inline-flex items-center gap-2 rounded-pill border border-primary/25 bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
            <Award className="h-3.5 w-3.5" aria-hidden="true" />
            ACHIEVEMENTS
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">
            My Achievements
          </h1>
          <p className="mt-2 max-w-2xl text-muted-foreground">
            Premium digital badges earned through verified progress. Download
            them, share them on LinkedIn, or let anyone confirm them against the
            Code Yaar registry.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link
            href="/dashboard"
            className="focus-ring inline-flex min-h-10 items-center gap-2 rounded-lg border border-border bg-card px-3.5 py-2 text-sm font-medium text-foreground hover:bg-muted"
          >
            <Home className="h-4 w-4" aria-hidden="true" />
            Back to Dashboard
          </Link>
          <Link
            href="/certificates"
            className="focus-ring inline-flex min-h-10 items-center gap-2 rounded-lg bg-cta px-3.5 py-2 text-sm font-semibold text-white hover:bg-cta-hover"
          >
            <ExternalLink className="h-4 w-4" aria-hidden="true" />
            Certificates
          </Link>
        </div>
      </div>

      {actionError && (
        <p
          role="alert"
          className="mb-4 rounded-card border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-600"
        >
          {actionError}
        </p>
      )}

      {/* ── Content ── */}
      {loading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div
              key={i}
              className="h-72 rounded-card border border-border bg-card animate-pulse"
            />
          ))}
        </div>
      ) : error === 'auth' ? (
        <div className="card-hairline p-12 text-center">
          <h2 className="text-lg font-semibold text-foreground">
            Sign in to view achievements
          </h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Badges are awarded by the server when you complete real work.
          </p>
          <Link
            href="/sign-in"
            className="focus-ring mt-6 inline-flex min-h-10 items-center rounded-lg bg-cta px-4 py-2 text-sm font-semibold text-white hover:bg-cta-hover"
          >
            Sign in
          </Link>
        </div>
      ) : earnedCount === 0 ? (
        <div className="card-hairline p-12 text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-primary/10">
            <Award className="h-6 w-6 text-primary" aria-hidden="true" />
          </div>
          <h2 className="mt-4 text-lg font-semibold text-foreground">
            No badges yet
          </h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Finish lessons, solve exercises, and complete courses to earn your
            first Code Yaar badge.
          </p>
          <Link
            href="/learn?view=courses"
            className="focus-ring mt-6 inline-flex min-h-10 items-center rounded-lg bg-cta px-4 py-2 text-sm font-semibold text-white hover:bg-cta-hover"
          >
            Browse courses
          </Link>
        </div>
      ) : (
        <>
          <p className="mb-4 text-sm text-muted-foreground">
            <span className="font-semibold text-foreground">{earnedCount}</span>{' '}
            badge{earnedCount === 1 ? '' : 's'} earned
          </p>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {items.map((badge) => (
              <article
                key={badge.id}
                className="flex flex-col rounded-card border border-border bg-card p-5 transition-shadow hover:shadow-[var(--shadow-1)]"
              >
                <div className="flex items-start gap-4">
                  <BadgeArtwork
                    badge={badge}
                    className="h-20 w-20 shrink-0 rounded-full object-cover shadow-sm"
                  />
                  <div className="min-w-0">
                    <div className="flex flex-wrap gap-1.5">
                      <span className="rounded-pill border border-border bg-muted px-2 py-0.5 text-[11px] font-medium text-muted-foreground">
                        {badge.achievement.category_label}
                      </span>
                      <span
                        className={`rounded-pill border px-2 py-0.5 text-[11px] font-medium ${levelTone(
                          badge.achievement.level_label
                        )}`}
                      >
                        {badge.achievement.level_label}
                      </span>
                    </div>
                    <h2 className="mt-2 text-base font-bold leading-snug text-foreground">
                      {badge.achievement.title}
                    </h2>
                    <p className="mt-1 text-xs text-muted-foreground">
                      Earned {formatShortDate(badge.earned_at)}
                    </p>
                  </div>
                </div>

                <p className="mt-3 line-clamp-2 text-sm text-muted-foreground">
                  {badge.achievement.description}
                </p>

                <p className="mt-3 font-mono text-[11px] text-muted-foreground">
                  {badge.credential_id}
                </p>

                <div className="mt-4 flex flex-wrap gap-2 border-t border-border pt-4">
                  <button
                    type="button"
                    onClick={() => setActive(badge)}
                    className="focus-ring inline-flex min-h-9 items-center gap-1.5 rounded-lg border border-border bg-background px-3 py-1.5 text-xs font-semibold text-foreground hover:bg-muted"
                  >
                    <Eye className="h-3.5 w-3.5" aria-hidden="true" />
                    View details
                  </button>
                  <button
                    type="button"
                    onClick={() => download(badge, 'png')}
                    disabled={busy !== null}
                    className="focus-ring inline-flex min-h-9 items-center rounded-lg bg-cta px-3 py-1.5 text-xs font-semibold text-white hover:bg-cta-hover disabled:opacity-60"
                  >
                    {busy === 'png' ? 'Preparing…' : 'PNG'}
                  </button>
                  <button
                    type="button"
                    onClick={() => download(badge, 'svg')}
                    disabled={busy !== null}
                    className="focus-ring inline-flex min-h-9 items-center rounded-lg border border-border bg-background px-3 py-1.5 text-xs font-semibold text-foreground hover:bg-muted disabled:opacity-60"
                  >
                    {busy === 'svg' ? 'Preparing…' : 'SVG'}
                  </button>
                </div>
              </article>
            ))}
          </div>
        </>
      )}

      {/* ── Detail dialog ── */}
      {active && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-slate-950/60 p-4"
          role="dialog"
          aria-modal="true"
          aria-label={`${active.achievement.title} badge details`}
          onClick={(e) => {
            if (e.target === e.currentTarget) setActive(null);
          }}
        >
          <div className="my-8 w-full max-w-lg rounded-card border border-border bg-card p-6 shadow-[var(--shadow-3)]">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-primary">
                  {active.achievement.category_label}
                </p>
                <h2 className="mt-1 text-xl font-bold text-foreground">
                  {active.achievement.title}
                </h2>
              </div>
              <button
                type="button"
                onClick={() => setActive(null)}
                aria-label="Close"
                className="focus-ring flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-muted-foreground hover:bg-muted"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="mt-5 flex flex-col items-center text-center">
              <BadgeArtwork
                badge={active}
                className="h-56 w-56 rounded-full object-cover"
              />
              <p className="mt-4 text-sm text-muted-foreground">
                {active.achievement.description}
              </p>
            </div>

            {/* LinkedIn-ready achievement graphic — the standalone credential
                image a learner attaches to a post (not a dashboard screenshot). */}
            {active.is_valid && (
              <div className="mt-5">
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  LinkedIn share graphic
                </p>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={badgesApi.shareImageUrl(active.credential_id, 'square')}
                  alt={`${active.achievement.title} — Code Yaar Academy share graphic`}
                  className="w-full rounded-card border border-border"
                  loading="lazy"
                />
              </div>
            )}

            <dl className="mt-5 grid grid-cols-2 gap-3 rounded-card border border-border bg-background p-4 text-sm">
              <div>
                <dt className="text-xs text-muted-foreground">Recipient</dt>
                <dd className="mt-0.5 font-semibold text-foreground">
                  {active.recipient_name}
                </dd>
              </div>
              <div>
                <dt className="text-xs text-muted-foreground">Level</dt>
                <dd className="mt-0.5 font-semibold text-foreground">
                  {active.achievement.level_label}
                </dd>
              </div>
              <div>
                <dt className="text-xs text-muted-foreground">Earned</dt>
                <dd className="mt-0.5 text-foreground">
                  {formatShortDate(active.earned_at)}
                </dd>
              </div>
              <div>
                <dt className="text-xs text-muted-foreground">Badge ID</dt>
                <dd className="mt-0.5 font-mono text-xs text-foreground">
                  {active.credential_id}
                </dd>
              </div>
            </dl>

            <div className="mt-5 flex flex-wrap gap-2">
              <DownloadButton
                onClick={() => download(active, 'png')}
                busy={busy === 'png'}
                label="Download PNG"
              />
              <DownloadButton
                onClick={() => download(active, 'svg')}
                busy={busy === 'svg'}
                label="Download SVG"
                variant="outline"
              />
              {active.is_valid && (
                <>
                  <DownloadButton
                    onClick={() => downloadShare(active, 'square')}
                    busy={busy === 'share-square'}
                    label="Share image (1:1)"
                    variant="outline"
                  />
                  <DownloadButton
                    onClick={() => downloadShare(active, 'wide')}
                    busy={busy === 'share-wide'}
                    label="Share image (link)"
                    variant="outline"
                  />
                </>
              )}
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              <LinkedInShareButton
                url={active.verification_url}
                text={badgeShareText({
                  badgeTitle: active.achievement.title,
                  verificationUrl: active.verification_url,
                })}
                variant="outline"
              />
              <CopyLinkButton url={active.verification_url} />
              <a
                href={active.verification_url}
                target="_blank"
                rel="noopener noreferrer"
                className="focus-ring inline-flex min-h-10 items-center gap-2 rounded-lg border border-border bg-card px-4 py-2 text-sm font-semibold text-foreground hover:bg-muted"
              >
                <ExternalLink className="h-4 w-4" aria-hidden="true" />
                Verify
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
