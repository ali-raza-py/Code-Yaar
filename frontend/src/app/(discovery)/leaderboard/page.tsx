'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { leaderboard as leaderboardApi, ApiError, type LeaderboardEntry } from '@/lib/api';
import { useAuth } from '@/hooks/use-auth';
import { NetworkError } from '@/components/learning/workspace/error-states';
import { Avatar } from '@/components/ui/avatar';

/**
 * PUBLIC leaderboard, dual mode by design: visitors see a top-10 teaser and
 * a join CTA (rankings are real API data, never invented), while signed-in
 * students get the full board with their own row highlighted. The API
 * answers anonymous reads, so this page is a marketing surface — not a
 * security boundary.
 */

// Visitors get a teaser; students get the whole board.
const ANON_LIMIT = 10;
const STUDENT_LIMIT = 50;

export default function LeaderboardPage() {
  const { user, loading: authLoading } = useAuth();
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // The signed-in user's id comes straight from the auth context — no extra
  // profile round trip needed to highlight their own row.
  const currentUserId = user?.id ?? null;

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await leaderboardApi.list({ limit: user ? STUDENT_LIMIT : ANON_LIMIT });
        if (cancelled) return;
        setEntries(data.entries);
        setError(null);
      } catch (e) {
        if (cancelled) return;
        setError(e instanceof ApiError && e.status === 401 ? 'auth' : 'network');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [user]);

  const getRankBadge = (rank: number) => {
    if (rank === 1) return { bg: 'bg-warning/20', text: 'text-tone-amber-fg', icon: '🥇' };
    if (rank === 2) return { bg: 'bg-muted', text: 'text-muted-foreground', icon: '🥈' };
    if (rank === 3) return { bg: 'bg-warning/10', text: 'text-tone-amber-fg/80', icon: '🥉' };
    return { bg: 'bg-card', text: 'text-muted-foreground', icon: String(rank) };
  };

  if (error === 'network') return <NetworkError />;

  const signedIn = Boolean(user);

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8">
        <div className="mb-3 inline-flex items-center gap-2 rounded-pill border border-primary/25 bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 01-.982-3.172M9.497 14.25a7.454 7.454 0 00.981-3.172M5.25 4.236c-.982.143-1.954.317-2.916.52A6.003 6.003 0 007.73 9.728M5.25 4.236V4.5c0 2.108.966 3.99 2.48 5.228M5.25 4.236V2.721C7.456 2.41 9.71 2.25 12 2.25c2.291 0 4.545.16 6.75.47v1.516M18.75 4.236c.982.143 1.954.317 2.916.52A6.003 6.003 0 0116.27 9.728M18.75 4.236V4.5c0 2.108-.966 3.99-2.48 5.228m0 0a6.023 6.023 0 01-2.77.852m0 0l-.5.075a7.48 7.48 0 01-1 .067 7.48 7.48 0 01-1-.067l-.5-.075m3 0a6.022 6.022 0 01-2.77-.852" />
          </svg>
          LEADERBOARD
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">
          Community Rankings
        </h1>
        <p className="mt-2 text-muted-foreground">
          See who&apos;s leading the Code-Yaar community. Rankings are based on total XP earned.
        </p>
      </div>

      {/* Leaderboard Table */}
      {loading || authLoading ? (
        <div className="space-y-2">
          {Array.from({ length: signedIn ? 10 : ANON_LIMIT }).map((_, i) => (
            <div key={i} className="flex items-center gap-4 rounded-card border border-border bg-card p-4 animate-pulse">
              <div className="h-8 w-8 rounded-full bg-muted" />
              <div className="h-4 w-24 rounded bg-muted" />
              <div className="flex-1" />
              <div className="h-4 w-16 rounded bg-muted/60" />
            </div>
          ))}
        </div>
      ) : entries.length === 0 ? (
        <div className="card-hairline p-12 text-center">
          <svg className="mx-auto h-10 w-10 text-muted-foreground/50" fill="none" viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 01-.982-3.172M9.497 14.25a7.454 7.454 0 00.981-3.172M5.25 4.236c-.982.143-1.954.317-2.916.52A6.003 6.003 0 007.73 9.728M5.25 4.236V4.5c0 2.108.966 3.99 2.48 5.228M5.25 4.236V2.721C7.456 2.41 9.71 2.25 12 2.25c2.291 0 4.545.16 6.75.47v1.516M18.75 4.236c.982.143 1.954.317 2.916.52A6.003 6.003 0 0116.27 9.728M18.75 4.236V4.5c0 2.108-.966 3.99-2.48 5.228m0 0a6.023 6.023 0 01-2.77.852m0 0l-.5.075a7.48 7.48 0 01-1 .067 7.48 7.48 0 01-1-.067l-.5-.075m3 0a6.022 6.022 0 01-2.77-.852" />
          </svg>
          <h2 className="mt-4 text-lg font-semibold text-foreground">No rankings yet</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Be the first to earn XP and claim the top spot!
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {entries.map((entry) => {
            const badge = getRankBadge(entry.rank);
            const isCurrentUser = entry.user_id === currentUserId;
            return (
              <div
                key={entry.user_id}
                className={`flex items-center gap-4 rounded-card border p-4 transition-colors ${
                  isCurrentUser
                    ? 'border-primary/30 bg-primary/5'
                    : 'border-border bg-card hover:bg-muted/50'
                }`}
              >
                {/* Rank */}
                <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-bold ${badge.bg} ${badge.text}`}>
                  {entry.rank <= 3 ? badge.icon : entry.rank}
                </div>

                {/* Avatar — shared initials primitive (no invented photos) */}
                <Avatar username={entry.username} name={entry.username} size={36} />

                {/* Username */}
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-semibold truncate ${isCurrentUser ? 'text-primary' : 'text-foreground'}`}>
                    <Link href={`/profile/${entry.username}`} className="hover:underline">
                      {entry.username}
                    </Link>
                    {isCurrentUser && <span className="ml-2 text-xs font-normal text-primary">(You)</span>}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Level {entry.level} · {entry.streak_days} day streak
                  </p>
                </div>

                {/* Stats */}
                <div className="hidden sm:flex items-center gap-4 text-xs text-muted-foreground">
                  <span>{entry.courses_completed} courses</span>
                  <span>{entry.challenges_solved} solved</span>
                </div>

                {/* XP */}
                <div className="text-right">
                  <p className="text-sm font-bold text-foreground">{entry.xp_points.toLocaleString()}</p>
                  <p className="text-xs text-muted-foreground">XP</p>
                </div>
              </div>
            );
          })}

          {/* Visitors get a teaser — the join CTA is the point of the page. */}
          {!signedIn && (
            <div className="rounded-card border border-primary/25 bg-primary/[0.04] p-6 text-center">
              <h2 className="text-lg font-bold text-foreground">Your name could be on this board</h2>
              <p className="mx-auto mt-2 max-w-md text-sm text-muted-foreground">
                Every lesson, exercise and challenge you complete earns XP. Create a free
                account to start climbing the rankings.
              </p>
              <div className="mt-4 flex flex-wrap items-center justify-center gap-3">
                <Link
                  href="/sign-up?next=%2Fleaderboard"
                  className="inline-flex h-10 items-center rounded-lg bg-cta px-4 text-sm font-semibold text-cta-fg transition-colors hover:bg-cta-hover"
                >
                  Get started free
                </Link>
                <Link
                  href="/sign-in?next=%2Fleaderboard"
                  className="inline-flex h-10 items-center rounded-lg border border-border px-4 text-sm font-semibold text-foreground transition-colors hover:bg-muted"
                >
                  Sign in
                </Link>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
