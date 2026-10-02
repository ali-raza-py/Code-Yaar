'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { profileStats, ApiError, type ProfileStatsData } from '@/lib/api';
import { NetworkError } from '@/components/learning/workspace/error-states';

const PROFICIENCY_LABELS = ['', 'Novice', 'Beginner', 'Intermediate', 'Advanced', 'Expert'];
const PROFICIENCY_COLORS = ['', 'bg-gray-100 text-gray-600', 'bg-blue-100 text-blue-700', 'bg-green-100 text-green-700', 'bg-purple-100 text-purple-700', 'bg-yellow-100 text-yellow-700'];

export default function ProfilePage() {
  const [data, setData] = useState<ProfileStatsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'skills' | 'activity'>('overview');

  useEffect(() => {
    loadProfile();
  }, []);

  async function loadProfile() {
    try {
      setLoading(true);
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
  }

  if (error === 'network') return <NetworkError />;
  if (error === 'auth') return (
    <div className="mx-auto max-w-4xl px-4 py-12 text-center">
      <p className="text-gray-500">Please sign in to view your profile.</p>
    </div>
  );

  if (loading || !data) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="animate-pulse space-y-6">
          <div className="flex items-center gap-4">
            <div className="h-20 w-20 rounded-full bg-gray-200" />
            <div className="space-y-2">
              <div className="h-6 w-40 rounded bg-gray-200" />
              <div className="h-4 w-24 rounded bg-gray-200" />
            </div>
          </div>
          <div className="grid grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-24 rounded-xl bg-gray-200" />
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
          <div className="h-20 w-20 shrink-0 overflow-hidden rounded-full bg-gray-100 ring-4 ring-purple-100">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={profile.avatar} alt={displayName} className="h-full w-full object-cover" />
          </div>
        ) : (
          <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-purple-400 to-purple-600 text-2xl font-bold text-white ring-4 ring-purple-100">
            {initials}
          </div>
        )}

        <div className="flex-1">
          <h1 className="text-2xl font-bold tracking-tight text-gray-900">{displayName}</h1>
          <p className="text-sm text-gray-500">
            @{user.username} · {profile.role === 'mentor' ? 'Mentor' : 'Student'} · Member since {memberSince}
          </p>
          {profile.bio && <p className="mt-1 text-sm text-gray-600">{profile.bio}</p>}
        </div>

        {/* Level + XP Badge */}
        <div className="flex items-center gap-3">
          <div className="text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-purple-100 text-lg font-bold text-purple-700">
              {profile.level}
            </div>
            <p className="mt-1 text-xs text-gray-500">Level</p>
          </div>
          <div className="text-center">
            <p className="text-lg font-bold text-gray-900">{profile.xp_points.toLocaleString()}</p>
            <p className="text-xs text-gray-500">Total XP</p>
          </div>
          <div className="text-center">
            <div className="flex items-center gap-1">
              <svg className="h-4 w-4 text-orange-500" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.362 5.214A8.252 8.252 0 0112 21 8.25 8.25 0 016.038 7.048 8.287 8.287 0 009 9.6a8.983 8.983 0 013.361-6.867 8.21 8.21 0 003 2.48z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 18a3.75 3.75 0 00.495-7.467 5.99 5.99 0 00-1.925 3.546 5.974 5.974 0 01-2.133-1A3.75 3.75 0 0012 18z" />
              </svg>
              <span className="text-lg font-bold text-gray-900">{profile.streak_days}</span>
            </div>
            <p className="text-xs text-gray-500">Day streak</p>
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
      <div className="mb-6 flex gap-1 border-b border-gray-200">
        {(['overview', 'skills', 'activity'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setActiveTab(t)}
            className={`px-4 py-2 text-sm font-medium capitalize transition-colors border-b-2 -mb-px ${
              activeTab === t
                ? 'border-purple-600 text-purple-700'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Achievements */}
          <section>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-base font-semibold text-gray-900">Achievements</h2>
              <span className="text-xs text-gray-500">{stats.achievements_earned} / {stats.total_achievements} earned</span>
            </div>
            {stats.achievements_earned > 0 ? (
              <div className="flex flex-wrap gap-2">
                {Array.from({ length: stats.achievements_earned }).map((_, i) => (
                  <div key={i} className="flex h-10 w-10 items-center justify-center rounded-full bg-yellow-100 text-yellow-700" title="Achievement earned">
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 01-.982-3.172M9.497 14.25a7.454 7.454 0 00.981-3.172M5.25 4.236c-.982.143-1.954.317-2.916.52A6.003 6.003 0 007.73 9.728M5.25 4.236V4.5c0 2.108.966 3.99 2.48 5.228M5.25 4.236V2.721C7.456 2.41 9.71 2.25 12 2.25c2.291 0 4.545.16 6.75.47v1.516M18.75 4.236c.982.143 1.954.317 2.916.52A6.003 6.003 0 0116.27 9.728M18.75 4.236V4.5c0 2.108-.966 3.99-2.48 5.228" />
                    </svg>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No achievements earned yet. Complete courses and challenges to unlock badges!</p>
            )}
          </section>

          {/* Active Courses */}
          <section>
            <h2 className="text-base font-semibold text-gray-900 mb-3">Active Courses</h2>
            {active_enrollments.length > 0 ? (
              <div className="space-y-2">
                {active_enrollments.map((e) => (
                  <Link
                    key={e.id}
                    href={`/learn/${e.course_slug}`}
                    className="flex items-center gap-4 rounded-lg border border-gray-200 bg-white p-4 transition-colors hover:border-purple-300 hover:bg-purple-50/30"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-gray-900 truncate">{e.course_title}</p>
                      <p className="text-xs text-gray-500">{e.track_title}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-24">
                        <div className="h-1.5 w-full rounded-full bg-gray-200">
                          <div
                            className="h-1.5 rounded-full bg-purple-600 transition-all"
                            style={{ width: `${e.progress_percentage}%` }}
                          />
                        </div>
                        <p className="mt-0.5 text-right text-[10px] text-gray-500">{e.progress_percentage}%</p>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">
                No active courses.{' '}
                <Link href="/learn" className="text-purple-600 hover:underline">Browse courses</Link>
              </p>
            )}
          </section>

          {/* Certifications */}
          {certifications.length > 0 && (
            <section>
              <h2 className="text-base font-semibold text-gray-900 mb-3">Certifications</h2>
              <div className="space-y-2">
                {certifications.map((c) => (
                  <div key={c.id} className="flex items-center gap-3 rounded-lg border border-green-200 bg-green-50 p-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-green-500 text-white">
                      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.697 50.697 0 017.74-3.342" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-green-900">{c.title}</p>
                      <p className="text-xs text-green-700">{c.track_title} · ID: {c.credential_id}</p>
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
              <div key={s.id} className="rounded-lg border border-gray-200 bg-white p-4">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <p className="text-sm font-semibold text-gray-900">{s.name}</p>
                    <p className="text-xs text-gray-500">{s.category}</p>
                  </div>
                  <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${PROFICIENCY_COLORS[s.proficiency]}`}>
                    {PROFICIENCY_LABELS[s.proficiency]}
                  </span>
                </div>
                <div className="h-2 w-full rounded-full bg-gray-200">
                  <div
                    className="h-2 rounded-full bg-purple-600 transition-all"
                    style={{ width: `${(s.proficiency / 5) * 100}%` }}
                  />
                </div>
              </div>
            ))
          ) : (
            <div className="rounded-lg border border-gray-200 bg-white p-8 text-center">
              <svg className="mx-auto h-10 w-10 text-gray-300" fill="none" viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
              </svg>
              <h3 className="mt-3 text-sm font-semibold text-gray-900">No skills tracked yet</h3>
              <p className="mt-1 text-xs text-gray-500">Complete courses and challenges to build your skill profile.</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'activity' && (
        <div className="space-y-4">
          {/* XP Breakdown */}
          <section>
            <h2 className="text-base font-semibold text-gray-900 mb-3">XP Breakdown</h2>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              {Object.entries(data.xp_breakdown).map(([action, amount]) => (
                <div key={action} className="rounded-lg border border-gray-200 bg-white p-3 text-center">
                  <p className="text-lg font-bold text-gray-900">{(amount as number).toLocaleString()}</p>
                  <p className="text-xs text-gray-500 capitalize">{action.replace(/_/g, ' ')}</p>
                </div>
              ))}
              {Object.keys(data.xp_breakdown).length === 0 && (
                <p className="col-span-3 text-sm text-gray-500 text-center py-4">No XP earned yet.</p>
              )}
            </div>
          </section>

          {/* Recent Activity */}
          <section>
            <h2 className="text-base font-semibold text-gray-900 mb-3">Recent Activity</h2>
            {xp_history.length > 0 ? (
              <div className="space-y-1">
                {xp_history.map((entry) => (
                  <div key={entry.id} className="flex items-center gap-3 rounded-lg px-3 py-2 hover:bg-gray-50">
                    <div className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
                      entry.amount > 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                    }`}>
                      {entry.amount > 0 ? '+' : ''}{entry.amount}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-900 truncate">{entry.description || entry.action.replace(/_/g, ' ')}</p>
                      <p className="text-xs text-gray-500">
                        {new Date(entry.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500 text-center py-4">No activity yet. Start learning to see your XP history!</p>
            )}
          </section>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, icon }: { label: string; value: number | string; icon: string }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 text-center">
      <svg className="mx-auto h-5 w-5 text-purple-500" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d={icon} />
      </svg>
      <p className="mt-2 text-2xl font-bold text-gray-900">{value}</p>
      <p className="mt-0.5 text-xs text-gray-500">{label}</p>
    </div>
  );
}
