'use client';

import { useState, useEffect } from 'react';
import { leaderboard as leaderboardApi, auth, ApiError, type LeaderboardEntry } from '@/lib/api';
import { NetworkError, ServerError } from '@/components/learning/workspace/error-states';

type Period = 'all' | 'week' | 'month';

export default function LeaderboardPage() {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [period, setPeriod] = useState<Period>('all');
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);

  useEffect(() => {
    loadLeaderboard();
    loadCurrentUser();
  }, []);

  async function loadCurrentUser() {
    try {
      const profile = await auth.getProfile() as { user: { id: number } };
      setCurrentUserId(profile.user.id);
    } catch {
      // Not authenticated
    }
  }

  async function loadLeaderboard() {
    try {
      setLoading(true);
      const data = await leaderboardApi.list({ limit: 50 });
      setEntries(data.entries);
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

  const getRankBadge = (rank: number) => {
    if (rank === 1) return { bg: 'bg-yellow-100', text: 'text-yellow-700', icon: '🥇' };
    if (rank === 2) return { bg: 'bg-gray-100', text: 'text-gray-600', icon: '' };
    if (rank === 3) return { bg: 'bg-amber-100', text: 'text-amber-700', icon: '🥉' };
    return { bg: 'bg-white', text: 'text-gray-500', icon: String(rank) };
  };

  if (error === 'network') return <NetworkError />;

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8">
        <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-purple-200 bg-purple-50 px-3 py-1 text-xs font-medium text-purple-700">
          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 01-.982-3.172M9.497 14.25a7.454 7.454 0 00.981-3.172M5.25 4.236c-.982.143-1.954.317-2.916.52A6.003 6.003 0 007.73 9.728M5.25 4.236V4.5c0 2.108.966 3.99 2.48 5.228M5.25 4.236V2.721C7.456 2.41 9.71 2.25 12 2.25c2.291 0 4.545.16 6.75.47v1.516M18.75 4.236c.982.143 1.954.317 2.916.52A6.003 6.003 0 0116.27 9.728M18.75 4.236V4.5c0 2.108-.966 3.99-2.48 5.228m0 0a6.023 6.023 0 01-2.77.852m0 0l-.5.075a7.48 7.48 0 01-1 .067 7.48 7.48 0 01-1-.067l-.5-.075m3 0a6.022 6.022 0 01-2.77-.852" />
          </svg>
          LEADERBOARD
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">
          Community Rankings
        </h1>
        <p className="mt-2 text-gray-600">
          See who&apos;s leading the Code-Yaar community. Rankings are based on total XP earned.
        </p>
      </div>

      {/* Period Tabs */}
      <div className="mb-6 flex items-center gap-2">
        {(['all', 'week', 'month'] as Period[]).map((p) => (
          <button
            key={p}
            onClick={() => setPeriod(p)}
            className={`rounded-full px-4 py-1.5 text-sm font-medium capitalize transition-colors ${
              period === p
                ? 'bg-gray-900 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {p === 'all' ? 'All Time' : `This ${p}`}
          </button>
        ))}
      </div>

      {/* Leaderboard Table */}
      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className="flex items-center gap-4 rounded-lg border border-gray-200 bg-white p-4 animate-pulse">
              <div className="h-8 w-8 rounded-full bg-gray-200" />
              <div className="h-4 w-24 rounded bg-gray-200" />
              <div className="flex-1" />
              <div className="h-4 w-16 rounded bg-gray-100" />
            </div>
          ))}
        </div>
      ) : entries.length === 0 ? (
        <div className="rounded-lg border border-gray-200 bg-white p-12 text-center">
          <svg className="mx-auto h-10 w-10 text-gray-300" fill="none" viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 01-.982-3.172M9.497 14.25a7.454 7.454 0 00.981-3.172M5.25 4.236c-.982.143-1.954.317-2.916.52A6.003 6.003 0 007.73 9.728M5.25 4.236V4.5c0 2.108.966 3.99 2.48 5.228M5.25 4.236V2.721C7.456 2.41 9.71 2.25 12 2.25c2.291 0 4.545.16 6.75.47v1.516M18.75 4.236c.982.143 1.954.317 2.916.52A6.003 6.003 0 0116.27 9.728M18.75 4.236V4.5c0 2.108-.966 3.99-2.48 5.228m0 0a6.023 6.023 0 01-2.77.852m0 0l-.5.075a7.48 7.48 0 01-1 .067 7.48 7.48 0 01-1-.067l-.5-.075m3 0a6.022 6.022 0 01-2.77-.852" />
          </svg>
          <h2 className="mt-4 text-lg font-semibold text-gray-900">No rankings yet</h2>
          <p className="mt-2 text-sm text-gray-600">
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
                className={`flex items-center gap-4 rounded-lg border p-4 transition-colors ${
                  isCurrentUser
                    ? 'border-purple-300 bg-purple-50'
                    : 'border-gray-200 bg-white hover:bg-gray-50'
                }`}
              >
                {/* Rank */}
                <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-bold ${badge.bg} ${badge.text}`}>
                  {entry.rank <= 3 ? badge.icon : entry.rank}
                </div>

                {/* Avatar */}
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-purple-400 to-purple-600 text-sm font-bold text-white">
                  {entry.username.charAt(0).toUpperCase()}
                </div>

                {/* Username */}
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-semibold truncate ${isCurrentUser ? 'text-purple-900' : 'text-gray-900'}`}>
                    {entry.username}
                    {isCurrentUser && <span className="ml-2 text-xs font-normal text-purple-600">(You)</span>}
                  </p>
                  <p className="text-xs text-gray-500">
                    Level {entry.level} · {entry.streak_days} day streak
                  </p>
                </div>

                {/* Stats */}
                <div className="hidden sm:flex items-center gap-4 text-xs text-gray-500">
                  <span>{entry.courses_completed} courses</span>
                  <span>{entry.challenges_solved} solved</span>
                </div>

                {/* XP */}
                <div className="text-right">
                  <p className="text-sm font-bold text-gray-900">{entry.xp_points.toLocaleString()}</p>
                  <p className="text-xs text-gray-500">XP</p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
