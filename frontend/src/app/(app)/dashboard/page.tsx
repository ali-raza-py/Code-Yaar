"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { ArrowRight, Trophy, BookOpen } from "lucide-react";
import { leaderboard as leaderboardApi, profileStats } from "@/lib/api";
import type { LeaderboardEntry, ProfileStatsData } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { NetworkError } from "@/components/learning/workspace/error-states";

function timeAgo(iso: string): string {
  const seconds = Math.max(0, Math.floor((Date.now() - new Date(iso).getTime()) / 1000));
  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  return new Date(iso).toLocaleDateString();
}

export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const [stats, setStats] = useState<ProfileStatsData | null>(null);
  const [topLearners, setTopLearners] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const load = useCallback(async () => {
    if (!user) return;
    try {
      const [statsData, board] = await Promise.all([profileStats.get(), leaderboardApi.list({ limit: 10 })]);
      setStats(statsData);
      setTopLearners(board.entries);
      setError(false);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    // Deferred via await so the effect never sets state synchronously.
    (async () => { await load(); })();
  }, [load]);

  // ── Loading ──────────────────────────────────────────────────────────────
  if (authLoading || (loading && user)) {
    return (
      <div className="mx-auto max-w-7xl animate-pulse px-4 py-6 sm:px-6 lg:px-8">
        <div className="mb-6 h-8 w-48 rounded bg-white" />
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="space-y-6 lg:col-span-2">
            <div className="h-40 rounded-xl bg-white" />
            <div className="h-32 rounded-xl bg-white" />
          </div>
          <div className="h-64 rounded-xl bg-white" />
        </div>
      </div>
    );
  }

  // ── Error ────────────────────────────────────────────────────────────────
  if (error) {
    return <NetworkError onRetry={load} />;
  }

  // ── Unauthenticated ──────────────────────────────────────────────────────
  if (!user) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 text-center sm:px-6">
        <h1 className="text-2xl font-bold text-foreground">Your dashboard starts here</h1>
        <p className="mt-3 text-sm text-muted-foreground">
          Sign in to track your courses, XP, streak, and learning activity — or create a free account
          to begin Python Foundations.
        </p>
        <div className="mt-6 flex items-center justify-center gap-3">
          <Link href="/sign-in" className="rounded-lg bg-cta px-5 py-2.5 text-sm font-bold text-white hover:bg-cta-hover">
            Sign in
          </Link>
          <Link href="/sign-up" className="rounded-lg border border-border px-5 py-2.5 text-sm font-medium text-foreground hover:bg-muted">
            Create account
          </Link>
        </div>
        <div className="mt-10 grid gap-4 text-left sm:grid-cols-2">
          <Link href="/courses/python-foundations" className="card-hairline p-5 transition-colors hover:border-primary">
            <h3 className="font-semibold text-foreground">Python Foundations</h3>
            <p className="mt-1 text-sm text-muted-foreground">Free, hands-on introduction course.</p>
          </Link>
          <Link href="/learn" className="card-hairline p-5 transition-colors hover:border-primary">
            <h3 className="font-semibold text-foreground">Browse all courses</h3>
            <p className="mt-1 text-sm text-muted-foreground">See everything available on Code Yaar.</p>
          </Link>
        </div>
      </div>
    );
  }

  const displayName = stats?.user.first_name || stats?.user.username || user.username;
  const enrollment = stats?.active_enrollments[0] ?? null;
  const profile = stats?.profile;
  const activity = stats?.xp_history ?? [];

  // Getting-started checklist from real records
  const checklist = [
    { label: 'Complete your profile', done: Boolean(profile?.avatar || profile?.bio), href: '/settings' },
    { label: 'Enroll in a course', done: (stats?.stats.total_enrollments ?? 0) > 0, href: '/learn' },
    { label: 'Finish your first lesson', done: (stats?.stats.lessons_completed ?? 0) > 0, href: '/learn' },
    { label: 'Solve your first exercise', done: (stats?.stats.unique_exercises_solved ?? 0) > 0, href: '/learn' },
  ];
  const doneCount = checklist.filter((item) => item.done).length;
  const userRank = topLearners.find((entry) => entry.user_id === stats?.user.id)?.rank ?? null;

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      {/* Top bar */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3"><h1 className="text-2xl font-bold text-foreground">My Activity</h1><Link href="/progress" className="rounded-lg bg-cta/10 px-3 py-1.5 text-xs font-bold text-cta hover:bg-cta/20">View progress</Link></div>
          <p className="mt-1 text-sm text-muted-foreground">Level {profile?.level ?? 1} · {displayName}</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* LEFT — Main content (2/3) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Continue Learning card */}
          <div className="overflow-hidden rounded-xl bg-hero-navy text-white">
            <div className="p-6 sm:p-8">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <div className="text-xs font-semibold uppercase tracking-wider text-white/50">
                    {enrollment ? 'Continue where you left off' : 'Your learning'}
                  </div>
                  <h2 className="mt-1 text-2xl font-bold sm:text-3xl">
                    {enrollment ? enrollment.course_title : 'No active courses yet'}
                  </h2>
                  <p className="mt-2 text-sm text-white/60">
                    {enrollment
                      ? `${enrollment.progress_percentage}% complete · Part of the ${enrollment.track_title} track`
                      : 'Pick a course to start your structured path.'}
                  </p>
                </div>
                <Link
                  href={enrollment ? `/learn/${enrollment.course_slug}` : '/learn'}
                  className="inline-flex items-center justify-center gap-2 rounded-lg bg-cta px-6 py-3 text-sm font-bold text-white transition-colors hover:bg-cta-hover whitespace-nowrap"
                >
                  {enrollment ? 'Continue Learning' : 'Browse Courses'}
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          </div>

          {/* Practice section (honest, no invented quotas) */}
          <div>
            <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-foreground">
              <BookOpen className="h-5 w-5 text-primary" />
              Practice
            </h2>
            <div className="card-hairline p-6">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h3 className="font-bold text-foreground">
                    {stats ? `${stats.stats.unique_exercises_solved} exercises solved · ${stats.stats.total_attempts} attempts` : 'Apply what you learn'}
                  </h3>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Exercises and challenges are graded server-side. Code evaluation via the sandbox
                    service is still being rolled out.
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Link href="/learn" className="inline-flex items-center gap-1 rounded-lg border border-[var(--color-section-border)] bg-[var(--color-section-light)] px-3 py-1.5 text-sm font-medium text-foreground">
                    Course exercises
                  </Link>
                  <Link href="/challenges" className="inline-flex items-center gap-1 text-sm font-medium text-primary hover:underline">
                    View challenges <ArrowRight className="h-3.5 w-3.5" />
                  </Link>
                </div>
              </div>
            </div>
          </div>

          {/* Recent activity — real XP ledger */}
          <div className="card-hairline p-6">
            <h2 className="font-bold text-foreground">Recent activity</h2>
            {activity.length === 0 ? (
              <p className="mt-3 text-sm text-muted-foreground">
                Nothing here yet. Complete a lesson or exercise and your XP history will appear.
              </p>
            ) : (
              <ul className="mt-3 space-y-3">
                {activity.slice(0, 6).map((item) => (
                  <li key={item.id} className="flex items-start justify-between gap-3 text-sm">
                    <span className="text-foreground">{item.description || item.action.replace(/_/g, ' ')}</span>
                    <span className="shrink-0 text-xs text-muted-foreground">
                      <span className={item.amount >= 0 ? 'font-semibold text-cta' : 'font-semibold text-danger'}>
                        {item.amount >= 0 ? `+${item.amount}` : item.amount} XP
                      </span>
                      <span className="ml-2">{timeAgo(item.created_at)}</span>
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Quick access grid */}
          <div className="grid gap-4 sm:grid-cols-2">
            <Link href="/learn" className="group card-hairline p-5 transition-colors hover:border-primary">
              <h3 className="font-semibold text-foreground group-hover:text-[var(--primary)]">Courses</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Structured lessons with hands-on exercises.
              </p>
              <div className="mt-3 text-sm font-medium text-primary">
                Browse courses <ArrowRight className="ml-1 inline h-3.5 w-3.5" />
              </div>
            </Link>
            <Link href="/projects" className="group card-hairline p-5 transition-colors hover:border-primary">
              <h3 className="font-semibold text-foreground group-hover:text-[var(--primary)]">Real World Projects</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Apply your knowledge to practical scenarios.
              </p>
              <div className="mt-3 text-sm font-medium text-primary">
                Browse projects <ArrowRight className="ml-1 inline h-3.5 w-3.5" />
              </div>
            </Link>
          </div>
        </div>

        {/* RIGHT — Sidebar (1/3) */}
        <div className="space-y-6">
          {/* Streak + XP from the server-side profile */}
          <div className="card-hairline p-6">
            <div className="flex items-center gap-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-primary to-cta text-xl font-bold text-white">
                {(displayName || '?').charAt(0).toUpperCase()}
              </div>
              <div>
                <div className="text-lg font-bold text-foreground">{displayName}</div>
                <div className="mt-2">
                  <div className="text-xs text-muted-foreground">Daily Streak</div>
                  <div className="text-lg font-bold text-foreground">{profile?.streak_days ?? 0} days</div>
                </div>
                <div className="mt-2">
                  <div className="text-xs text-muted-foreground">Total XP</div>
                  <div className="text-lg font-bold text-foreground">{(profile?.xp_points ?? 0).toLocaleString()} XP</div>
                </div>
              </div>
            </div>
          </div>

          {/* Leaderboard snapshot */}
          <div className="card-hairline p-6">
            <div className="flex items-center justify-between">
              <h3 className="flex items-center gap-2 font-bold text-foreground">
                <Trophy className="h-5 w-5 text-amber" />
                Leaderboard
              </h3>
              <Link href="/leaderboard" className="text-sm font-medium text-primary hover:underline">
                View all
              </Link>
            </div>
            {topLearners.length === 0 ? (
              <p className="mt-4 text-sm text-muted-foreground">
                The leaderboard is empty. Earn XP from lessons and exercises to appear here.
              </p>
            ) : (
              <>
                <ol className="mt-4 space-y-2">
                  {topLearners.slice(0, 5).map((entry) => (
                    <li key={entry.rank} className={`flex items-center justify-between rounded-lg px-2.5 py-1.5 text-sm ${entry.user_id === stats?.user.id ? 'bg-cta/10 font-semibold' : ''}`}>
                      <span className="flex items-center gap-2 text-foreground">
                        <span className="w-5 text-muted-foreground">{entry.rank}</span>
                        {entry.username}
                      </span>
                      <span className="text-muted-foreground">{entry.xp_points.toLocaleString()} XP</span>
                    </li>
                  ))}
                </ol>
                <p className="mt-3 text-xs text-muted-foreground">
                  {userRank !== null ? `You're ranked #${userRank} overall.` : "You're not in the top 10 yet."}
                </p>
              </>
            )}
          </div>

          {/* Getting Started — derived from real records */}
          <div className="rounded-xl bg-primary p-6 text-white">
            <h3 className="font-bold">Getting Started ({doneCount}/{checklist.length})</h3>
            <div className="mt-3 space-y-2">
              {checklist.map((task, i) => (
                <Link key={task.label} href={task.href} className="focus-ring flex items-center gap-2 rounded text-sm text-white/80 hover:text-white">
                  <div className={`flex h-5 w-5 items-center justify-center rounded-full border text-xs ${task.done ? 'border-white bg-white text-primary' : 'border-white/30'}`}>
                    {task.done ? '✓' : i + 1}
                  </div>
                  {task.label}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
