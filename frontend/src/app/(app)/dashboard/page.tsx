"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
  ArrowRight,
  Award,
  BookOpen,
  Check,
  Dumbbell,
  Flame,
  FolderGit2,
  Megaphone,
  Trophy,
  Zap,
} from "lucide-react";
import { announcements as announcementsApi, leaderboard as leaderboardApi, profileStats } from "@/lib/api";
import type { LeaderboardEntry, ProfileStatsData, PublicAnnouncement } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { AchievementIcon } from "@/components/achievements/achievement-icon";

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
  const [latestAnnouncements, setLatestAnnouncements] = useState<PublicAnnouncement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const load = useCallback(async () => {
    if (!user) return;
    try {
      const [statsData, board, announcementList] = await Promise.all([
        profileStats.get(),
        leaderboardApi.list({ limit: 10 }),
        announcementsApi.list().catch(() => [] as PublicAnnouncement[]),
      ]);
      setStats(statsData);
      setTopLearners(board.entries);
      setLatestAnnouncements(announcementList.slice(0, 4));
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
      <div className="mx-auto max-w-6xl animate-pulse px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-6 h-8 w-48 rounded bg-muted" />
        <div className="grid gap-6 xl:grid-cols-[minmax(0,1.7fr)_minmax(18rem,0.9fr)]">
          <div className="space-y-5">
            <div className="h-40 rounded-xl bg-muted" />
            <div className="h-32 rounded-xl bg-muted" />
          </div>
          <div className="h-64 rounded-xl bg-muted" />
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
  const courseProgress = Math.max(0, Math.min(100, enrollment?.progress_percentage ?? 0));
  const checklistProgress = Math.round((doneCount / checklist.length) * 100);

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <header className="mb-8 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-primary">
            Your learning dashboard
          </p>
          <h1 className="mt-2 break-words font-display text-3xl font-semibold leading-tight tracking-tight text-foreground sm:text-4xl">
            Welcome back, {displayName}
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Pick up where you left off and see how far you&apos;ve come.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <span className="inline-flex items-center rounded-full border border-border bg-card px-3 py-1.5 text-sm font-medium text-foreground">
            Level {profile?.level ?? 1}
          </span>
          <Link
            href="/progress?tab=overview"
            className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg bg-cta px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-cta-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          >
            View progress
            <ArrowRight aria-hidden="true" className="h-4 w-4" />
          </Link>
        </div>
      </header>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.7fr)_minmax(18rem,0.9fr)] xl:gap-8">
        <div className="min-w-0 space-y-5">
          {/* Continue Learning card */}
          <section aria-labelledby="continue-learning-title" className="rounded-xl bg-hero-navy p-6 text-white sm:p-8">
            <div className="grid gap-6 md:grid-cols-[minmax(0,1fr)_auto] md:items-center">
              <div className="min-w-0">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-white/65">
                  {enrollment ? 'Continue where you left off' : 'Your learning'}
                </p>
                <h2 id="continue-learning-title" className="mt-2 break-words font-display text-2xl font-semibold leading-tight sm:text-3xl">
                  {enrollment ? enrollment.course_title : 'No active courses yet'}
                </h2>
                <p className="mt-2 text-sm leading-6 text-white/70">
                  {enrollment
                    ? `Part of the ${enrollment.track_title} track`
                    : 'Choose a course to start your structured learning path.'}
                </p>
                {enrollment && (
                  <div className="mt-5 max-w-xl">
                    <div className="mb-2 flex items-center justify-between gap-4 text-xs">
                      <span className="text-white/75">Course progress</span>
                      <span className="font-semibold tabular-nums text-white">{courseProgress}%</span>
                    </div>
                    <div
                      aria-label={`${courseProgress}% complete`}
                      aria-valuemax={100}
                      aria-valuemin={0}
                      aria-valuenow={courseProgress}
                      className="h-2 overflow-hidden rounded-full bg-white/15"
                      role="progressbar"
                    >
                      <div
                        className="h-full rounded-full bg-mint transition-[width] duration-500"
                        style={{ width: `${courseProgress}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
              <Link
                href={enrollment ? `/learn/${enrollment.course_slug}` : '/learn'}
                className="inline-flex min-h-11 items-center justify-center gap-2 whitespace-nowrap rounded-lg bg-cta px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-cta-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-hero-navy"
              >
                {enrollment ? 'Continue learning' : 'Browse courses'}
                <ArrowRight aria-hidden="true" className="h-4 w-4" />
              </Link>
            </div>
          </section>

          {/* Practice section (honest, no invented quotas) */}
          <section aria-labelledby="practice-title">
            <h2 id="practice-title" className="mb-3 flex items-center gap-2 text-lg font-semibold text-foreground">
              <Dumbbell aria-hidden="true" className="h-5 w-5 text-primary" />
              Practice
            </h2>
            <div className="card-hairline p-5 sm:p-6">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="min-w-0">
                  <h3 className="font-semibold text-foreground">
                    {stats ? `${stats.stats.unique_exercises_solved} exercises solved · ${stats.stats.total_attempts} attempts` : 'Apply what you learn'}
                  </h3>
                  <p className="mt-1 max-w-2xl text-sm leading-6 text-muted-foreground">
                    Exercises and challenges are graded server-side. Code evaluation via the sandbox
                    service is still being rolled out.
                  </p>
                </div>
                <div className="flex shrink-0 flex-wrap items-center gap-x-4 gap-y-2">
                  <Link href="/learn" className="inline-flex min-h-10 items-center rounded-lg border border-border bg-background px-3 py-2 text-sm font-medium text-foreground transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                    Course exercises
                  </Link>
                  <Link href="/challenges" className="inline-flex min-h-10 items-center gap-1 text-sm font-medium text-primary hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                    View challenges <ArrowRight aria-hidden="true" className="h-3.5 w-3.5" />
                  </Link>
                </div>
              </div>
            </div>
          </section>

          {/* Recent activity — real XP ledger */}
          <section aria-labelledby="recent-activity-title" className="card-hairline p-5 sm:p-6">
            <h2 id="recent-activity-title" className="font-semibold text-foreground">Recent activity</h2>
            {activity.length === 0 ? (
              <p className="mt-3 text-sm leading-6 text-muted-foreground">
                Nothing here yet. Complete a lesson or exercise and your XP history will appear.
              </p>
            ) : (
              <ul className="mt-3 divide-y divide-border">
                {activity.slice(0, 6).map((item) => (
                  <li key={item.id} className="flex flex-col gap-1.5 py-3 text-sm first:pt-0 last:pb-0 sm:flex-row sm:items-center sm:justify-between sm:gap-4">
                    <span className="min-w-0 text-foreground">
                      {item.description || item.action.replace(/_/g, ' ')}
                    </span>
                    <span className="flex shrink-0 items-center gap-3 text-xs text-muted-foreground">
                      <span className={`font-semibold tabular-nums ${item.amount >= 0 ? 'text-cta' : 'text-danger'}`}>
                        {item.amount >= 0 ? `+${item.amount}` : item.amount} XP
                      </span>
                      <time dateTime={item.created_at}>{timeAgo(item.created_at)}</time>
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </section>

          {/* Quick access grid */}
          <nav aria-label="Explore learning" className="grid gap-4 sm:grid-cols-2">
            <Link href="/learn" className="group card-hairline p-5 transition-colors hover:border-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
              <span className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <BookOpen aria-hidden="true" className="h-5 w-5" />
              </span>
              <h3 className="font-semibold text-foreground transition-colors group-hover:text-primary">Courses</h3>
              <p className="mt-1 text-sm leading-6 text-muted-foreground">
                Structured lessons with hands-on exercises.
              </p>
              <div className="mt-4 inline-flex items-center text-sm font-medium text-primary">
                Browse courses <ArrowRight aria-hidden="true" className="ml-1 h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
              </div>
            </Link>
            <Link href="/projects" className="group card-hairline p-5 transition-colors hover:border-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
              <span className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <FolderGit2 aria-hidden="true" className="h-5 w-5" />
              </span>
              <h3 className="font-semibold text-foreground transition-colors group-hover:text-primary">Real World Projects</h3>
              <p className="mt-1 text-sm leading-6 text-muted-foreground">
                Apply your knowledge to practical scenarios.
              </p>
              <div className="mt-4 inline-flex items-center text-sm font-medium text-primary">
                Browse projects <ArrowRight aria-hidden="true" className="ml-1 h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
              </div>
            </Link>
          </nav>

          {/* Achievements snapshot — earned badges + the next one in reach */}
          {stats && (
            <section aria-labelledby="achievements-title" className="card-hairline p-5 sm:p-6">
              <div className="flex items-center justify-between">
                <h2 id="achievements-title" className="flex items-center gap-2 font-semibold text-foreground">
                  <Award aria-hidden="true" className="h-5 w-5 text-primary" />
                  Achievements
                </h2>
                <Link href="/progress?tab=achievements" className="inline-flex min-h-10 items-center text-sm font-medium text-primary hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                  View all
                </Link>
              </div>
              <p className="mt-1 text-xs text-muted-foreground">
                {stats.stats.achievements_earned} of {stats.stats.total_achievements} badges earned
              </p>
              {(() => {
                const earned = stats.achievements.filter((a) => a.earned).slice(0, 6);
                if (earned.length === 0) {
                  return (
                    <p className="mt-4 text-sm text-muted-foreground">
                      No badges yet — complete lessons, exercises and courses to earn your first one.
                    </p>
                  );
                }
                return (
                  <div className="mt-4 grid grid-cols-3 gap-3 sm:grid-cols-6">
                    {earned.map((b) => (
                      <div key={b.id} className="flex flex-col items-center text-center">
                        <span className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
                          <AchievementIcon name={b.icon} className="h-6 w-6" />
                        </span>
                        <span className="mt-1 line-clamp-2 text-[10px] leading-tight text-muted-foreground">{b.title}</span>
                      </div>
                    ))}
                  </div>
                );
              })()}
              {stats.next_badge && (
                <div className="mt-4 rounded-lg border border-border bg-background p-3">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-xs font-semibold text-foreground">Next badge · {stats.next_badge.title}</p>
                    <span className="shrink-0 text-xs tabular-nums text-muted-foreground">
                      {stats.next_badge.progress.current}/{stats.next_badge.progress.target}
                    </span>
                  </div>
                  <div
                    aria-label={`${stats.next_badge.title} progress`}
                    aria-valuemax={Math.max(1, stats.next_badge.progress.target)}
                    aria-valuemin={0}
                    aria-valuenow={Math.min(
                      stats.next_badge.progress.current,
                      Math.max(1, stats.next_badge.progress.target),
                    )}
                    className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-muted"
                    role="progressbar"
                  >
                    <div className="h-full rounded-pill bg-primary" style={{ width: `${stats.next_badge.progress.target > 0 ? Math.min(100, Math.round((stats.next_badge.progress.current / stats.next_badge.progress.target) * 100)) : 0}%` }} />
                  </div>
                </div>
              )}
            </section>
          )}
        </div>

        <aside aria-label="Your learning at a glance" className="min-w-0 space-y-5">
          {/* Streak + XP from the server-side profile */}
          <section aria-labelledby="learner-stats-title" className="card-hairline p-5 sm:p-6">
            <div className="flex min-w-0 items-center gap-3">
              <span aria-hidden="true" className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-lg font-semibold text-primary">
                {(displayName || '?').charAt(0).toUpperCase()}
              </span>
              <div className="min-w-0">
                <h2 id="learner-stats-title" className="truncate font-semibold text-foreground">{displayName}</h2>
                <p className="mt-0.5 text-sm text-muted-foreground">Level {profile?.level ?? 1} learner</p>
              </div>
            </div>
            <div className="mt-5 grid grid-cols-2 divide-x divide-border border-t border-border pt-4">
              <div className="pr-4">
                <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <Flame aria-hidden="true" className="h-4 w-4 text-amber" />
                  Daily streak
                </div>
                <p className="mt-1 text-lg font-semibold tabular-nums text-foreground">
                  {profile?.streak_days ?? 0} {(profile?.streak_days ?? 0) === 1 ? 'day' : 'days'}
                </p>
              </div>
              <div className="pl-4">
                <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <Zap aria-hidden="true" className="h-4 w-4 text-primary" />
                  Total XP
                </div>
                <p className="mt-1 text-lg font-semibold tabular-nums text-foreground">
                  {(profile?.xp_points ?? 0).toLocaleString()} XP
                </p>
              </div>
            </div>
          </section>

          {/* Leaderboard snapshot */}
          <section aria-labelledby="leaderboard-title" className="card-hairline p-5 sm:p-6">
            <div className="flex items-center justify-between gap-3">
              <h2 id="leaderboard-title" className="flex items-center gap-2 font-semibold text-foreground">
                <Trophy aria-hidden="true" className="h-5 w-5 text-amber" />
                Leaderboard
              </h2>
              <Link href="/leaderboard" className="inline-flex min-h-10 shrink-0 items-center text-sm font-medium text-primary hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                View all
              </Link>
            </div>
            {topLearners.length === 0 ? (
              <p className="mt-3 text-sm leading-6 text-muted-foreground">
                The leaderboard is empty. Earn XP from lessons and exercises to appear here.
              </p>
            ) : (
              <>
                <ol aria-label="Top learners" className="mt-3 space-y-1">
                  {topLearners.slice(0, 5).map((entry) => {
                    const isCurrentLearner = entry.user_id === stats?.user.id;
                    return (
                      <li
                        key={entry.rank}
                        className={`grid grid-cols-[1.75rem_minmax(0,1fr)_auto] items-center gap-2 rounded-lg px-2 py-2 text-sm ${
                          isCurrentLearner ? 'bg-primary/5 font-semibold' : ''
                        }`}
                      >
                        <span className={`text-center tabular-nums ${
                          entry.rank === 1 ? 'font-semibold text-amber' : 'text-muted-foreground'
                        }`}>
                          {entry.rank}
                        </span>
                        <span className="min-w-0 truncate text-foreground" title={entry.username}>
                          {entry.username}
                        </span>
                        <span className="text-right text-xs tabular-nums text-muted-foreground sm:text-sm">
                          {entry.xp_points.toLocaleString()} XP
                        </span>
                      </li>
                    );
                  })}
                </ol>
                <p className="mt-3 text-xs text-muted-foreground">
                  {userRank !== null ? `You're ranked #${userRank} overall.` : "You're not in the top 10 yet."}
                </p>
              </>
            )}
          </section>

          {/* Getting Started — derived from real records */}
          <section aria-labelledby="getting-started-title" className="card-hairline p-5 sm:p-6">
            <div className="flex items-center justify-between gap-3">
              <div>
                <h2 id="getting-started-title" className="font-semibold text-foreground">Getting started</h2>
                <p className="mt-1 text-xs text-muted-foreground">A few steps to make this space yours.</p>
              </div>
              <span className="shrink-0 rounded-full bg-muted px-2.5 py-1 text-xs font-semibold tabular-nums text-foreground">
                {doneCount}/{checklist.length}
              </span>
            </div>
            <div
              aria-label={`${checklistProgress}% complete`}
              aria-valuemax={100}
              aria-valuemin={0}
              aria-valuenow={checklistProgress}
              className="mt-4 h-1.5 overflow-hidden rounded-full bg-muted"
              role="progressbar"
            >
              <div className="h-full rounded-full bg-primary transition-[width] duration-300" style={{ width: `${checklistProgress}%` }} />
            </div>
            <ul className="mt-3 divide-y divide-border">
              {checklist.map((task, i) => (
                <li key={task.label}>
                  <Link
                    href={task.href}
                    className="group flex min-h-11 items-center gap-3 rounded-md py-2 text-sm text-foreground transition-colors hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  >
                    <span className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border text-[11px] ${
                      task.done
                        ? 'border-success bg-success text-white'
                        : 'border-border bg-background text-muted-foreground'
                    }`}>
                      {task.done ? <Check aria-hidden="true" className="h-3 w-3" /> : i + 1}
                    </span>
                    <span className="min-w-0 flex-1">{task.label}</span>
                    <ArrowRight aria-hidden="true" className="h-3.5 w-3.5 shrink-0 text-muted-foreground opacity-0 transition-all group-hover:translate-x-0.5 group-hover:opacity-100" />
                  </Link>
                </li>
              ))}
            </ul>
          </section>

          {/* Latest announcements — live from the publishing system */}
          {latestAnnouncements.length > 0 && (
            <section aria-labelledby="announcements-title" className="card-hairline p-5 sm:p-6">
              <h2 id="announcements-title" className="flex items-center gap-2 font-semibold text-foreground">
                <Megaphone aria-hidden="true" className="h-5 w-5 text-primary" />
                Announcements
              </h2>
              <ul className="mt-3 space-y-2">
                {latestAnnouncements.map((item) => (
                  <li key={item.id}>
                    <Link
                      href={item.slug ? `/announcements/${item.slug}` : "/announcements"}
                      className="group block rounded-lg border border-border p-3 transition-colors hover:border-primary hover:bg-muted/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                      <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
                        <span className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                          {item.category_label}
                        </span>
                        {item.priority !== "normal" && (
                          <span className={`rounded px-1.5 py-0.5 text-[10px] font-bold uppercase ${
                            item.priority === "urgent"
                              ? "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300"
                              : "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300"
                          }`}>
                            {item.priority_label}
                          </span>
                        )}
                      </div>
                      <p className="mt-1 text-sm font-semibold text-foreground transition-colors group-hover:text-primary">{item.title}</p>
                      {item.short_description && (
                        <p className="mt-1 line-clamp-2 text-xs leading-5 text-muted-foreground">{item.short_description}</p>
                      )}
                    </Link>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </aside>
      </div>
    </div>
  );
}
