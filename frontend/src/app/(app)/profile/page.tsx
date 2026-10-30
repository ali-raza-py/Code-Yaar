'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { Award, BookOpen, Braces, Flame, GraduationCap, Medal, Sparkles, Star } from 'lucide-react';
import { profileStats, ApiError, type ProfileStatsData } from '@/lib/api';
import { NetworkError } from '@/components/learning/workspace/error-states';

const PROFICIENCY_LABELS = ['', 'Novice', 'Beginner', 'Intermediate', 'Advanced', 'Expert'];
const PROFICIENCY_COLORS = ['', 'bg-muted text-muted-foreground', 'bg-info/10 text-info', 'bg-success/15 text-success', 'bg-primary/10 text-primary', 'bg-warning/15 text-warning'];
const BADGE_ICONS = {
  course: GraduationCap,
  chapter: BookOpen,
  streak: Flame,
  exercise: Braces,
  skill: Sparkles,
  special: Award,
} as const;
const BADGE_TONES = {
  course: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-300',
  chapter: 'bg-sky-500/10 text-sky-700 dark:text-sky-300',
  streak: 'bg-orange-500/10 text-orange-700 dark:text-orange-300',
  exercise: 'bg-violet-500/10 text-violet-700 dark:text-violet-300',
  skill: 'bg-amber-500/10 text-amber-700 dark:text-amber-300',
  special: 'bg-primary/10 text-primary',
} as const;

export default function ProfilePage() {
  const [data, setData] = useState<ProfileStatsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'skills' | 'activity'>('overview');

  const loadProfile = useCallback(async () => {
    try {
      const stats = await profileStats.get();
      setData(stats);
      setError(null);
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        setError('auth');
      } else {
        setError('network');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Deferred via await so the effect never sets state synchronously.
    (async () => { await loadProfile(); })();
  }, [loadProfile]);

  if (error === 'network') return <NetworkError />;
  if (error === 'auth') return (
    <div className="mx-auto max-w-4xl px-4 py-12 text-center">
      <p className="text-muted-foreground">Please sign in to view your profile.</p>
    </div>
  );

  if (loading || !data) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="animate-pulse space-y-6">
          <div className="flex items-center gap-4">
            <div className="h-20 w-20 rounded-full bg-muted" />
            <div className="space-y-2">
              <div className="h-6 w-40 rounded bg-muted" />
              <div className="h-4 w-24 rounded bg-muted" />
            </div>
          </div>
          <div className="grid grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-24 rounded-xl bg-muted" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  const { user, profile, stats, xp_history, skills, certifications, active_enrollments } = data;
  const initials = `${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}`.toUpperCase() || user.username[0].toUpperCase();
  const displayName = `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username;
  const memberSince = new Date(user.date_joined).toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  const accuracy = stats.total_attempts > 0 ? Math.round((stats.correct_attempts / stats.total_attempts) * 100) : 0;

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Profile Header */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center">
        {/* Avatar */}
        {profile.avatar ? (
          <div className="h-20 w-20 shrink-0 overflow-hidden rounded-full bg-muted ring-4 ring-primary/20">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={profile.avatar} alt={displayName} className="h-full w-full object-cover" />
          </div>
        ) : (
          <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-primary/60 to-primary text-2xl font-bold text-white ring-4 ring-primary/20">
            {initials}
          </div>
        )}

        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-foreground">{displayName}</h1>
            {user.username === 'demo' && <span className="rounded-pill border border-info/25 bg-info/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-info">Demo account · sample records</span>}
          </div>
          <p className="text-sm text-muted-foreground">
            @{user.username} · {profile.role === 'mentor' ? 'Mentor' : 'Student'} · Member since {memberSince}
          </p>
          {profile.bio && <p className="mt-1 text-sm text-muted-foreground">{profile.bio}</p>}
        </div>

        {/* Level + XP Badge */}
        <div className="flex items-center gap-3">
          <div className="text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-lg font-bold text-primary">
              {profile.level}
            </div>
            <p className="mt-1 text-xs text-muted-foreground">Level</p>
          </div>
          <div className="text-center">
            <p className="text-lg font-bold text-foreground">{profile.xp_points.toLocaleString()}</p>
            <p className="text-xs text-muted-foreground">Total XP</p>
          </div>
          <div className="text-center">
            <div className="flex items-center gap-1">
              <svg className="h-4 w-4 text-warning" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.362 5.214A8.252 8.252 0 0112 21 8.25 8.25 0 016.038 7.048 8.287 8.287 0 009 9.6a8.983 8.983 0 013.361-6.867 8.21 8.21 0 003 2.48z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 18a3.75 3.75 0 00.495-7.467 5.99 5.99 0 00-1.925 3.546 5.974 5.974 0 01-2.133-1A3.75 3.75 0 0012 18z" />
              </svg>
              <span className="text-lg font-bold text-foreground">{profile.streak_days}</span>
            </div>
            <p className="text-xs text-muted-foreground">Day streak</p>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="mb-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatCard label="Courses Active" value={stats.active_enrollments} icon="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
        <StatCard label="Courses Done" value={stats.completed_courses} icon="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.697 50.697 0 017.74-3.342" />
        <StatCard label="Exercises Solved" value={stats.unique_exercises_solved} icon="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        <StatCard label="Accuracy" value={`${accuracy}%`} icon="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
      </div>

      {/* Tabs */}
      <div className="mb-6 flex gap-1 border-b border-border">
        {(['overview', 'skills', 'activity'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setActiveTab(t)}
            className={`px-4 py-2 text-sm font-medium capitalize transition-colors border-b-2 -mb-px ${
              activeTab === t
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Achievement badges */}
          <section>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-base font-semibold text-foreground">Achievement badges</h2>
              <div className="flex items-center gap-3">
                <span className="text-xs text-muted-foreground">{stats.achievements_earned} / {stats.total_achievements} earned</span>
                <Link href="/achievements" className="focus-ring rounded text-xs font-semibold text-primary hover:underline">View My Achievements</Link>
                <Link href="/certificates" className="focus-ring rounded text-xs font-semibold text-primary hover:underline">Certificates</Link>
              </div>
            </div>
            <p className="mb-3 text-xs text-muted-foreground">Verified learning milestones earned in your Code Yaar journey.</p>
            {data.achievements.length > 0 ? (
              <div className="grid gap-3 sm:grid-cols-2">
                {data.achievements.map((badge) => {
                  const Icon = BADGE_ICONS[badge.category as keyof typeof BADGE_ICONS] ?? Medal;
                  const tone = BADGE_TONES[badge.category as keyof typeof BADGE_TONES] ?? 'bg-muted text-muted-foreground';
                  return (
                    <article key={badge.id} className={`flex min-w-0 items-start gap-3 rounded-card border p-3 transition-colors ${badge.earned ? 'border-border bg-card' : 'border-border/70 bg-muted/30 opacity-75'}`}>
                      <span className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-lg ${badge.earned ? tone : 'bg-muted text-muted-foreground'}`}>
                        <Icon className="h-5 w-5" aria-hidden="true" />
                      </span>
                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center justify-between gap-x-2 gap-y-1">
                          <h3 className="text-sm font-semibold text-foreground">{badge.title}</h3>
                          <span className={`text-[10px] font-semibold uppercase tracking-wide ${badge.earned ? 'text-success' : 'text-muted-foreground'}`}>{badge.earned ? 'Earned' : 'Locked'}</span>
                        </div>
                        <p className="mt-1 text-xs leading-5 text-muted-foreground">{badge.description}</p>
                        <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[10px] text-muted-foreground">
                          <span className="capitalize">{badge.category}</span>
                          {badge.xp_bonus > 0 && <span className="inline-flex items-center gap-1"><Star className="h-3 w-3 text-warning" /> {badge.xp_bonus} XP</span>}
                          {badge.earned_at && <time dateTime={badge.earned_at}>Earned {new Date(badge.earned_at).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}</time>}
                        </div>
                        {badge.earned && (
                          <Link href="/achievements" className="focus-ring mt-2 inline-block text-[11px] font-semibold text-primary hover:underline">
                            View badge &amp; share →
                          </Link>
                        )}
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No badges are available yet.</p>
            )}
          </section>

          {/* Active Courses */}
          <section>
            <h2 className="text-base font-semibold text-foreground mb-3">Active Courses</h2>
            {active_enrollments.length > 0 ? (
              <div className="space-y-2">
                {active_enrollments.map((e) => (
                  <Link
                    key={e.id}
                    href={`/learn/${e.course_slug}`}
                    className="flex items-center gap-4 rounded-lg border border-border bg-card p-4 transition-colors hover:border-primary/30 hover:bg-primary/5"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-foreground truncate">{e.course_title}</p>
                      <p className="text-xs text-muted-foreground">{e.track_title}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-24">
                        <div className="h-1.5 w-full rounded-full bg-muted">
                          <div
                            className="h-1.5 rounded-full bg-primary transition-all"
                            style={{ width: `${e.progress_percentage}%` }}
                          />
                        </div>
                        <p className="mt-0.5 text-right text-[10px] text-muted-foreground">{e.progress_percentage}%</p>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                No active courses.{' '}
                <Link href="/learn" className="focus-ring rounded text-primary hover:underline">Browse courses</Link>
              </p>
            )}
          </section>

          {/* Certifications */}
          {certifications.length > 0 && (
            <section>
              <h2 className="text-base font-semibold text-foreground mb-3">Certifications</h2>
              <div className="space-y-2">
                {certifications.map((c) => (
                  <div key={c.id} className="flex items-center gap-3 rounded-lg border border-success/30 bg-success/10 p-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-success text-white">
                      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.697 50.697 0 017.74-3.342" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-foreground">{c.title}</p>
                      <p className="text-xs text-muted-foreground">{c.track_title} · ID: {c.credential_id}</p>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      )}

      {activeTab === 'skills' && (
        <div className="space-y-4">
          {skills.length > 0 ? (
            skills.map((s) => (
              <div key={s.id} className="rounded-lg border border-border bg-card p-4">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <p className="text-sm font-semibold text-foreground">{s.name}</p>
                    <p className="text-xs text-muted-foreground">{s.category}</p>
                  </div>
                  <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${PROFICIENCY_COLORS[s.proficiency]}`}>
                    {PROFICIENCY_LABELS[s.proficiency]}
                  </span>
                </div>
                <div className="h-2 w-full rounded-full bg-muted">
                  <div
                    className="h-2 rounded-full bg-primary transition-all"
                    style={{ width: `${(s.proficiency / 5) * 100}%` }}
                  />
                </div>
              </div>
            ))
          ) : (
            <div className="rounded-lg border border-border bg-card p-8 text-center">
              <svg className="mx-auto h-10 w-10 text-muted-foreground/50" fill="none" viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
              </svg>
              <h3 className="mt-3 text-sm font-semibold text-foreground">No skills tracked yet</h3>
              <p className="mt-1 text-xs text-muted-foreground">Complete courses and challenges to build your skill profile.</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'activity' && (
        <div className="space-y-4">
          {/* XP Breakdown */}
          <section>
            <h2 className="text-base font-semibold text-foreground mb-3">XP Breakdown</h2>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              {Object.entries(data.xp_breakdown).map(([action, amount]) => (
                <div key={action} className="rounded-lg border border-border bg-card p-3 text-center">
                  <p className="text-lg font-bold text-foreground">{(amount as number).toLocaleString()}</p>
                  <p className="text-xs text-muted-foreground capitalize">{action.replace(/_/g, ' ')}</p>
                </div>
              ))}
              {Object.keys(data.xp_breakdown).length === 0 && (
                <p className="col-span-3 text-sm text-muted-foreground text-center py-4">No XP earned yet.</p>
              )}
            </div>
          </section>

          {/* Recent Activity */}
          <section>
            <h2 className="text-base font-semibold text-foreground mb-3">Recent Activity</h2>
            {xp_history.length > 0 ? (
              <div className="space-y-1">
                {xp_history.map((entry) => (
                  <div key={entry.id} className="flex items-center gap-3 rounded-lg px-3 py-2 hover:bg-muted/60">
                    <div className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
                      entry.amount > 0 ? 'bg-success/15 text-success' : 'bg-danger/15 text-danger'
                    }`}>
                      {entry.amount > 0 ? '+' : ''}{entry.amount}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-foreground truncate">{entry.description || entry.action.replace(/_/g, ' ')}</p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(entry.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground text-center py-4">No activity yet. Start learning to see your XP history!</p>
            )}
          </section>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, icon }: { label: string; value: number | string; icon: string }) {
  return (
    <div className="rounded-card border border-border bg-card p-4 text-center">
      <svg className="mx-auto h-5 w-5 text-primary" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d={icon} />
      </svg>
      <p className="mt-2 text-2xl font-bold text-foreground">{value}</p>
      <p className="mt-0.5 text-xs text-muted-foreground">{label}</p>
    </div>
  );
}
