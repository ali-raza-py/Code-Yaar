'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { Award, ExternalLink, Eye, Filter, Home, Lock, X } from 'lucide-react';
import {
  ApiError,
  achievements as achievementsApi,
  badges as badgesApi,
  type AchievementDefinition,
  type EarnedBadge,
} from '@/lib/api';
import { badgeShareText, formatShortDate } from '@/lib/share';
import {
  CopyLinkButton,
  DownloadButton,
  LinkedInShareButton,
} from '@/components/credentials/credential-actions';
import { NetworkError } from '@/components/learning/workspace/error-states';
import { AchievementIcon } from '@/components/achievements/achievement-icon';
import { DifficultyPill } from '@/components/ui/difficulty-pill';

const DIFFICULTY_FILTERS = ['all', 'beginner', 'intermediate', 'advanced'] as const;
type StatusFilter = 'all' | 'earned' | 'locked';

/** Linear progress bar built from design tokens (no raw hex). */
function ProgressBar({ current, target }: { current: number; target: number }) {
  const pct = target > 0 ? Math.min(100, Math.round((current / target) * 100)) : 0;
  return (
    <div>
      <div className="h-2 w-full overflow-hidden rounded-pill bg-muted">
        <div className="h-full rounded-pill bg-primary" style={{ width: `${pct}%` }} />
      </div>
      <p className="mt-1 text-[11px] text-muted-foreground">
        {current} / {target} · {pct}%
      </p>
    </div>
  );
}

/** Earned artwork from the real record, or a placeholder medallion otherwise. */
function TileArtwork({
  definition,
  earned,
  className,
}: {
  definition: AchievementDefinition;
  earned?: EarnedBadge;
  className?: string;
}) {
  const [failed, setFailed] = useState(false);
  if (earned && earned.is_valid && !failed) {
    return (
      // Official artwork served by Django from the real record — the same file
      // the Download actions deliver, so preview and download never diverge.
      // eslint-disable-next-line @next/next/no-img-element
      <img
        src={badgesApi.publicImageUrl(earned.public_id)}
        alt={`${definition.title} badge`}
        className={className}
        onError={() => setFailed(true)}
        loading="lazy"
      />
    );
  }
  return (
    <div
      className={`flex items-center justify-center rounded-full ${
        earned ? 'bg-gradient-to-br from-primary/15 to-primary/5' : 'bg-muted'
      } ${className ?? ''}`}
      aria-hidden="true"
    >
      <Award
        className={`h-1/3 w-1/3 ${earned ? 'text-primary' : 'text-muted-foreground'}`}
      />
    </div>
  );
}

/**
 * The achievements experience body, shared by the standalone /achievements
 * page and the My Progress > Achievements tab. `compact` drops the breadcrumb
 * and page header when the shell already labels the view; the sibling links
 * retarget to the tabbed routes so the two entry points stay consistent.
 */
export function AchievementsTabBody({
  compact = false,
  overviewHref = '/dashboard',
  certificatesHref = '/certificates',
}: {
  compact?: boolean;
  overviewHref?: string;
  certificatesHref?: string;
}) {
  const [defs, setDefs] = useState<AchievementDefinition[]>([]);
  const [earnedMap, setEarnedMap] = useState<Record<string, EarnedBadge>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<'auth' | 'network' | null>(null);

  const [category, setCategory] = useState('all');
  const [difficulty, setDifficulty] = useState<(typeof DIFFICULTY_FILTERS)[number]>('all');
  const [status, setStatus] = useState<StatusFilter>('all');

  const [active, setActive] = useState<AchievementDefinition | null>(null);
  const [busy, setBusy] = useState<'png' | 'svg' | 'share-square' | 'share-wide' | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [catalogue, earned] = await Promise.all([
          achievementsApi.list(),
          badgesApi.myAchievements(),
        ]);
        if (cancelled) return;
        const map: Record<string, EarnedBadge> = {};
        for (const b of earned) {
          if (b.status === 'revoked') continue;
          // Keep the most recent award if a definition somehow has several.
          if (!map[b.achievement.slug]) map[b.achievement.slug] = b;
        }
        setDefs(catalogue);
        setEarnedMap(map);
        setError(null);
      } catch (e) {
        if (!cancelled) setError(e instanceof ApiError && e.status === 401 ? 'auth' : 'network');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
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

  const categories = useMemo(() => {
    const set = new Map<string, string>();
    for (const d of defs) set.set(d.category, d.category_label);
    return Array.from(set.entries()).sort((a, b) => a[1].localeCompare(b[1]));
  }, [defs]);

  const visible = useMemo(
    () =>
      defs.filter((d) => {
        if (category !== 'all' && d.category !== category) return false;
        if (difficulty !== 'all' && d.difficulty !== difficulty) return false;
        if (status === 'earned' && !d.earned) return false;
        if (status === 'locked' && d.earned) return false;
        return true;
      }),
    [defs, category, difficulty, status]
  );

  const earnedCount = useMemo(
    () => defs.filter((d) => d.earned).length,
    [defs]
  );

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

  const activeEarned = active ? earnedMap[active.slug] : undefined;

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      {/* ── Breadcrumb ── */}
      {!compact && (
        <nav aria-label="Breadcrumb" className="mb-4">
          <ol className="flex flex-wrap items-center gap-1.5 text-xs text-muted-foreground">
            <li>
              <Link href={overviewHref} className="hover:text-primary">
                {overviewHref === '/dashboard' ? 'Dashboard' : 'My Progress'}
              </Link>
            </li>
            <li aria-hidden="true">/</li>
            <li className="text-foreground" aria-current="page">
              Achievements
            </li>
          </ol>
        </nav>
      )}

      {/* ── Header ── */}
      {!compact && (
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <div className="mb-3 inline-flex items-center gap-2 rounded-pill border border-primary/25 bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
              <Award className="h-3.5 w-3.5" aria-hidden="true" />
              ACHIEVEMENTS
            </div>
            <h1 className="text-3xl font-bold tracking-tight text-foreground">
              Achievements
            </h1>
            <p className="mt-2 max-w-2xl text-muted-foreground">
              Every badge the Code Yaar academy can award — earned and yet to come.
              Finish real work to unlock them, then download and share verified
              credentials.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Link
              href={overviewHref}
              className="focus-ring inline-flex min-h-10 items-center gap-2 rounded-lg border border-border bg-card px-3.5 py-2 text-sm font-medium text-foreground hover:bg-muted"
            >
              <Home className="h-4 w-4" aria-hidden="true" />
              Back to Dashboard
            </Link>
            <Link
              href={certificatesHref}
              className="focus-ring inline-flex min-h-10 items-center gap-2 rounded-lg bg-cta px-3.5 py-2 text-sm font-semibold text-white hover:bg-cta-hover"
            >
              <ExternalLink className="h-4 w-4" aria-hidden="true" />
              Certificates
            </Link>
          </div>
        </div>
      )}

      {actionError && (
        <p
          role="alert"
          className="mb-4 rounded-card border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-600"
        >
          {actionError}
        </p>
      )}

      {/* ── Filters ── */}
      {!loading && error !== 'auth' && defs.length > 0 && (
        <div className="mb-6 flex flex-col gap-3 rounded-card border border-border bg-card p-4 sm:flex-row sm:flex-wrap sm:items-center">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            <Filter className="h-4 w-4" aria-hidden="true" />
            Filter
          </div>
          <label className="flex items-center gap-2 text-sm">
            <span className="text-muted-foreground">Category</span>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="focus-ring rounded-lg border border-border bg-background px-2.5 py-1.5 text-sm text-foreground"
            >
              <option value="all">All categories</option>
              {categories.map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <div className="flex flex-wrap items-center gap-1.5" role="group" aria-label="Difficulty">
            {DIFFICULTY_FILTERS.map((d) => (
              <button
                key={d}
                type="button"
                onClick={() => setDifficulty(d)}
                aria-pressed={difficulty === d}
                className={`focus-ring min-h-9 rounded-lg border px-3 py-1.5 text-xs font-semibold capitalize ${
                  difficulty === d
                    ? 'border-primary bg-primary/10 text-primary'
                    : 'border-border bg-background text-foreground hover:bg-muted'
                }`}
              >
                {d === 'all' ? 'Any level' : d}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-1.5" role="group" aria-label="Status">
            {(['all', 'earned', 'locked'] as StatusFilter[]).map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => setStatus(s)}
                aria-pressed={status === s}
                className={`focus-ring min-h-9 rounded-lg border px-3 py-1.5 text-xs font-semibold capitalize ${
                  status === s
                    ? 'border-primary bg-primary/10 text-primary'
                    : 'border-border bg-background text-foreground hover:bg-muted'
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ── Content ── */}
      {loading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="h-64 rounded-card border border-border bg-card animate-pulse"
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
      ) : defs.length === 0 ? (
        <div className="card-hairline p-12 text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-primary/10">
            <Award className="h-6 w-6 text-primary" aria-hidden="true" />
          </div>
          <h2 className="mt-4 text-lg font-semibold text-foreground">
            No badges available yet
          </h2>
          <p className="mt-2 text-sm text-muted-foreground">
            The badge registry is empty right now. Check back soon.
          </p>
        </div>
      ) : (
        <>
          <p className="mb-4 text-sm text-muted-foreground">
            <span className="font-semibold text-foreground">{earnedCount}</span> of{' '}
            <span className="font-semibold text-foreground">{defs.length}</span> badges earned
          </p>
          {visible.length === 0 ? (
            <div className="card-hairline p-10 text-center text-sm text-muted-foreground">
              No badges match these filters.
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {visible.map((d) => {
                const earned = earnedMap[d.slug];
                return (
                  <article
                    key={d.id}
                    className={`flex flex-col rounded-card border border-border bg-card p-5 transition-shadow hover:shadow-[var(--shadow-1)] ${
                      d.earned ? '' : 'opacity-95'
                    }`}
                  >
                    <div className="flex items-start gap-4">
                      {earned ? (
                        <TileArtwork
                          definition={d}
                          earned={earned}
                          className="h-20 w-20 shrink-0 rounded-full object-cover shadow-sm"
                        />
                      ) : (
                        <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-full border border-dashed border-border bg-muted text-muted-foreground">
                          <AchievementIcon name={d.icon} className="h-8 w-8" />
                        </div>
                      )}
                      <div className="min-w-0">
                        <div className="flex flex-wrap gap-1.5">
                          <span className="rounded-pill border border-border bg-muted px-2 py-0.5 text-[11px] font-medium text-muted-foreground">
                            {d.category_label}
                          </span>
                          <DifficultyPill difficulty={d.difficulty} label={d.difficulty_label} size="sm" />
                        </div>
                        <h2 className="mt-2 text-base font-bold leading-snug text-foreground">
                          {d.title}
                        </h2>
                        <p className="mt-1 text-xs text-muted-foreground">
                          {d.earned && earned
                            ? `Earned ${formatShortDate(earned.earned_at)}`
                            : d.level_label}
                        </p>
                      </div>
                    </div>

                    <p className="mt-3 line-clamp-2 text-sm text-muted-foreground">
                      {d.description}
                    </p>

                    <div className="mt-3 border-t border-border pt-3">
                      {d.earned && earned ? (
                        <div className="flex flex-wrap gap-2">
                          <button
                            type="button"
                            onClick={() => setActive(d)}
                            className="focus-ring inline-flex min-h-9 items-center gap-1.5 rounded-lg border border-border bg-background px-3 py-1.5 text-xs font-semibold text-foreground hover:bg-muted"
                          >
                            <Eye className="h-3.5 w-3.5" aria-hidden="true" />
                            View &amp; share
                          </button>
                        </div>
                      ) : (
                        <div className="flex items-center justify-between gap-2">
                          <span className="inline-flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
                            <Lock className="h-3.5 w-3.5" aria-hidden="true" />
                            Locked
                          </span>
                          <button
                            type="button"
                            onClick={() => setActive(d)}
                            className="focus-ring inline-flex min-h-9 items-center gap-1.5 rounded-lg border border-border bg-background px-3 py-1.5 text-xs font-semibold text-foreground hover:bg-muted"
                          >
                            How to earn
                          </button>
                        </div>
                      )}
                      {!d.earned && d.progress && (
                        <div className="mt-3">
                          <ProgressBar current={d.progress.current} target={d.progress.target} />
                        </div>
                      )}
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </>
      )}

      {/* ── Detail dialog ── */}
      {active && (
        <div
          className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-slate-950/60 p-4"
          role="dialog"
          aria-modal="true"
          aria-label={`${active.title} details`}
          onClick={(e) => {
            if (e.target === e.currentTarget) setActive(null);
          }}
        >
          <div className="my-8 w-full max-w-lg rounded-card border border-border bg-card p-6 shadow-[var(--shadow-3)]">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-primary">
                  {active.category_label}
                </p>
                <h2 className="mt-1 text-xl font-bold text-foreground">{active.title}</h2>
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

            {activeEarned ? (
              <>
                <div className="mt-5 flex flex-col items-center text-center">
                  <TileArtwork
                    definition={active}
                    earned={activeEarned}
                    className="h-56 w-56 rounded-full object-cover"
                  />
                  <p className="mt-4 text-sm text-muted-foreground">{active.description}</p>
                </div>

                {activeEarned.is_valid && (
                  <div className="mt-5">
                    <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                      LinkedIn share graphic
                    </p>
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={badgesApi.shareImageUrl(activeEarned.credential_id, 'square')}
                      alt={`${active.title} — Code Yaar Academy share graphic`}
                      className="mx-auto block max-h-[60vh] w-auto rounded-card border border-border"
                      loading="lazy"
                    />
                  </div>
                )}

                <dl className="mt-5 grid grid-cols-2 gap-3 rounded-card border border-border bg-background p-4 text-sm">
                  <div>
                    <dt className="text-xs text-muted-foreground">Recipient</dt>
                    <dd className="mt-0.5 font-semibold text-foreground">
                      {activeEarned.recipient_name}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs text-muted-foreground">Level</dt>
                    <dd className="mt-0.5 font-semibold text-foreground">{active.level_label}</dd>
                  </div>
                  <div>
                    <dt className="text-xs text-muted-foreground">Earned</dt>
                    <dd className="mt-0.5 text-foreground">
                      {formatShortDate(activeEarned.earned_at)}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs text-muted-foreground">Difficulty</dt>
                    <dd className="mt-0.5">
                      <DifficultyPill difficulty={active.difficulty} label={active.difficulty_label} size="sm" />
                    </dd>
                  </div>
                </dl>

                <div className="mt-5 flex flex-wrap gap-2">
                  <DownloadButton
                    onClick={() => download(activeEarned, 'png')}
                    busy={busy === 'png'}
                    label="Download PNG"
                  />
                  <DownloadButton
                    onClick={() => download(activeEarned, 'svg')}
                    busy={busy === 'svg'}
                    label="Download SVG"
                    variant="outline"
                  />
                  {activeEarned.is_valid && (
                    <>
                      <DownloadButton
                        onClick={() => downloadShare(activeEarned, 'square')}
                        busy={busy === 'share-square'}
                        label="Share image (1:1)"
                        variant="outline"
                      />
                      <DownloadButton
                        onClick={() => downloadShare(activeEarned, 'wide')}
                        busy={busy === 'share-wide'}
                        label="Share image (link)"
                        variant="outline"
                      />
                    </>
                  )}
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  <LinkedInShareButton
                    url={activeEarned.verification_url}
                    text={badgeShareText({
                      badgeTitle: active.title,
                      verificationUrl: activeEarned.verification_url,
                    })}
                    variant="outline"
                  />
                  <CopyLinkButton url={activeEarned.verification_url} />
                  <a
                    href={activeEarned.verification_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="focus-ring inline-flex min-h-10 items-center gap-2 rounded-lg border border-border bg-card px-4 py-2 text-sm font-semibold text-foreground hover:bg-muted"
                  >
                    <ExternalLink className="h-4 w-4" aria-hidden="true" />
                    Verify
                  </a>
                </div>
              </>
            ) : (
              <>
                <div className="mt-5 flex flex-col items-center text-center">
                  <div className="flex h-40 w-40 items-center justify-center rounded-full border border-dashed border-border bg-muted text-muted-foreground">
                    <AchievementIcon name={active.icon} className="h-16 w-16" />
                  </div>
                  <p className="mt-4 text-sm text-muted-foreground">{active.description}</p>
                </div>

                <div className="mt-5 rounded-card border border-border bg-background p-4">
                  <p className="text-xs font-semibold uppercase tracking-wide text-primary">
                    How to earn
                  </p>
                  <p className="mt-1 text-sm text-foreground">{active.how_to_earn}</p>
                  <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                    <DifficultyPill difficulty={active.difficulty} label={active.difficulty_label} size="sm" />
                    <span className="rounded-pill border border-border bg-muted px-2 py-0.5">
                      +{active.xp_bonus} XP
                    </span>
                  </div>
                </div>

                {active.progress ? (
                  <div className="mt-4">
                    <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                      Your progress
                    </p>
                    <ProgressBar current={active.progress.current} target={active.progress.target} />
                  </div>
                ) : (
                  <p className="mt-4 text-sm text-muted-foreground">
                    Not started yet — keep learning to work toward this badge.
                  </p>
                )}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
